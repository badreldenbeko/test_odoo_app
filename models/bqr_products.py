from datetime import timedelta

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from collections import defaultdict


class BqrToolsSupplies(models.Model):
    _name = 'bqr.tools.supplies'
    _inherit = 'inquiry.tools.supplies'
    _description = 'BQR Tools And Supplies'

    inquiry_id = fields.Many2one('inquiry.inquiry', required=False)
    bqr_id = fields.Many2one('budgetary.quotation.request', required=True)
    warehouse_id = fields.Many2one('stock.warehouse', related='bqr_id.warehouse_id')
    state = fields.Selection(
        selection=[
            ('draft', "Draft"),
            ('open', "Open"),
            ('confirmed', "Confirmed"),
            ('done', "Contract Done"),
            ('cancel', "Cancelled"),
        ], related='bqr_id.state')
    selected = fields.Boolean(string=_('Select'), default=False)
    currency_id = fields.Many2one(related='product_id.currency_id')
    standard_price = fields.Float(compute='_calc_standard_price')
    total_standard_price = fields.Float(string=_('Total Cost'), digits='Product Price',
                                        compute='_calc_total_standard_price')
    rfq_min_price = fields.Float(string=_('MIN Price'), digits='Product Price',
                                 compute='_calc_product_prices_from_rfqs')
    rfq_avg_price = fields.Float(string=_('AVG Price'), digits='Product Price',
                                 compute='_calc_product_prices_from_rfqs')
    rfq_max_price = fields.Float(string=_('MAX Price'), digits='Product Price',
                                 compute='_calc_product_prices_from_rfqs')
    rfq_purchase_price = fields.Float(string=_('Purchase Price'), digits='Product Price',
                                      compute='_calc_purchase_price_rfq_id')
    min_rfq_id = fields.Many2one('purchase.order', string=_('RFQ'), compute='_calc_product_prices_from_rfqs')
    max_rfq_id = fields.Many2one('purchase.order', string=_('RFQ'), compute='_calc_product_prices_from_rfqs')
    purchase_rfq_id = fields.Many2one('purchase.order', string=_('RFQ'), compute='_calc_purchase_price_rfq_id')
    margin = fields.Float(string=_('Margin'), digits='Product Price')
    price_after_margin = fields.Float(string=_('Price After Margin'), digits='Product Price',
                                      compute='_calc_price_after_margin')
    total_price_after_margin = fields.Float(string=_('Total After Margin'), digits='Product Price',
                                            compute='_calc_total_price_after_margin')
    sent_to_por = fields.Boolean()

    @api.depends('product_id')
    def _calc_standard_price(self):
        for rec in self:
            rec.standard_price = rec.product_id.standard_price

    @api.depends('standard_price', 'product_qty')
    def _calc_total_standard_price(self):
        for rec in self:
            rec.total_standard_price = rec.standard_price * rec.product_qty

    @api.depends('product_id', 'bqr_id.rfq_ids')
    def _calc_product_prices_from_rfqs(self):
        for rec in self:
            rfq_list = list()
            price_list = list()
            if rec.bqr_id.rfq_ids:
                for rfq in rec.bqr_id.rfq_ids:
                    for line in rfq.order_line:
                        if line.product_id == rec.product_id:
                            rfq_list.append(rfq)
                            price_list.append(line.price_unit)
            if len(rfq_list) > 0 and len(price_list) > 0:
                rec.rfq_min_price = min(price_list)
                rec.rfq_avg_price = sum(price_list) / len(price_list)
                rec.rfq_max_price = max(price_list)
                rec.min_rfq_id = rfq_list[price_list.index(min(price_list))].id
                rec.max_rfq_id = rfq_list[price_list.index(max(price_list))].id
            else:
                rec.rfq_min_price = 0
                rec.rfq_avg_price = 0
                rec.rfq_max_price = 0
                rec.min_rfq_id = None
                rec.max_rfq_id = None

    @api.depends('product_id', 'bqr_id.rfq_ids')
    def _calc_purchase_price_rfq_id(self):
        for rec in self:
            rfq_id = None
            purchase_price = 0.0
            if rec.bqr_id.rfq_ids:
                for rfq in rec.bqr_id.rfq_ids:
                    if rfq.state == 'purchase':
                        rfq_id = rfq.id
                        for line in rfq.order_line:
                            if rec.product_id == line.product_id:
                                purchase_price = line.price_unit
            rec.purchase_rfq_id = rfq_id
            rec.rfq_purchase_price = purchase_price

    @api.depends('margin', 'bqr_id.t_margin_on', 'bqr_id.t_margin_type')
    def _calc_price_after_margin(self):
        for rec in self:
            price_after_margin = 0.0
            if rec.bqr_id.t_margin_on == 'confirmed':
                if rec.bqr_id.t_margin_type == 'amount':
                    price_after_margin = rec.rfq_purchase_price + rec.margin
                else:
                    price_after_margin = rec.rfq_purchase_price + (rec.rfq_purchase_price * rec.margin / 100)
            elif rec.bqr_id.t_margin_on == 'min_price':
                if rec.bqr_id.t_margin_type == 'amount':
                    price_after_margin = rec.rfq_min_price + rec.margin
                else:
                    price_after_margin = rec.rfq_min_price + (rec.rfq_min_price * rec.margin / 100)
            elif rec.bqr_id.t_margin_on == 'max_price':
                if rec.bqr_id.t_margin_type == 'amount':
                    price_after_margin = rec.rfq_max_price + rec.margin
                else:
                    price_after_margin = rec.rfq_max_price + (rec.rfq_max_price * rec.margin / 100)
            elif rec.bqr_id.t_margin_on == 'avg_price':
                if rec.bqr_id.t_margin_type == 'amount':
                    price_after_margin = rec.rfq_avg_price + rec.margin
                else:
                    price_after_margin = rec.rfq_avg_price + (rec.rfq_avg_price * rec.margin / 100)
            elif rec.bqr_id.t_margin_on == 'cost':
                if rec.bqr_id.t_margin_type == 'amount':
                    price_after_margin = rec.standard_price + rec.margin
                else:
                    price_after_margin = rec.standard_price + (rec.standard_price * rec.margin / 100)
            rec.price_after_margin = price_after_margin

    @api.depends('product_qty', 'price_after_margin')
    def _calc_total_price_after_margin(self):
        for rec in self:
            price = 0.0
            price = rec.price_after_margin * rec.product_qty
            rec.total_price_after_margin = price

    @api.depends('product_type', 'product_qty', 'state', 'move_ids', 'product_uom_id')
    def _compute_qty_to_deliver(self):
        for line in self:
            line.qty_to_deliver = line.product_qty
            if line.state in ('draft', 'open', 'confirmed', 'done') and line.product_type in [
                'product'] and line.product_uom_id and line.qty_to_deliver > 0:
                if not line.move_ids:
                    line.display_qty_widget = False
                else:
                    line.display_qty_widget = True
            else:
                line.display_qty_widget = False

    @api.depends('product_id', 'route_id', 'bqr_id.warehouse_id', 'product_id.route_ids')
    def _compute_is_mto(self):
        self.is_mto = False
        for line in self:
            if not line.display_qty_widget:
                continue
            product = line.product_id
            product_routes = line.route_id or (product.route_ids + product.categ_id.total_route_ids)

            # Check MTO
            mto_route = line.bqr_id.warehouse_id.mto_pull_id.route_id
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

    @api.depends(
        'product_id', 'customer_lead', 'product_qty', 'product_uom_id', 'bqr_id.date',
        'move_ids', 'move_ids.forecast_expected_date', 'move_ids.forecast_availability',
        'warehouse_id')
    def _compute_qty_at_date(self):
        treated = self.browse()
        for line in self.filtered(lambda l: l.state in ('draft', 'open', 'confirmed', 'done')):
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
            line.scheduled_date = line.bqr_id.date or line._expected_date()
            line.virtual_available_at_date = False
            treated |= line

        qty_processed_per_product = defaultdict(lambda: 0)
        # grouped_lines = defaultdict(lambda: self.env['bqr.tools.supplies'])
        grouped_lines = self._compute_grouped_lines()
        # We first loop over the SO lines to group them by warehouse and schedule
        # date in order to batch the read of the quantities computed field.
        for line in self.filtered(lambda l: l.state in ('draft', 'open', 'confirmed', 'done')):
            if not (line.product_id and line.display_qty_widget):
                continue
            grouped_lines[(line.warehouse_id.id, line.bqr_id.date or line._expected_date())] |= line

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
        grouped_lines = defaultdict(lambda: self.env['bqr.tools.supplies'])
        return grouped_lines

    def _expected_date(self):
        self.ensure_one()
        if self.state in ('draft', 'open', 'confirmed', 'done') and self.bqr_id.date:
            bqr_date = self.bqr_id.date
        else:
            bqr_date = fields.Datetime.now()
        return bqr_date + timedelta(days=self.customer_lead or 0.0)

    def send_tools_to_por(self):
        por_obj = self.env['purchase.order.request'].search([('bqr_id', '=', self.bqr_id.id)], limit=1)
        new_por_obj = self.env['purchase.order.request']
        por_lines = list()
        if por_obj:
            if por_obj.por_tools_supplies_ids:
                for line in por_obj.por_tools_supplies_ids:
                    if line.product_id == self.product_id:
                        line.product_qty = self.product_qty
                    else:
                        por_lines.append((0, 0, {
                            'inquiry_id': self.inquiry_id.id,
                            'bqr_id': self.bqr_id.id,
                            'por_id': por_obj.id,
                            'product_id': self.product_id.id,
                            'product_uom_id': self.product_uom_id.id,
                            'product_qty': self.product_qty
                        }))
                        try:
                            por_obj.por_tools_supplies_ids = por_lines
                        except Exception as e:
                            print(e)
                    self.sent_to_por = True
                    self.selected = False
            else:
                por_lines.append((0, 0, {
                    'inquiry_id': self.inquiry_id.id,
                    'bqr_id': self.bqr_id.id,
                    'por_id': por_obj.id,
                    'product_id': self.product_id.id,
                    'product_uom_id': self.product_uom_id.id,
                    'product_qty': self.product_qty
                }))
                try:
                    por_obj.por_tools_supplies_ids = por_lines
                except Exception as e:
                    print(e)
            self.sent_to_por = True
            self.selected = False
        else:
            por_vals = {
                'bqr_id': self.bqr_id.id
            }
            try:
                new_por = new_por_obj.create(por_vals)
                por_lines.append((0, 0, {
                    'inquiry_id': self.inquiry_id.id,
                    'bqr_id': self.bqr_id.id,
                    'por_id': new_por.id,
                    'product_id': self.product_id.id,
                    'product_uom_id': self.product_uom_id.id,
                    'product_qty': self.product_qty
                }))
                new_por.por_tools_supplies_ids = por_lines

                utils = self.env['utils.utils']
                utils.send_group_notification(self.env.user, 'budgetary.quotation.request', self.bqr_id.id, 'purchase',
                                              'warning',
                                              'BOR Created', f'New BOR {new_por.name} Created')
                self.sent_to_por = True
                self.selected = False

            except Exception as e:
                print(e)


