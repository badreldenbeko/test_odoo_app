from odoo import fields, models, api, _
from datetime import datetime


class BudgetaryQuotationRequest(models.Model):
    _name = 'budgetary.quotation.request'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'Budgetary Quotation Request'

    name = fields.Char(
        required=True, copy=False, readonly=True,
        index='trigram',
        tracking=True,
        default=lambda self: _('New Costing'))
    state = fields.Selection(
        selection=[
            ('draft', _("Draft")),
            ('open', _("Open")),
            ('confirmed', _("Confirmed")),
            ('done', _("Contract Done")),
            ('cancel', _("Cancelled")),
        ],
        string=_("Status"), readonly=True, copy=False, index=True, tracking=True, default='draft')
    inquiry_id = fields.Many2one('inquiry.inquiry', required=True, copy=False, tracking=True)
    job_category = fields.Selection(
        [('trading', 'Trading'), ('service', 'Service'), ('manufacturing', 'Manufacturing'), ('other', 'Other')],
        related='inquiry_id.job_category')
    trading_job_category = fields.Selection([('finished', 'Finished'), ('semi_finished', 'Semi Finished')],
                                            related='inquiry_id.trading_job_category')
    date = fields.Datetime()
    warehouse_id = fields.Many2one('stock.warehouse', related='inquiry_id.warehouse_id')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    bqr_tools_supplies_ids = fields.One2many('bqr.tools.supplies', 'bqr_id')
    bqr_service_consumable_ids = fields.One2many('bqr.service.consumable', 'bqr_id')
    bqr_material_ids = fields.One2many('bqr.material', 'bqr_id')
    bqr_finished_product_ids = fields.One2many('bqr.finished.product', 'bqr_id')
    bqr_semi_finished_product_ids = fields.One2many('bqr.semi.finished.product', 'bqr_id')
    bqr_manufacturing_product_ids = fields.One2many('bqr.manufacturing.product', 'bqr_id')
    tools_selected = fields.Boolean(default=False)
    material_selected = fields.Boolean(default=False)
    finish_selected = fields.Boolean(default=False)
    semi_finish_selected = fields.Boolean(default=False)
    all_tools_selected = fields.Boolean(default=False)
    all_material_selected = fields.Boolean(default=False)
    all_finish_selected = fields.Boolean(default=False)
    all_semi_finish_selected = fields.Boolean(default=False)
    rfq_ids = fields.One2many('purchase.order', 'bqr_id')
    rfq_count = fields.Integer(compute='_calc_rfq_count')
    bqr_operation_ids = fields.One2many('bqr.operations.line', 'bqr_id', 'Operations', copy=False)
    m_margin = fields.Float(string=_('Margin'), digits='Product Price')
    m_margin_on = fields.Selection(
        selection=[
            ('cost', _("Cost")),
            ('min_price', _("Min Price")),
            ('avg_price', _("Avg Price")),
            ('max_price', _("Max Price")),
            ('confirmed', _("Confirmed")),
        ],
        string=_("Margin On"), copy=False, tracking=True, default='cost')
    m_margin_type = fields.Selection(
        selection=[
            ('percentage', _("Percentage")),
            ('amount', _("Amount")),
        ],
        string=_("Margin Type"), copy=False, tracking=True, default='percentage')
    t_margin = fields.Float(string=_('Margin'), digits='Product Price')
    t_margin_on = fields.Selection(
        selection=[
            ('cost', _("Cost")),
            ('min_price', _("Min Price")),
            ('avg_price', _("Avg Price")),
            ('max_price', _("Max Price")),
            ('confirmed', _("Confirmed")),
        ],
        string=_("Margin On"), copy=False, tracking=True, default='cost')
    t_margin_type = fields.Selection(
        selection=[
            ('percentage', _("Percentage")),
            ('amount', _("Amount")),
        ],
        string=_("Margin Type"), copy=False, tracking=True, default='percentage')
    fp_margin = fields.Float(string=_('Margin'), digits='Product Price')
    fp_margin_on = fields.Selection(
        selection=[
            ('cost', _("Cost")),
            ('min_price', _("Min Price")),
            ('avg_price', _("Avg Price")),
            ('max_price', _("Max Price")),
            ('confirmed', _("Confirmed")),
        ],
        string=_("Margin On"), copy=False, tracking=True, default='cost')
    fp_margin_type = fields.Selection(
        selection=[
            ('percentage', _("Percentage")),
            ('amount', _("Amount")),
        ],
        string=_("Margin Type"), copy=False, tracking=True, default='percentage')
    sfp_margin = fields.Float(string=_('Margin'), digits='Product Price')
    sfp_margin_on = fields.Selection(
        selection=[
            ('cost', _("Cost")),
            ('min_price', _("Min Price")),
            ('avg_price', _("Avg Price")),
            ('max_price', _("Max Price")),
            ('confirmed', _("Confirmed")),
        ],
        string=_("Margin On"), copy=False, tracking=True, default='cost')
    sfp_margin_type = fields.Selection(
        selection=[
            ('percentage', _("Percentage")),
            ('amount', _("Amount")),
        ],
        string=_("Margin Type"), copy=False, tracking=True, default='percentage')
    mm_margin = fields.Float(string=_('Margin'), digits='Product Price')
    mm_margin_on = fields.Selection(
        selection=[
            ('cost', _("Cost")),
            ('min_price', _("Min Price")),
            ('avg_price', _("Avg Price")),
            ('max_price', _("Max Price")),
            ('confirmed', _("Confirmed")),
        ],
        string=_("Margin On"), copy=False, tracking=True, default='cost')
    mm_margin_type = fields.Selection(
        selection=[
            ('percentage', _("Percentage")),
            ('amount', _("Amount")),
        ],
        string=_("Margin Type"), copy=False, tracking=True, default='percentage')
    o_margin = fields.Float(string=_('Margin'), digits='Product Price')
    o_margin_type = fields.Selection(
        selection=[
            ('percentage', _("Percentage")),
            ('amount', _("Amount")),
        ],
        string=_("Margin Type"), copy=False, tracking=True, default='amount')
    reserve_ids = fields.One2many('stock.picking', 'bqr_id')
    reserve_count = fields.Integer(compute='_calc_reserve_count')
    por_ids = fields.One2many('purchase.order.request', 'bqr_id')
    por_count = fields.Integer(compute='_calc_por_count')
    t_total_after_margin = fields.Float(string=_('Supplies'), digits='Product Price',
                                        compute='_calc_total_price_after_margin')
    m_total_after_margin = fields.Float(string=_('Materials'), digits='Product Price',
                                        compute='_calc_total_price_after_margin')
    fp_total_after_margin = fields.Float(string=_('Finish Product'), digits='Product Price',
                                         compute='_calc_total_price_after_margin')
    sfp_total_after_margin = fields.Float(string=_('Semi Finish Product'), digits='Product Price',
                                          compute='_calc_total_price_after_margin')
    mm_total_after_margin = fields.Float(string=_('Manufacturing Product'), digits='Product Price',
                                         compute='_calc_total_price_after_margin')
    o_total_after_margin = fields.Float(string=_('Workcenter'), digits='Product Price',
                                        compute='_calc_total_price_after_margin')
    emp_total_after_margin = fields.Float(string=_('Employees'), digits='Product Price',
                                          compute='_calc_total_price_after_margin')
    all_total_after_margin = fields.Float(string=_('Total Amount'), digits='Product Price',
                                          compute='_calc_total_price_after_margin')
    overhead_line_ids = fields.One2many('bqr.overhead.line', 'bqr_id')
    total_overheads = fields.Float(string=_('Overheads'), compute='_calc_total_price_after_margin')
    bqr_revision_ids = fields.One2many('bqr.revision', 'bqr_id')
    all_sent_to_por = fields.Boolean()

    @api.model_create_multi
    def create(self, vals_list):
        self.env.registry.clear_cache()
        for vals in vals_list:
            if not vals.get('name') and vals.get('inquiry_id'):
                inquiry = self.env['inquiry.inquiry'].search([('id', '=', vals.get('inquiry_id'))], limit=1)
                product_name = inquiry.name if inquiry else "Inquiry-"
                vals['name'] = product_name + '-' + self.env['ir.sequence'].next_by_code(
                    'seq.budgetary.quotation.request') or _("New Costing")
        res = super().create(vals_list)
        return res

    def unlink(self):
        self._delete_line_ids(self.bqr_tools_supplies_ids)
        self._delete_line_ids(self.bqr_service_consumable_ids)
        self._delete_line_ids(self.bqr_finished_product_ids)
        self._delete_line_ids(self.bqr_semi_finished_product_ids)
        self._delete_line_ids(self.bqr_manufacturing_product_ids)
        self._delete_line_ids(self.bqr_material_ids)
        self._delete_line_ids(self.bqr_operation_ids)
        return super(BudgetaryQuotationRequest, self).unlink()

    @api.model
    def _delete_line_ids(self, lines):
        if lines:
            for line in lines:
                line.unlink()

    @api.onchange('bqr_tools_supplies_ids')
    def _compute_tools_selected(self):
        selected_lines = list()
        for line in self.bqr_tools_supplies_ids:
            if line.selected:
                selected_lines.append(line)
        if selected_lines:
            self.tools_selected = True
        else:
            self.tools_selected = False
        if len(selected_lines) == len(self.bqr_tools_supplies_ids):
            self.all_tools_selected = True
        else:
            self.all_tools_selected = False

    def select_all_tools_to_por(self):
        for line in self.bqr_tools_supplies_ids:
            # if not line.rfq_create:
            line.selected = True
        self.tools_selected = True
        self.all_tools_selected = True

    def deselect_all_tools_to_por(self):
        for line in self.bqr_tools_supplies_ids:
            line.selected = False
        self.tools_selected = False
        self.all_tools_selected = False

    @api.onchange('bqr_material_ids')
    def _compute_material_selected(self):
        selected_lines = list()
        for line in self.bqr_material_ids:
            if line.selected:
                selected_lines.append(line)
        if selected_lines:
            self.material_selected = True
        else:
            self.material_selected = False
        if len(selected_lines) == len(self.bqr_material_ids):
            self.all_material_selected = True
        else:
            self.all_material_selected = False

    def select_all_material_to_rfq(self):
        for line in self.bqr_material_ids:
            # if not line.rfq_create:
            line.selected = True
        self.material_selected = True
        self.all_material_selected = True

    def deselect_all_material_to_rfq(self):
        for line in self.bqr_material_ids:
            line.selected = False
        self.material_selected = False
        self.all_material_selected = False

    @api.onchange('bqr_semi_finished_product_ids')
    def _compute_finish_selected(self):
        selected_lines = list()
        for line in self.bqr_finished_product_ids:
            if line.selected:
                selected_lines.append(line)
        if selected_lines:
            self.finish_selected = True
        else:
            self.finish_selected = False
        if len(selected_lines) == len(self.bqr_finished_product_ids):
            self.all_finish_selected = True
        else:
            self.all_finish_selected = False

    def select_all_finish_to_rfq(self):
        for line in self.bqr_finished_product_ids:
            # if not line.rfq_create:
            line.selected = True
        self.finish_selected = True
        self.all_finish_selected = True

    def deselect_all_finish_to_rfq(self):
        for line in self.bqr_finished_product_ids:
            line.selected = False
        self.finish_selected = False
        self.all_finish_selected = False

    @api.onchange('bqr_semi_finished_product_ids')
    def _compute_semi_finish_selected(self):
        selected_lines = list()
        for line in self.bqr_semi_finished_product_ids:
            if line.selected:
                selected_lines.append(line)
        if selected_lines:
            self.semi_finish_selected = True
        else:
            self.semi_finish_selected = False
        if len(selected_lines) == len(self.bqr_semi_finished_product_ids):
            self.all_semi_finish_selected = True
        else:
            self.all_semi_finish_selected = False

    def select_all_semi_finish_to_rfq(self):
        for line in self.bqr_semi_finished_product_ids:
            # if not line.rfq_create:
            line.selected = True
        self.semi_finish_selected = True
        self.all_semi_finish_selected = True

    def deselect_all_semi_finish_to_rfq(self):
        for line in self.bqr_semi_finished_product_ids:
            line.selected = False
        self.semi_finish_selected = False
        self.all_semi_finish_selected = False

    @api.depends('rfq_ids')
    def _calc_rfq_count(self):
        for rec in self:
            rec.rfq_count = len(rec.rfq_ids)

    def open_view_inquiry_rfqs(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'name': 'RFQs',
            'view_mode': 'tree,form',
            'domain': [('bqr_id', '=', self.id)],
            'context': {'default_bqr_id': self.id, 'default_inquiry_id': self.inquiry_id.id},
            'target': 'current',
        }

    @api.depends('reserve_ids')
    def _calc_reserve_count(self):
        for rec in self:
            rec.reserve_count = len(rec.reserve_ids)

    def open_view_bqr_reserve(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'name': 'Reserved',
            'view_mode': 'tree,form',
            'domain': [('bqr_id', '=', self.id)],
            'context': {'default_bqr_id': self.id},
            'target': 'current',
        }

    @api.depends('por_ids')
    def _calc_por_count(self):
        for rec in self:
            rec.por_count = len(rec.por_ids)

    def open_view_por_ids(self):
        por = self.env['purchase.order.request'].search([('bqr_id', '=', self.id)], limit=1)
        if por:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'purchase.order.request',
                'name': por.name,
                'view_type': 'form',
                'view_mode': 'form',
                'res_id': por.id,
                'target': 'current',
            }
        else:
            return True

    def change_all_material_margin(self):
        for line in self.bqr_material_ids:
            line.margin = self.m_margin

    def change_all_tools_margin(self):
        for line in self.bqr_tools_supplies_ids:
            line.margin = self.t_margin

    def change_all_finish_product_margin(self):
        for line in self.bqr_finished_product_ids:
            line.margin = self.fp_margin

    def change_all_semi_finish_product_margin(self):
        for line in self.bqr_semi_finished_product_ids:
            line.margin = self.sfp_margin

    def change_all_manufacturing_product_margin(self):
        for line in self.bqr_manufacturing_product_ids:
            line.margin = self.mm_margin

    def change_all_operation_margin(self):
        for line in self.bqr_operation_ids:
            line.margin = self.o_margin

    @api.depends('bqr_tools_supplies_ids', 'bqr_material_ids', 'bqr_operation_ids', 'overhead_line_ids')
    def _calc_total_price_after_margin(self):
        for rec in self:
            rec.t_total_after_margin = sum(rec.bqr_tools_supplies_ids.mapped('total_price_after_margin'))
            rec.m_total_after_margin = sum(rec.bqr_material_ids.mapped('total_price_after_margin'))
            rec.fp_total_after_margin = sum(rec.bqr_finished_product_ids.mapped('total_price_after_margin'))
            rec.sfp_total_after_margin = sum(rec.bqr_semi_finished_product_ids.mapped('total_price_after_margin'))
            rec.mm_total_after_margin = sum(rec.bqr_manufacturing_product_ids.mapped('total_price_after_margin'))
            rec.o_total_after_margin = sum(rec.bqr_operation_ids.mapped('total_workcenter_cost'))
            rec.emp_total_after_margin = sum(rec.bqr_operation_ids.mapped('total_employee_cost'))
            rec.total_overheads = sum(rec.overhead_line_ids.mapped('amount'))
            rec.all_total_after_margin = rec.fp_total_after_margin + rec.sfp_total_after_margin + rec.mm_total_after_margin

    def change_to_open_bqr(self):
        self.state = 'open'

    def confirm_bqr(self):
        self.state = 'confirmed'

    def done_bqr(self):
        self.state = 'done'

    def cancel_bqr(self):
        self.state = 'cancel'

    def back_to_draft_bqr(self):
        self.state = 'draft'

    def send_all_selected_to_por(self):
        por_obj = self.env['purchase.order.request'].search([('bqr_id', '=', self.id)], limit=1)
        new_por_obj = self.env['purchase.order.request']
        selected_tools_por_lines = list()
        selected_mat_por_lines = list()
        selected_finish_por_lines = list()
        selected_semi_finish_por_lines = list()
        tools_por_lines = list()
        mat_por_lines = list()
        finish_por_lines = list()
        semi_por_lines = list()
        for line in self.bqr_tools_supplies_ids:
            if line.selected and not line.sent_to_por:
                selected_tools_por_lines.append(line)
        for line in self.bqr_material_ids:
            if line.selected and not line.sent_to_por:
                selected_mat_por_lines.append(line)
        for line in self.bqr_finished_product_ids:
            if line.selected and not line.sent_to_por:
                selected_finish_por_lines.append(line)
        for line in self.bqr_semi_finished_product_ids:
            if line.selected and not line.sent_to_por:
                selected_semi_finish_por_lines.append(line)
        if por_obj:
            tools_por_lines = self._prepare_por_lines(por_obj.id, por_obj.por_tools_supplies_ids,
                                                      selected_tools_por_lines)
            mat_por_lines = self._prepare_por_lines(por_obj.id, por_obj.por_material_ids,
                                                    selected_mat_por_lines)
            finish_por_lines = self._prepare_por_lines(por_obj.id, por_obj.por_finish_ids,
                                                       selected_finish_por_lines)
            semi_por_lines = self._prepare_por_lines(por_obj.id, por_obj.por_semi_finish_ids,
                                                     selected_semi_finish_por_lines)
            try:
                por_obj.por_tools_supplies_ids = tools_por_lines
                por_obj.por_material_ids = mat_por_lines
                por_obj.por_finish_ids = finish_por_lines
                por_obj.por_semi_finish_ids = semi_por_lines
            except Exception as e:
                print(e)
        else:
            por_vals = {
                'bqr_id': self.id
            }
            try:
                new_por = new_por_obj.create(por_vals)
                tools_por_lines = self._prepare_por_lines(por_obj.id, por_obj.por_tools_supplies_ids,
                                                          selected_tools_por_lines)
                mat_por_lines = self._prepare_por_lines(por_obj.id, por_obj.por_material_ids,
                                                        selected_mat_por_lines)
                finish_por_lines = self._prepare_por_lines(por_obj.id, por_obj.por_semi_finish_ids,
                                                           selected_finish_por_lines)
                semi_por_lines = self._prepare_por_lines(por_obj.id, por_obj.por_semi_finish_ids,
                                                         selected_semi_finish_por_lines)
                new_por.por_tools_supplies_ids = tools_por_lines
                new_por.por_material_ids = mat_por_lines
                new_por.por_finish_ids = finish_por_lines
                new_por.por_semi_finish_ids = semi_por_lines

                utils = self.env['utils.utils']
                utils.send_group_notification(self.env.user, 'budgetary.quotation.request', self.id, 'purchase',
                                              'warning',
                                              'BOR Created',
                                              f'New BOR {new_por.name} Created')

            except Exception as e:
                print(e)

    def _prepare_por_lines(self, por_id, por_lines, selected_lines):
        lines = list()
        if len(por_lines) > 0:
            for line in selected_lines:
                for por_line in por_lines:
                    if line.product_id == por_line.product_id:
                        por_line.product_qty = line.product_qty
                    else:
                        lines.append((0, 0, {
                            'inquiry_id': line.inquiry_id.id,
                            'bqr_id': self.id,
                            'por_id': por_id,
                            'product_id': line.product_id.id,
                            'product_uom_id': line.product_uom_id.id,
                            'product_qty': line.product_qty
                        }))
            return lines
        else:
            for line in selected_lines:
                lines.append((0, 0, {
                    'inquiry_id': line.inquiry_id.id,
                    'bqr_id': self.id,
                    'por_id': por_id,
                    'product_id': line.product_id.id,
                    'product_uom_id': line.product_uom_id.id,
                    'product_qty': line.product_qty
                }))
            return lines

    def create_revision_from_bqr(self):
        rev_obj = self.env['bqr.revision']
        rev_vals = {
            'bqr_id': self.id,
            'date': datetime.now(),
            'm_margin': self.m_margin,
            'm_margin_on': self.m_margin_on,
            'm_margin_type': self.m_margin_type,
            't_margin': self.t_margin,
            't_margin_on': self.t_margin_on,
            't_margin_type': self.t_margin_type,
            'fp_margin': self.fp_margin,
            'fp_margin_on': self.fp_margin_on,
            'fp_margin_type': self.fp_margin_type,
            'sfp_margin': self.sfp_margin,
            'sfp_margin_on': self.sfp_margin_on,
            'sfp_margin_type': self.sfp_margin_type,
            'mm_margin': self.mm_margin,
            'mm_margin_on': self.mm_margin_on,
            'mm_margin_type': self.mm_margin_type,
            'o_margin': self.o_margin,
            'o_margin_type': self.o_margin_type,
        }
        new_rev = rev_obj.create(rev_vals)
        return True
