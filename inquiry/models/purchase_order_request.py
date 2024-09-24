from odoo import fields, models, api, _
from collections import defaultdict


class PurchaseOrderRequest(models.Model):
    _name = 'purchase.order.request'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'Purchase order request'

    name = fields.Char(
        required=True, copy=False, readonly=True,
        index='trigram',
        tracking=True,
        default=lambda self: _('New Purchase Request'))
    bqr_id = fields.Many2one('budgetary.quotation.request', required=True, copy=False)
    job_category = fields.Selection(
        [('trading', 'Trading'), ('service', 'Service'), ('manufacturing', 'Manufacturing'), ('other', 'Other')],
        related='bqr_id.inquiry_id.job_category')
    trading_job_category = fields.Selection([('finished', 'Finished'), ('semi_finished', 'Semi Finished')],
                                            related='bqr_id.inquiry_id.trading_job_category')
    por_tools_supplies_ids = fields.One2many('por.tools.supplies.line', 'por_id')
    por_material_ids = fields.One2many('por.material.line', 'por_id')
    por_finish_ids = fields.One2many('por.finish.line', 'por_id')
    por_semi_finish_ids = fields.One2many('por.semi.finish.line', 'por_id')
    rfq_ids = fields.One2many('purchase.order', 'por_id')
    rfq_count = fields.Integer(compute='_calc_rfq_count')
    tools_selected = fields.Boolean(default=False)
    all_tools_selected = fields.Boolean(default=False)
    finish_selected = fields.Boolean(default=False)
    all_finish_selected = fields.Boolean(default=False)
    semi_finish_selected = fields.Boolean(default=False)
    all_semi_finish_selected = fields.Boolean(default=False)
    material_selected = fields.Boolean(default=False)
    all_material_selected = fields.Boolean(default=False)

    def unlink(self):
        self._delete_line_ids(self.por_tools_supplies_ids)
        self._delete_line_ids(self.por_material_ids)
        self._delete_line_ids(self.por_finish_ids)
        self._delete_line_ids(self.por_semi_finish_ids)
        for line in self.bqr_id.bqr_tools_supplies_ids:
            line.sent_to_por = False
        for line in self.bqr_id.bqr_material_ids:
            line.sent_to_por = False
        return super(PurchaseOrderRequest, self).unlink()

    @api.model
    def _delete_line_ids(self, lines):
        if lines:
            for line in lines:
                line.unlink()

    @api.model_create_multi
    def create(self, vals_list):
        self.env.registry.clear_cache()
        for vals in vals_list:
            if not vals.get('name') and vals.get('bqr_id'):
                bqr = self.env['budgetary.quotation.request'].search([('id', '=', vals.get('bqr_id'))], limit=1)
                bqr_name = bqr.name if bqr.name else "CP-"
                vals['name'] = bqr_name + '-' + self.env['ir.sequence'].next_by_code(
                    'seq.purchase.order.request') or _("New Purchase Request")
        res = super().create(vals_list)
        return res

    @api.depends('rfq_ids')
    def _calc_rfq_count(self):
        for rec in self:
            rec.rfq_count = len(rec.rfq_ids)

    def open_view_por_rfqs(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'name': 'RFQs',
            'view_mode': 'tree,form',
            'domain': [('por_id', '=', self.id)],
            'context': {'default_por_id': self.id, 'default_bqr_id': self.bqr_id.id,
                        'default_inquiry_id': self.bqr_id.inquiry_id.id},
            'target': 'current',
        }

    def select_all_tools_line(self):
        for line in self.por_tools_supplies_ids:
            line.selected = True
        self.tools_selected = True
        self.all_tools_selected = True

    def deselect_all_tools_line(self):
        for line in self.por_tools_supplies_ids:
            line.selected = False
        self.tools_selected = False
        self.all_tools_selected = False

    @api.onchange('por_tools_ids')
    def _compute_tools_selected(self):
        selected_lines = list()
        for line in self.por_tools_supplies_ids:
            if line.selected:
                selected_lines.append(line)
        if selected_lines:
            self.tools_selected = True
        else:
            self.tools_selected = False
        if len(selected_lines) == len(self.por_tools_ids):
            self.all_tools_selected = True
        else:
            self.all_tools_selected = False

    def select_all_finish_line(self):
        for line in self.por_finish_ids:
            line.selected = True
        self.finish_selected = True
        self.all_finish_selected = True

    def deselect_all_finish_line(self):
        for line in self.por_finish_ids:
            line.selected = False
        self.finish_selected = False
        self.all_finish_selected = False

    @api.onchange('por_finish_ids')
    def _compute_finish_selected(self):
        selected_lines = list()
        for line in self.por_finish_ids:
            if line.selected:
                selected_lines.append(line)
        if selected_lines:
            self.finish_selected = True
        else:
            self.finish_selected = False
        if len(selected_lines) == len(self.por_finish_ids):
            self.all_finish_selected = True
        else:
            self.all_finish_selected = False

    def select_all_semi_finish_line(self):
        for line in self.por_semi_finish_ids:
            line.selected = True
        self.semi_finish_selected = True
        self.all_semi_finish_selected = True

    def deselect_all_semi_finish_line(self):
        for line in self.por_semi_finish_ids:
            line.selected = False
        self.semi_finish_selected = False
        self.all_semi_finish_selected = False

    @api.onchange('por_finish_ids')
    def _compute_semi_finish_selected(self):
        selected_lines = list()
        for line in self.por_semi_finish_ids:
            if line.selected:
                selected_lines.append(line)
        if selected_lines:
            self.semi_finish_selected = True
        else:
            self.semi_finish_selected = False
        if len(selected_lines) == len(self.por_semi_finish_ids):
            self.all_semi_finish_selected = True
        else:
            self.all_semi_finish_selected = False

    def select_all_material_line(self):
        for line in self.por_material_ids:
            line.selected = True
        self.material_selected = True
        self.all_material_selected = True

    def deselect_all_material_line(self):
        for line in self.por_material_ids:
            line.selected = False
        self.material_selected = False
        self.all_material_selected = False

    @api.onchange('por_material_ids')
    def _compute_material_selected(self):
        selected_lines = list()
        for line in self.por_material_ids:
            if line.selected:
                selected_lines.append(line)
        if selected_lines:
            self.material_selected = True
        else:
            self.material_selected = False
        if len(selected_lines) == len(self.por_material_ids):
            self.all_material_selected = True
        else:
            self.all_material_selected = False