class BqrServiceConsumable(models.Model):
    _name = 'bqr.service.consumable'
    _inherit = 'bqr.tools.supplies'
    _description = 'BQR Service Consumable'

    product_id = fields.Many2one('product.product', string="Product", change_default=True, ondelete='restrict',
                                 index='btree_not_null',
                                 domain="[('detailed_type', '=', 'product')]")
    currency_id = fields.Many2one(related='product_id.currency_id')
    standard_price = fields.Float(string=_('Cost'), digits='Product Price', compute='_calc_total_standard_price')
    total_standard_price = fields.Float(string=_('Total Cost'), digits='Product Price',
                                        compute='_calc_total_standard_price')
    rfq_min_price = fields.Float(string=_('MIN Price'), digits='Product Price',
                                 compute='_calc_total_standard_price')
    rfq_avg_price = fields.Float(string=_('AVG Price'), digits='Product Price',
                                 compute='_calc_total_standard_price')
    rfq_max_price = fields.Float(string=_('MAX Price'), digits='Product Price',
                                 compute='_calc_total_standard_price')
    total_rfq_min_price = fields.Float(string=_('Total MIN Price'), digits='Product Price',
                                       compute='_calc_total_standard_price')
    total_rfq_avg_price = fields.Float(string=_('Total AVG Price'), digits='Product Price',
                                       compute='_calc_total_standard_price')
    total_rfq_max_price = fields.Float(string=_('Total MAX Price'), digits='Product Price',
                                       compute='_calc_total_standard_price')
    price_after_margin = fields.Float(string=_('Unit Margin'), digits='Product Price',
                                      compute='_calc_price_after_margin')
    total_price_after_margin = fields.Float(string=_('Sale Price'), digits='Product Price',
                                            compute='_calc_total_price_after_margin')
    price_margin_status = fields.Char(compute='_calc_price_margin_status')

    @api.depends('product_id', 'bqr_id.bqr_material_ids', 'bqr_id.bqr_operation_ids', 'bqr_id.bqr_tools_supplies_ids',
                 'bqr_id.bqr_service_consumable_ids')
    def _calc_total_standard_price(self):
        for rec in self:
            unit_price = 0.0
            after_margin = 0.0
            bom_obj = self.env['mrp.bom'].search([('product_tmpl_id', '=', rec.product_id.product_tmpl_id.id)], limit=1)
            if bom_obj:
                for line in rec.bqr_id.bqr_material_ids:
                    if line.product_id.product_tmpl_id.id in bom_obj.bom_line_ids.mapped('product_id').ids:
                        unit_price += line.total_price_after_margin / rec.product_qty
                        after_margin += line.price_after_margin
                for operation in rec.bqr_id.bqr_operation_ids:
                    if operation.operation_id.id in bom_obj.operation_ids.ids:
                        unit_price += operation.quantity_price_after_margin / rec.product_qty
                        after_margin += operation.after_margin
            for tool in rec.bqr_id.bqr_tools_supplies_ids:
                after_margin += (tool.total_price_after_margin / len(rec.bqr_id.bqr_service_consumable_ids)) / rec.product_qty
                # after_margin += tool.price_after_margin / rec.product_qty
            for over_head in rec.bqr_id.overhead_line_ids:
                after_margin += (over_head.amount / len(rec.bqr_id.bqr_service_consumable_ids)) / rec.product_qty
                # after_margin += over_head.amount / rec.product_qty
            rec.standard_price = unit_price
            rec.total_standard_price = unit_price * rec.product_qty
            rec.price_after_margin = after_margin
            rec.total_price_after_margin = rec.price_after_margin * rec.product_qty

    @api.depends('bqr_id')
    def _calc_price_margin_status(self):
        for rec in self:
            if rec.bqr_id.t_margin <= 0:
                rec.price_margin_status = 'Tools & Supplies Margin Not Apply'
            elif rec.bqr_id.m_margin <= 0:
                rec.price_margin_status = 'Materials Margin Not Apply'
            elif rec.bqr_id.o_margin <= 0:
                rec.price_margin_status = 'Operations Margin Not Apply'
            elif rec.bqr_id.t_margin <= 0 and rec.bqr_id.m_margin <= 0 and rec.bqr_id.o_margin <= 0:
                rec.price_margin_status = 'No Margin Apply'
            elif rec.bqr_id.t_margin > 0 and rec.bqr_id.m_margin > 0 and rec.bqr_id.o_margin > 0:
                rec.price_margin_status = 'All Margin Apply'

    def _compute_grouped_lines(self):
        grouped_lines = defaultdict(lambda: self.env['bqr.service.consumable'])
        return grouped_lines


