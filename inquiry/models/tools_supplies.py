from odoo import fields, models, api, _
from datetime import timedelta
from collections import defaultdict
from odoo.exceptions import UserError


class InquiryToolsSupplies(models.Model):
    _name = 'inquiry.tools.supplies'
    _description = 'Inquiry Tools And Supplies'

    sequence = fields.Integer(default=10)
    inquiry_id = fields.Many2one('inquiry.inquiry', required=True)
    state = fields.Selection(
        selection=[
            ('draft', "Draft"),
            ('initial', "Initial Contract Review"),
            ('review_one', "Contract Review One"),
            ('final', "Final Contract Review"),
            ('done', "Contract Done"),
            ('regret', "Regret"),
        ], related='inquiry_id.state')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    product_id = fields.Many2one('product.product', string="Product", change_default=True, ondelete='restrict',
                                 index='btree_not_null',
                                 domain="[('detailed_type', '=', 'product'), ('sale_ok', '=', False), ('purchase_ok', '=', True), ('categ_id.is_tool_supply', '=', True)]")
    product_type = fields.Selection(related='product_id.detailed_type')
    product_uom_category_id = fields.Many2one('uom.category', related='product_id.uom_id.category_id',
                                              depends=['product_id'])
    product_uom_id = fields.Many2one('uom.uom', related='product_id.uom_id')
    product_qty = fields.Float(required=True)
    standard_price = fields.Float(digits='Product Price')

    qty_delivered_method = fields.Selection(selection=[('stock_move', 'Stock Moves')])
    route_id = fields.Many2one('stock.route', string='Route', domain=[('sale_selectable', '=', True)],
                               ondelete='restrict', check_company=True)
    move_ids = fields.Many2many('stock.move', string='Stock Moves')
    virtual_available_at_date = fields.Float(compute='_compute_qty_at_date', digits='Product Unit of Measure')
    scheduled_date = fields.Datetime(compute='_compute_qty_at_date')
    forecast_expected_date = fields.Datetime(compute='_compute_qty_at_date')
    free_qty_today = fields.Float(compute='_compute_qty_at_date', digits='Product Unit of Measure')
    qty_available_today = fields.Float(compute='_compute_qty_at_date')
    warehouse_id = fields.Many2one('stock.warehouse', related='inquiry_id.warehouse_id')
    qty_to_deliver = fields.Float(compute='_compute_qty_to_deliver', digits='Product Unit of Measure')
    is_mto = fields.Boolean(compute='_compute_is_mto')
    display_qty_widget = fields.Boolean(compute='_compute_qty_to_deliver')
    customer_lead = fields.Float(
        compute='_compute_customer_lead', store=True, readonly=False, precompute=True,
        inverse='_inverse_customer_lead')

    @api.onchange('product_id')
    def compute_move_ids(self):
        moves = self.env['stock.move'].search([('product_id', '=', self.product_id.id)])
        print(moves)
        self.move_ids = moves

    @api.depends('product_type', 'product_qty', 'state', 'move_ids', 'product_uom_id')
    def _compute_qty_to_deliver(self):
        for line in self:
            line.qty_to_deliver = line.product_qty
            if line.state in ('draft', 'initial', 'review_one', 'final', 'done') and line.product_type in [
                'product'] and line.product_uom_id and line.qty_to_deliver > 0:
                if not line.move_ids:
                    line.display_qty_widget = False
                else:
                    line.display_qty_widget = True
            else:
                line.display_qty_widget = False

    @api.depends('product_id', 'route_id', 'inquiry_id.warehouse_id', 'product_id.route_ids')
    def _compute_is_mto(self):
        self.is_mto = False
        for line in self:
            if not line.display_qty_widget:
                continue
            product = line.product_id
            product_routes = line.route_id or (product.route_ids + product.categ_id.total_route_ids)

            # Check MTO
            mto_route = line.inquiry_id.warehouse_id.mto_pull_id.route_id
            if not mto_route:
                try:
                    mto_route = self.env['stock.warehouse']._find_global_route('stock.route_warehouse0_mto',
                                                                               _('Replenish on Order (MTO)'))
                except UserError:
                    # if route MTO not found in ir_model_data, we treat the product as in MTS
                    pass

            if mto_route and mto_route in product_routes:
                line.is_mto = True
            else:
                line.is_mto = False

    @api.depends('product_id')
    def _compute_customer_lead(self):
        for line in self:
            line.customer_lead = line.product_id.sale_delay

    @api.depends(
        'product_id', 'customer_lead', 'product_qty', 'product_uom_id', 'inquiry_id.date',
        'move_ids', 'move_ids.forecast_expected_date', 'move_ids.forecast_availability',
        'warehouse_id')
    def _compute_qty_at_date(self):
        treated = self.browse()
        for line in self.filtered(lambda l: l.state in ('draft', 'initial', 'review_one', 'final', 'done')):
            if not line.display_qty_widget:
                continue
            moves = line.move_ids.filtered(lambda m: m.product_id == line.product_id)
            line.forecast_expected_date = max(moves.filtered("forecast_expected_date").mapped("forecast_expected_date"),
                                              default=False)
            line.qty_available_today = 0
            line.free_qty_today = 0
            for move in moves:
                line.qty_available_today += move.product_uom._compute_quantity(move.quantity, line.product_uom_id)
                line.free_qty_today += move.product_id.uom_id._compute_quantity(move.forecast_availability,
                                                                                line.product_uom_id)
            line.scheduled_date = line.inquiry_id.date or line._expected_date()
            line.virtual_available_at_date = False
            treated |= line

        qty_processed_per_product = defaultdict(lambda: 0)
        # grouped_lines = defaultdict(lambda: self.env['inquiry.tools.supplies'])
        grouped_lines = self._compute_grouped_lines()
        # We first loop over the SO lines to group them by warehouse and schedule
        # date in order to batch the read of the quantities computed field.
        for line in self.filtered(lambda l: l.state in ('draft', 'initial', 'review_one', 'final', 'done')):
            if not (line.product_id and line.display_qty_widget):
                continue
            grouped_lines[(line.warehouse_id.id, line.inquiry_id.date or line._expected_date())] |= line

        for (warehouse, scheduled_date), lines in grouped_lines.items():
            product_qties = lines.mapped('product_id').with_context(to_date=scheduled_date, warehouse=warehouse).read([
                'qty_available',
                'free_qty',
                'virtual_available',
            ])
            qties_per_product = {
                product['id']: (product['qty_available'], product['free_qty'], product['virtual_available'])
                for product in product_qties
            }
            for line in lines:
                line.scheduled_date = scheduled_date
                qty_available_today, free_qty_today, virtual_available_at_date = qties_per_product[line.product_id.id]
                line.qty_available_today = qty_available_today - qty_processed_per_product[line.product_id.id]
                line.free_qty_today = free_qty_today - qty_processed_per_product[line.product_id.id]
                line.virtual_available_at_date = virtual_available_at_date - qty_processed_per_product[
                    line.product_id.id]
                line.forecast_expected_date = False
                product_qty = line.product_qty
                if line.product_uom_id and line.product_id.uom_id and line.product_uom_id != line.product_id.uom_id:
                    line.qty_available_today = line.product_id.uom_id._compute_quantity(line.qty_available_today,
                                                                                        line.product_uom_id)
                    line.free_qty_today = line.product_id.uom_id._compute_quantity(line.free_qty_today,
                                                                                   line.product_uom_id)
                    line.virtual_available_at_date = line.product_id.uom_id._compute_quantity(
                        line.virtual_available_at_date, line.product_uom_id)
                    product_qty = line.product_uom_id._compute_quantity(product_qty, line.product_id.uom_id)
                qty_processed_per_product[line.product_id.id] += product_qty
            treated |= lines
        remaining = (self - treated)
        remaining.virtual_available_at_date = False
        remaining.scheduled_date = False
        remaining.forecast_expected_date = False
        remaining.free_qty_today = False
        remaining.qty_available_today = False

    def _compute_grouped_lines(self):
        grouped_lines = defaultdict(lambda: self.env['inquiry.tools.supplies'])
        return grouped_lines

    def _expected_date(self):
        self.ensure_one()
        if self.state in ('draft', 'initial', 'review_one', 'final', 'done') and self.inquiry_id.date:
            inquiry_date = self.inquiry_id.date
        else:
            inquiry_date = fields.Datetime.now()
        return inquiry_date + timedelta(days=self.customer_lead or 0.0)