class PorToolsSuppliesLine(models.Model):
    _name = 'por.tools.supplies.line'
    _inherit = 'inquiry.tools.supplies'
    _description = 'POR tools & supplies line'

    por_id = fields.Many2one('purchase.order.request', required=True)
    bqr_id = fields.Many2one('budgetary.quotation.request')
    rfq_ids = fields.Many2many('purchase.order')
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
    selected = fields.Boolean(string=_('Select'), default=False)

    @api.depends('product_id')
    def _calc_standard_price(self):
        for rec in self:
            rec.standard_price = rec.product_id.standard_price

    @api.depends('standard_price', 'product_qty')
    def _calc_total_standard_price(self):
        for rec in self:
            rec.total_standard_price = rec.standard_price * rec.product_qty

    @api.depends('product_id', 'por_id.rfq_ids')
    def _calc_product_prices_from_rfqs(self):
        for rec in self:
            rfq_list = list()
            price_list = list()
            if rec.por_id.rfq_ids:
                for rfq in rec.por_id.rfq_ids:
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

    @api.depends('product_id', 'por_id.rfq_ids')
    def _calc_purchase_price_rfq_id(self):
        for rec in self:
            rfq_id = None
            purchase_price = 0.0
            if rec.por_id.rfq_ids:
                for rfq in rec.por_id.rfq_ids:
                    if rfq.state == 'purchase':
                        rfq_id = rfq.id
                        for line in rfq.order_line:
                            if rec.product_id == line.product_id:
                                purchase_price = line.price_unit
            rec.purchase_rfq_id = rfq_id
            rec.rfq_purchase_price = purchase_price

    def _compute_grouped_lines(self):
        grouped_lines = defaultdict(lambda: self.env['por.tools.supplies.line'])
        return grouped_lines


class PorMaterial(models.Model):
    _name = 'por.material.line'
    _inherit = 'inquiry.tools.supplies'
    _description = 'POR Material'

    por_id = fields.Many2one('purchase.order.request', required=True)
    bqr_id = fields.Many2one('budgetary.quotation.request')
    rfq_ids = fields.Many2many('purchase.order')
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
    selected = fields.Boolean(string=_('Select'), default=False)

    @api.depends('product_id')
    def _calc_standard_price(self):
        for rec in self:
            rec.standard_price = rec.product_id.standard_price

    @api.depends('standard_price', 'product_qty')
    def _calc_total_standard_price(self):
        for rec in self:
            rec.total_standard_price = rec.standard_price * rec.product_qty

    @api.depends('product_id', 'por_id.rfq_ids')
    def _calc_product_prices_from_rfqs(self):
        for rec in self:
            rfq_list = list()
            price_list = list()
            if rec.por_id.rfq_ids:
                for rfq in rec.por_id.rfq_ids:
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

    @api.depends('product_id', 'por_id.rfq_ids')
    def _calc_purchase_price_rfq_id(self):
        for rec in self:
            rfq_id = None
            purchase_price = 0.0
            if rec.por_id.rfq_ids:
                for rfq in rec.por_id.rfq_ids:
                    if rfq.state == 'purchase':
                        rfq_id = rfq.id
                        for line in rfq.order_line:
                            if rec.product_id == line.product_id:
                                purchase_price = line.price_unit
            rec.purchase_rfq_id = rfq_id
            rec.rfq_purchase_price = purchase_price

    def _compute_grouped_lines(self):
        grouped_lines = defaultdict(lambda: self.env['por.material.line'])
        return grouped_lines


class PorFinish(models.Model):
    _name = 'por.finish.line'
    _inherit = 'por.tools.supplies.line'
    _description = 'POR Finish'

    def _compute_grouped_lines(self):
        grouped_lines = defaultdict(lambda: self.env['por.finish.line'])
        return grouped_lines


class PorSemiFinish(models.Model):
    _name = 'por.semi.finish.line'
    _inherit = 'por.tools.supplies.line'
    _description = 'POR Semi Finish'

    def _compute_grouped_lines(self):
        grouped_lines = defaultdict(lambda: self.env['por.semi.finish.line'])
        return grouped_lines