class BqrMaterial(models.Model):
    _name = 'bqr.material'
    _inherit = 'bqr.tools.supplies'
    _description = 'BQR Material'

    rfq_min_price = fields.Float(string=_('MIN Price'), digits='Product Price',
                                 compute='_calc_product_prices_from_rfqs')
    rfq_avg_price = fields.Float(string=_('AVG Price'), digits='Product Price',
                                 compute='_calc_product_prices_from_rfqs')
    rfq_max_price = fields.Float(string=_('MAX Price'), digits='Product Price',
                                 compute='_calc_product_prices_from_rfqs')
    price_after_margin = fields.Float(string=_('Price After Margin'), digits='Product Price',
                                      compute='_calc_price_after_margin')
    total_price_after_margin = fields.Float(string=_('Total After Margin'), digits='Product Price',
                                            compute='_calc_total_price_after_margin')

    @api.depends('margin', 'bqr_id.m_margin_on', 'bqr_id.m_margin_type')
    def _calc_price_after_margin(self):
        for rec in self:
            price_after_margin = 0.0
            if rec.bqr_id.m_margin_on == 'confirmed':
                if rec.bqr_id.m_margin_type == 'amount':
                    price_after_margin = rec.rfq_purchase_price + rec.margin
                else:
                    price_after_margin = rec.rfq_purchase_price + (rec.rfq_purchase_price * rec.margin / 100)
            elif rec.bqr_id.m_margin_on == 'cost':
                if rec.bqr_id.m_margin_type == 'amount':
                    price_after_margin = rec.standard_price + rec.margin
                else:
                    price_after_margin = rec.standard_price + (rec.standard_price * rec.margin / 100)
            elif rec.bqr_id.m_margin_on == 'min_price':
                if rec.bqr_id.m_margin_type == 'amount':
                    price_after_margin = rec.rfq_min_price + rec.margin
                else:
                    price_after_margin = rec.rfq_min_price + (rec.rfq_min_price * rec.margin / 100)
            elif rec.bqr_id.m_margin_on == 'max_price':
                if rec.bqr_id.m_margin_type == 'amount':
                    price_after_margin = rec.rfq_max_price + rec.margin
                else:
                    price_after_margin = rec.rfq_max_price + (rec.rfq_max_price * rec.margin / 100)
            elif rec.bqr_id.m_margin_on == 'avg_price':
                if rec.bqr_id.m_margin_type == 'amount':
                    price_after_margin = rec.rfq_avg_price + rec.margin
                else:
                    price_after_margin = rec.rfq_avg_price + (rec.rfq_avg_price * rec.margin / 100)
            rec.price_after_margin = price_after_margin

    def _compute_grouped_lines(self):
        grouped_lines = defaultdict(lambda: self.env['bqr.material'])
        return grouped_lines

    def send_mat_to_por(self):
        por_obj = self.env['purchase.order.request'].search([('bqr_id', '=', self.bqr_id.id)], limit=1)
        new_por_obj = self.env['purchase.order.request']
        por_lines = list()
        print(self.product_id)
        if por_obj:
            print(por_obj)
            if por_obj.por_material_ids.ids:
                for line in por_obj.por_material_ids:
                    if line.product_id == self.product_id:
                        line.product_qty = self.product_qty
                    else:
                        por_lines.append((0, 0, {
                            'inquiry_id': self.inquiry_id.id,
                            'bqr_id': self.bqr_id.id,
                            'por_id': por_obj.id,
                            'product_id': self.product_id.id,
                            'product_uom_id': self.product_uom_id.id,
                            'product_qty': self.product_qty
                        }))
                        try:
                            por_obj.por_material_ids = por_lines
                        except Exception as e:
                            print(e)
                    self.sent_to_por = True
                    self.selected = False

            else:
                por_lines.append((0, 0, {
                    'inquiry_id': self.inquiry_id.id,
                    'bqr_id': self.bqr_id.id,
                    'por_id': por_obj.id,
                    'product_id': self.product_id.id,
                    'product_uom_id': self.product_uom_id.id,
                    'product_qty': self.product_qty
                }))
                try:
                    por_obj.por_material_ids = por_lines
                except Exception as e:
                    print(e)
                self.sent_to_por = True
                self.selected = False
        else:
            por_vals = {
                'bqr_id': self.bqr_id.id
            }
            try:
                new_por = new_por_obj.create(por_vals)
                por_lines.append((0, 0, {
                    'inquiry_id': self.inquiry_id.id,
                    'bqr_id': self.bqr_id.id,
                    'por_id': new_por.id,
                    'product_id': self.product_id.id,
                    'product_uom_id': self.product_uom_id.id,
                    'product_qty': self.product_qty
                }))
                new_por.por_material_ids = por_lines

                utils = self.env['utils.utils']
                utils.send_group_notification(self.env.user, 'budgetary.quotation.request', self.bqr_id.id, 'purchase',
                                              'warning',
                                              'BOR Created',
                                              f'New BOR {new_por.name} Created')
                self.sent_to_por = True
                self.selected = False

            except Exception as e:
                print(e)


class BqrFinishedProduct(models.Model):
    _name = 'bqr.finished.product'
    _inherit = 'bqr.tools.supplies'
    _description = 'BQR Finished Product'

    def _compute_grouped_lines(self):
        grouped_lines = defaultdict(lambda: self.env['bqr.finished.product'])
        return grouped_lines

    @api.depends('margin', 'bqr_id.t_margin_on', 'bqr_id.t_margin_type')
    def _calc_price_after_margin(self):
        for rec in self:
            price_after_margin = 0.0
            if rec.bqr_id.fp_margin_on == 'confirmed':
                if rec.bqr_id.fp_margin_type == 'amount':
                    price_after_margin = rec.rfq_purchase_price + rec.margin
                else:
                    price_after_margin = rec.rfq_purchase_price + (rec.rfq_purchase_price * rec.margin / 100)
            elif rec.bqr_id.fp_margin_on == 'min_price':
                if rec.bqr_id.fp_margin_type == 'amount':
                    price_after_margin = rec.rfq_min_price + rec.margin
                else:
                    price_after_margin = rec.rfq_min_price + (rec.rfq_min_price * rec.margin / 100)
            elif rec.bqr_id.fp_margin_on == 'max_price':
                if rec.bqr_id.fp_margin_type == 'amount':
                    price_after_margin = rec.rfq_max_price + rec.margin
                else:
                    price_after_margin = rec.rfq_max_price + (rec.rfq_max_price * rec.margin / 100)
            elif rec.bqr_id.fp_margin_on == 'avg_price':
                if rec.bqr_id.fp_margin_type == 'amount':
                    price_after_margin = rec.rfq_avg_price + rec.margin
                else:
                    price_after_margin = rec.rfq_avg_price + (rec.rfq_avg_price * rec.margin / 100)
            elif rec.bqr_id.fp_margin_on == 'cost':
                if rec.bqr_id.fp_margin_type == 'amount':
                    price_after_margin = rec.standard_price + rec.margin
                else:
                    price_after_margin = rec.standard_price + (rec.standard_price * rec.margin / 100)
            rec.price_after_margin = price_after_margin

    def send_tools_to_por(self):
        por_obj = self.env['purchase.order.request'].search([('bqr_id', '=', self.bqr_id.id)], limit=1)
        new_por_obj = self.env['purchase.order.request']
        por_lines = list()
        if por_obj:
            if por_obj.por_finish_ids:
                for line in por_obj.por_finish_ids:
                    if line.product_id == self.product_id:
                        line.product_qty = self.product_qty
                    else:
                        por_lines.append((0, 0, {
                            'inquiry_id': self.inquiry_id.id,
                            'bqr_id': self.bqr_id.id,
                            'por_id': por_obj.id,
                            'product_id': self.product_id.id,
                            'product_uom_id': self.product_uom_id.id,
                            'product_qty': self.product_qty
                        }))
                        try:
                            por_obj.por_finish_ids = por_lines
                        except Exception as e:
                            print(e)
                    self.sent_to_por = True
                    self.selected = False
            else:
                por_lines.append((0, 0, {
                    'inquiry_id': self.inquiry_id.id,
                    'bqr_id': self.bqr_id.id,
                    'por_id': por_obj.id,
                    'product_id': self.product_id.id,
                    'product_uom_id': self.product_uom_id.id,
                    'product_qty': self.product_qty
                }))
                try:
                    por_obj.por_finish_ids = por_lines
                except Exception as e:
                    print(e)
            self.sent_to_por = True
        else:
            por_vals = {
                'bqr_id': self.bqr_id.id
            }
            try:
                new_por = new_por_obj.create(por_vals)
                por_lines.append((0, 0, {
                    'inquiry_id': self.inquiry_id.id,
                    'bqr_id': self.bqr_id.id,
                    'por_id': new_por.id,
                    'product_id': self.product_id.id,
                    'product_uom_id': self.product_uom_id.id,
                    'product_qty': self.product_qty
                }))
                new_por.por_finish_ids = por_lines

                utils = self.env['utils.utils']
                utils.send_group_notification(self.env.user, 'budgetary.quotation.request', self.bqr_id.id, 'purchase',
                                              'warning',
                                              'BOR Created',
                                              f'New BOR {new_por.name} Created')
                self.sent_to_por = True
                self.selected = False
            except Exception as e:
                print(e)


class BqrSemiFinishedProduct(models.Model):
    _name = 'bqr.semi.finished.product'
    _inherit = 'bqr.tools.supplies'
    _description = 'BQR Semi Finished Product'

    price_margin_status = fields.Char(compute='_calc_price_margin_status')
    total_semi_finish_cost = fields.Float(digits='Product Price', compute='_calc_total_semi_finish_cost',
                                          string=_('Total cost'))

    @api.depends('product_id', 'bqr_id.bqr_semi_finished_product_ids', 'bqr_id.bqr_tools_supplies_ids',
                 'bqr_id.bqr_material_ids', 'bqr_id.bqr_operation_ids', 'bqr_id.overhead_line_ids', 'purchase_rfq_id')
    def _calc_total_semi_finish_cost(self):
        for rec in self:
            unit_cost = 0.0
            bom_obj = self.env['mrp.bom'].search([('product_tmpl_id', '=', rec.product_id.product_tmpl_id.id)], limit=1)
            if bom_obj:
                for line in rec.bqr_id.bqr_material_ids:
                    if line.product_id.id in bom_obj.bom_line_ids.mapped('product_id').ids:
                        unit_cost += line.total_price_after_margin / rec.product_qty
                for operation in rec.bqr_id.bqr_operation_ids:
                    if operation.operation_id.id in bom_obj.operation_ids.ids:
                        unit_cost += operation.quantity_price_after_margin / rec.product_qty
            unit_cost += (sum(rec.bqr_id.bqr_tools_supplies_ids.mapped('total_price_after_margin')) / len(
                rec.bqr_id.bqr_semi_finished_product_ids)) / rec.product_qty
            unit_cost += (sum(rec.bqr_id.overhead_line_ids.mapped('amount')) / len(
                rec.bqr_id.bqr_semi_finished_product_ids)) / rec.product_qty
            if rec.purchase_rfq_id:
                unit_cost += rec.rfq_purchase_price
            else:
                unit_cost += rec.standard_price
            rec.total_semi_finish_cost = unit_cost

    @api.depends('bqr_id')
    def _calc_price_margin_status(self):
        for rec in self:
            if rec.bqr_id.t_margin <= 0:
                rec.price_margin_status = 'Tools & Supplies Margin Not Apply'
            elif rec.bqr_id.m_margin <= 0:
                rec.price_margin_status = 'Materials Margin Not Apply'
            elif rec.bqr_id.o_margin <= 0:
                rec.price_margin_status = 'Operations Margin Not Apply'
            elif rec.bqr_id.t_margin <= 0 and rec.bqr_id.m_margin <= 0 and rec.bqr_id.o_margin <= 0:
                rec.price_margin_status = 'No Margin Apply'
            elif rec.bqr_id.t_margin > 0 and rec.bqr_id.m_margin > 0 and rec.bqr_id.o_margin > 0:
                rec.price_margin_status = 'All Margin Apply'

    @api.depends('margin', 'bqr_id.sfp_margin_type')
    def _calc_price_after_margin(self):
        for rec in self:
            price_after_margin = 0.0
            if rec.bqr_id.sfp_margin_type == 'amount':
                price_after_margin = rec.total_semi_finish_cost + rec.margin
            else:
                price_after_margin = rec.total_semi_finish_cost + (rec.total_semi_finish_cost * rec.margin / 100)
            rec.price_after_margin = price_after_margin

    def send_tools_to_por(self):
        por_obj = self.env['purchase.order.request'].search([('bqr_id', '=', self.bqr_id.id)], limit=1)
        new_por_obj = self.env['purchase.order.request']
        por_lines = list()
        if por_obj:
            if por_obj.por_semi_finish_ids:
                for line in por_obj.por_semi_finish_ids:
                    if line.product_id == self.product_id:
                        line.product_qty = self.product_qty
                    else:
                        por_lines.append((0, 0, {
                            'inquiry_id': self.inquiry_id.id,
                            'bqr_id': self.bqr_id.id,
                            'por_id': por_obj.id,
                            'product_id': self.product_id.id,
                            'product_uom_id': self.product_uom_id.id,
                            'product_qty': self.product_qty
                        }))
                        try:
                            por_obj.por_semi_finish_ids = por_lines
                        except Exception as e:
                            print(e)
                    self.sent_to_por = True
                    self.selected = False
            else:
                por_lines.append((0, 0, {
                    'inquiry_id': self.inquiry_id.id,
                    'bqr_id': self.bqr_id.id,
                    'por_id': por_obj.id,
                    'product_id': self.product_id.id,
                    'product_uom_id': self.product_uom_id.id,
                    'product_qty': self.product_qty
                }))
                try:
                    por_obj.por_semi_finish_ids = por_lines
                except Exception as e:
                    print(e)
            self.sent_to_por = True
        else:
            por_vals = {
                'bqr_id': self.bqr_id.id
            }
            try:
                new_por = new_por_obj.create(por_vals)
                por_lines.append((0, 0, {
                    'inquiry_id': self.inquiry_id.id,
                    'bqr_id': self.bqr_id.id,
                    'por_id': new_por.id,
                    'product_id': self.product_id.id,
                    'product_uom_id': self.product_uom_id.id,
                    'product_qty': self.product_qty
                }))
                new_por.por_semi_finish_ids = por_lines

                utils = self.env['utils.utils']
                utils.send_group_notification(self.env.user, 'budgetary.quotation.request', self.bqr_id.id, 'purchase',
                                              'warning',
                                              'BOR Created',
                                              f'New BOR {new_por.name} Created')
                self.sent_to_por = True
                self.selected = False
            except Exception as e:
                print(e)

    def _compute_grouped_lines(self):
        grouped_lines = defaultdict(lambda: self.env['bqr.semi.finished.product'])
        return grouped_lines


class BqrManufacturingProduct(models.Model):
    _name = 'bqr.manufacturing.product'
    _inherit = 'bqr.tools.supplies'
    _description = 'BQR Manufacturing Product'

    total_manu_finish_cost = fields.Float(digits='Product Price', string=_('Total cost'),
                                          compute='_calc_manufacturing_total_cost')
    total_standard_price = fields.Float(string=_('Total Cost'), digits='Product Price',
                                        compute='_calc_total_standard_price')

    def _compute_grouped_lines(self):
        grouped_lines = defaultdict(lambda: self.env['bqr.manufacturing.product'])
        return grouped_lines

    @api.depends('product_id', 'bqr_id.bqr_material_ids', 'bqr_id.bqr_operation_ids', 'bqr_id.bqr_tools_supplies_ids',
                 'bqr_id.bqr_manufacturing_product_ids', 'bqr_id.overhead_line_ids')
    def _calc_manufacturing_total_cost(self):
        for rec in self:
            unit_cost = 0.0
            bom_obj = self.env['mrp.bom'].search([('product_tmpl_id', '=', rec.product_id.product_tmpl_id.id)], limit=1)
            if bom_obj:
                for line in rec.bqr_id.bqr_material_ids:
                    if line.product_id.product_tmpl_id.id in bom_obj.bom_line_ids.mapped('product_id').ids:
                        unit_cost += line.total_price_after_margin / rec.product_qty
                for operation in rec.bqr_id.bqr_operation_ids:
                    if operation.operation_id.id in bom_obj.operation_ids.ids:
                        unit_cost += operation.quantity_price_after_margin / rec.product_qty
            unit_cost += (sum(rec.bqr_id.bqr_tools_supplies_ids.mapped('total_price_after_margin')) / len(
                rec.bqr_id.bqr_manufacturing_product_ids)) / rec.product_qty
            unit_cost += (sum(rec.bqr_id.overhead_line_ids.mapped('amount')) / len(
                rec.bqr_id.bqr_manufacturing_product_ids)) / rec.product_qty
            unit_cost += rec.rfq_purchase_price
            rec.total_manu_finish_cost = unit_cost

    @api.depends('total_standard_price', 'product_qty')
    def _calc_total_standard_price(self):
        for rec in self:
            rec.total_standard_price = rec.total_manu_finish_cost * rec.product_qty

    @api.depends('margin', 'bqr_id.t_margin_on', 'bqr_id.t_margin_type')
    def _calc_price_after_margin(self):
        for rec in self:
            price_after_margin = 0.0
            if rec.bqr_id.mm_margin_on == 'confirmed':
                if rec.bqr_id.mm_margin_type == 'amount':
                    price_after_margin = rec.rfq_purchase_price + rec.margin
                else:
                    price_after_margin = rec.rfq_purchase_price + (rec.rfq_purchase_price * rec.margin / 100)
            elif rec.bqr_id.mm_margin_on == 'min_price':
                if rec.bqr_id.mm_margin_type == 'amount':
                    price_after_margin = rec.rfq_min_price + rec.margin
                else:
                    price_after_margin = rec.rfq_min_price + (rec.rfq_min_price * rec.margin / 100)
            elif rec.bqr_id.mm_margin_on == 'max_price':
                if rec.bqr_id.mm_margin_type == 'amount':
                    price_after_margin = rec.rfq_max_price + rec.margin
                else:
                    price_after_margin = rec.rfq_max_price + (rec.rfq_max_price * rec.margin / 100)
            elif rec.bqr_id.mm_margin_on == 'avg_price':
                if rec.bqr_id.mm_margin_type == 'amount':
                    price_after_margin = rec.rfq_avg_price + rec.margin
                else:
                    price_after_margin = rec.rfq_avg_price + (rec.rfq_avg_price * rec.margin / 100)
            elif rec.bqr_id.mm_margin_on == 'cost':
                if rec.bqr_id.mm_margin_type == 'amount':
                    price_after_margin = rec.total_manu_finish_cost + rec.margin
                else:
                    price_after_margin = rec.total_manu_finish_cost + (rec.total_manu_finish_cost * rec.margin / 100)
            rec.price_after_margin = price_after_margin
