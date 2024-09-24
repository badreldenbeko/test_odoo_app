import collections
from datetime import datetime

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class Inquiry(models.Model):
    _name = 'inquiry.inquiry'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'Inquiry Table'

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    name = fields.Char(
        string=_("Inquiry Reference"),
        required=True, copy=False, readonly=True,
        index='trigram',
        tracking=True,
        default=lambda self: _('New Inquiry'))
    state = fields.Selection(
        selection=[
            ('draft', "Draft"),
            ('initial', "Initial Contract"),
            ('final', "Final Contract Review"),
            ('done', "Contract Done"),
            ('regret', "Regret"),
            ('review_one', "Contract Review One"),
        ],
        string=_("Status"), copy=False, index=True, tracking=True, default='draft')
    job_category = fields.Selection(
        [('trading', 'Trading'), ('service', 'Service'), ('manufacturing', 'Manufacturing'), ('other', 'Other')],
        required=True, copy=False, tracking=True)
    trading_job_category = fields.Selection([('finished', 'Finished'), ('semi_finished', 'Semi Finished')],
                                            copy=False, tracking=True)
    has_prp = fields.Boolean()
    prp_ids = fields.One2many('project.realization.plan', 'inquiry_id')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    partner_id = fields.Many2one('res.partner', required=True, string=_("Customer"), tracking=True)
    partner_rfq_ref_no = fields.Char(string=_('RFQ/REF NO.'))
    partner_rfq_ref_date = fields.Date(string=_('RFQ/REF Date'))
    date = fields.Datetime(string=_('Inquiry Date'), default=datetime.now(), tracking=True, copy=False)
    delivery_date = fields.Datetime(string=_('Delivery Date'), tracking=True, copy=False)
    confirmed_delivery_date = fields.Char(tracing=True)
    payment_terms_id = fields.Many2one('account.payment.term', tracking=True)
    incoterm_id = fields.Many2one('account.incoterms', tracking=True)
    analytic_account_id = fields.Many2one('account.analytic.account', tracking=True)
    new_product = fields.Boolean(default=False, tracking=True)
    new_product_design = fields.Selection(
        [('beginning', 'Desired In The Beginning'), ('later', 'Desired In A Later Stage')], tracking=True)
    # mrp_eco_ids = fields.One2many('inquiry.mrp.eco.line', 'inquiry_id')
    # mrp_eco_line_count = fields.Integer(compute='_calc_mrp_eco_count')
    new_product_name = fields.Char()
    project_ids = fields.One2many('project.project', 'inquiry_id', string=_('Projects'))
    project_count = fields.Integer(compute='_calc_project_count')
    description_of_work = fields.Html()
    requirement_line_ids = fields.One2many('inquiry.requirements', 'inquiry_id')
    scope_of_product_ids = fields.One2many('scope.of.product.line', 'inquiry_id')
    is_manufacturing = fields.Boolean(default=False, tracking=True)
    is_field_service = fields.Boolean(default=False, tracking=True)
    is_repair_or_service = fields.Boolean(default=False, tracking=True)
    initial_review_ids = fields.One2many('initial.review.line', 'inquiry_id')
    tools_supplies_line_ids = fields.One2many('inquiry.tools.supplies', 'inquiry_id')
    service_line_ids = fields.One2many('inquiry.service.line', 'inquiry_id')
    trading_finished_line_ids = fields.One2many('inquiry.trading.finished.line', 'inquiry_id')
    trading_semi_finished_line_ids = fields.One2many('inquiry.trading.semi.finished.line', 'inquiry_id')
    manufacturing_line_ids = fields.One2many('inquiry.manufacturing.line', 'inquiry_id')
    bqr_ids = fields.One2many('budgetary.quotation.request', 'inquiry_id')
    bqr_count = fields.Integer(compute='_calc_bqr_count')
    rfq_ids = fields.One2many('purchase.order', 'inquiry_id')
    rfq_count = fields.Integer(compute='_calc_rfq_count')
    reserve_ids = fields.One2many('stock.picking', 'inquiry_id')
    reserve_count = fields.Integer(compute='_calc_reserve_count')
    margin_type = fields.Selection(
        selection=[
            ('percentage', _("Percentage")),
            ('amount', _("Amount")),
        ],
        string=_("Extra Margin Type"), copy=False, tracking=True, default='percentage')
    margin = fields.Float(string=_('Extra Margin'), digits='Product Price')
    sale_order_ids = fields.One2many('sale.order', 'inquiry_id')
    sale_order_count = fields.Integer(compute='_calc_sale_order_count')
    manufacturing_order_ids = fields.One2many('mrp.production', 'inquiry_id')
    manufacturing_order_count = fields.Integer(compute='_calc_manufacturing_orders_count')
    inquiry_followers_ids = fields.One2many('inquiry.followers', 'inquiry_id')
    all_followers_accept = fields.Boolean(compute='_compute_all_followers_accept', default=False)

    @api.depends('inquiry_followers_ids')
    def _compute_all_followers_accept(self):
        for rec in self:
            all_accept = False
            count = 0
            for line in rec.inquiry_followers_ids:
                if line.state == 'accept':
                    count += 1
            if count == len(rec.inquiry_followers_ids):
                all_accept = True
            rec.all_followers_accept = all_accept

    order_acceptance = fields.Selection([('yes', 'Yes'), ('no', 'No')])
    order_acceptance_detail = fields.Html()
    customer_requirements_detail = fields.Html()
    amendment_review = fields.Html()
    commercial_line_ids = fields.One2many('inquiry.commercial.line', 'inquiry_id')
    commercial_tax = fields.Boolean(string=_('Tax'))
    commercial_insurance = fields.Boolean(string=_('Insurance'))
    commercial_others = fields.Boolean(string=_('Others'))
    commercial_dr_comment = fields.Html(string=_('Comment'))
    commercial_invoice = fields.Boolean(string=_('Invoice'))
    commercial_d_note = fields.Boolean(string=_('D. Note'))
    commercial_packing_list = fields.Boolean(string=_('Packing List'))
    commercial_lpo = fields.Boolean(string=_('LPO'))
    commercial_dns_comment = fields.Html(string=_('Comment'))
    commercial_comments = fields.Html(string=_('Additional Comments'))
    design_development_ids = fields.One2many('design.development.line', 'inquiry_id')
    attached_design = fields.Binary(string=_('Attach Phase wise design review reports'))
    attached_design_comments = fields.Html(string=_('comments'))
    design_development_comments = fields.Html(string=_('Additional Comments'))
    qa_qc_ids = fields.One2many('inquiry.qa.qc.line', 'inquiry_id')
    qa_qc_comments = fields.Html(string=_('Additional Comments'))
    machinery_ids = fields.One2many('inquiry.machinery.line', 'inquiry_id')

    # Signs
    bdm_id = fields.Many2one('hr.employee', string=_('Prepared By: BDM'))
    bdm_date = fields.Date(string=_('Date'))
    tm_id = fields.Many2one('hr.employee', string=_('Prepared By: Technical Manager'))
    tm_date = fields.Date(string=_('Date'))
    om_id = fields.Many2one('hr.employee', string=_('Prepared By: Operations Manager'))
    om_date = fields.Date(string=_('Date'))
    qcm_id = fields.Many2one('hr.employee', string=_('Prepared By: QA/QC Supervisor'))
    qcm_date = fields.Date(string=_('Date'))
    risk_identification = fields.Boolean(string=_('Risk Identification Note Required?'))
    risk_identification_file = fields.Binary(string=_('Risk Identification Note'))
    risk_identification_comment = fields.Html(string=_('Additional Comments'))
    sale_order_id = fields.Many2one('sale.order', string=_('Select SO To Create WO'))
    post_review_sale_order_id = fields.Many2one('sale.order', string=_('Select SO To print Order review'))

    print_wo_id = fields.Many2one('mrp.production', string=_('Select WO To Print'))

    @api.model
    def _default_warehouse_id(self):
        return self.env.user._get_default_warehouse_id()

    warehouse_id = fields.Many2one('stock.warehouse', default=_default_warehouse_id, check_company=True, store=True)

    # Design & development Selection
    design_status = fields.Selection([('not', 'No Applicable'), ('yes', 'Yes'), ('no', 'No')], default='not')
    delivery_terms = fields.Selection([('local', 'Local'), ('inter', 'International')], default='local')

    print_wo_comment = fields.Html(compute='_compute_print_wo_comment')

    parent_id = fields.Many2one('inquiry.inquiry')
    children_count = fields.Integer(compute='_compute_children_count')

    @api.depends('print_wo_id')
    def _compute_print_wo_comment(self):
        for rec in self:
            rec.print_wo_comment = rec.print_wo_id.report_comment

    def unlink(self):
        self._delete_line_ids(self.requirement_line_ids)
        self._delete_line_ids(self.scope_of_product_ids)
        self._delete_line_ids(self.initial_review_ids)
        self._delete_line_ids(self.tools_supplies_line_ids)
        self._delete_line_ids(self.service_line_ids)
        self._delete_line_ids(self.trading_finished_line_ids)
        self._delete_line_ids(self.trading_semi_finished_line_ids)
        self._delete_line_ids(self.manufacturing_line_ids)
        self._delete_line_ids(self.bqr_ids)
        self._delete_line_ids(self.rfq_ids)
        self._delete_line_ids(self.reserve_ids)
        self._delete_line_ids(self.sale_order_ids)
        self._delete_line_ids(self.manufacturing_order_ids)
        self._delete_line_ids(self.inquiry_followers_ids)
        self._delete_line_ids(self.design_development_ids)
        self._delete_line_ids(self.prp_ids)
        return super(Inquiry, self).unlink()

    @api.model
    def _delete_line_ids(self, lines):
        if lines:
            for line in lines:
                line.unlink()

    def open_record(self):
        # group_obj = self.env.ref('purchase.group_purchase_user')
        # print(group_obj.users.mapped('partner_id'))
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'inquiry.inquiry',
            'name': self.name,
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'current',
        }

    def write(self, vals):
        res = super(Inquiry, self).write(vals)
        # if vals.get('parent_id'):
        #     children = self.env['inquiry.inquiry'].search([('parent_id', '=', vals.get('parent_id'))])
        #     self.name = self.parent_id.name + '-' + str(len(children))
        return res

    @api.model_create_multi
    def create(self, vals_list):
        vals_list = self._prepare_inquiry_name(vals_list)
        res = super().create(vals_list)
        self._create_project_for_inquiry(res)
        self._create_prp_lines(res)
        self._create_scope_of_product_lines(res)
        self._create_initial_review_lines(res)
        self._create_commercial_lines(res)
        self._create_design_development_lines(res)
        self._create_qa_qc_lines(res)

        utils = self.env['utils.utils']
        utils.send_group_notification(self.env.user, 'inquiry.inquiry', res.id, 'sales',
                                      'success',
                                      'Inquiry Created', f'New Inquiry {res.name} Created')
        return res

    def _prepare_inquiry_name(self, vals_list):
        for vals in vals_list:
            # COMPUTE SEQUENCE FOR INQUIRY DEPENDS ON JOB CATEGORY
            if vals.get('name', _("New Inquiry")) == _("New Inquiry"):
                if vals['job_category'] == 'trading':
                    if vals['trading_job_category'] == 'finished':
                        vals['name'] = self.env['ir.sequence'].next_by_code('seq.trading.finished.inquiry') or _(
                            "New Trading Finished Inquiry")
                    elif vals['trading_job_category'] == 'semi_finished':
                        vals['name'] = self.env['ir.sequence'].next_by_code('seq.trading.semi.finished.inquiry') or _(
                            "New Trading Semi Finished Inquiry")
                elif vals['job_category'] == 'service':
                    vals['name'] = self.env['ir.sequence'].next_by_code('seq.service.inquiry') or _(
                        "New Service Inquiry")
                elif vals['job_category'] == 'manufacturing':
                    vals['name'] = self.env['ir.sequence'].next_by_code('seq.manufacturing.inquiry') or _(
                        "New Manufacturing Inquiry")
                elif vals['job_category'] == 'other':
                    vals['name'] = self.env['ir.sequence'].next_by_code('seq.other.inquiry') or _(
                        "New Other Inquiry")

            # CREATE NEW ANALYTIC ACCOUNT FOR THE INQUIRY
            if not vals.get('analytic_account_id'):
                account_analytic_plan = self.env['account.analytic.plan'].search(
                    [('name', '=', 'Inquiry')], limit=1)
                analytic_account_vals = {
                    'name': vals['name'],
                    'plan_id': account_analytic_plan.id,
                    'partner_id': vals['partner_id'],
                    'code': vals['name'],
                }
                new_inquiry_analytic_account = self.env['account.analytic.account'].create(analytic_account_vals)
                vals['analytic_account_id'] = new_inquiry_analytic_account.id
        return vals_list

    def _create_prp_lines(self, rec):
        if rec.has_prp:
            requirements_objs = self.env['project.realization.plan.requirements'].search([])
            requirements_lines = list()
            for requirement in requirements_objs:
                requirements_lines.append((0, 0, {
                    'prp_requirements': requirement.id,
                }))
            rec.prp_ids = requirements_lines

    def _create_scope_of_product_lines(self, rec):
        scope_of_product_objs = self.env['scope.of.product'].search([])
        scope_of_product_lines = list()
        for scope in scope_of_product_objs:
            scope_of_product_lines.append((0, 0, {
                'scope_of_product_id': scope.id,
            }))
        rec.scope_of_product_ids = scope_of_product_lines

    def _create_initial_review_lines(self, rec):
        initial_review_objs = self.env['initial.review'].search([])
        initial_review_lines = list()
        for initial_review in initial_review_objs:
            initial_review_lines.append((0, 0, {
                'initial_review_id': initial_review.id,
            }))
        rec.initial_review_ids = initial_review_lines

    def _create_commercial_lines(self, rec):
        commercial_objs = self.env['inquiry.commercial'].search([])
        commercial_lines = list()
        for commercial in commercial_objs:
            commercial_lines.append((0, 0, {
                'commercial_id': commercial.id,
            }))
        rec.commercial_line_ids = commercial_lines

    def _create_design_development_lines(self, rec):
        design_development_objs = self.env['design.development'].search([])
        design_development_lines = list()
        for design_development in design_development_objs:
            design_development_lines.append((0, 0, {
                'design_development_id': design_development.id,
            }))
        rec.design_development_ids = design_development_lines

    def _create_qa_qc_lines(self, rec):
        qa_qc_objs = self.env['inquiry.qa.qc'].search([])
        qa_qc_lines = list()
        for qa_ac in qa_qc_objs:
            qa_qc_lines.append((0, 0, {
                'qa_qc_id': qa_ac.id,
            }))
        rec.qa_qc_ids = qa_qc_lines

    def _create_project_for_inquiry(self, rec):
        seq_name = self.env['ir.sequence'].next_by_code('seq.project')
        if rec.job_category == 'other':
            project_name = f'{seq_name.split("-")[0]}-' or _(
                "New Project")
        else:
            project_name = f'{seq_name.split("-")[0]}-{rec.name.split("-")[0]}-{rec.name.split("-")[2]}-{seq_name.split("-")[1]}' or _(
                "New Project")
        vals = {
            'name': project_name,
            'inquiry_id': rec.id,
            'partner_id': rec.partner_id.id,

        }
        self.env['project.project'].create(vals)

    @api.depends('project_ids')
    def _calc_project_count(self):
        for rec in self:
            rec.project_count = len(rec.project_ids)

    def open_view_inquiry_projects(self):
        project = self.env['project.project'].search([('inquiry_id', '=', self.id)], limit=1)
        if project:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'project.project',
                'name': project.name,
                'view_type': 'form',
                'view_mode': 'form',
                'res_id': project.id,
                'target': 'current',
            }
        else:
            return True

    def open_view_inquiry_sale_order(self):
        # sale_order = self.env['sale.order'].search([('inquiry_id', '=', self.id)], limit=1)
        # if sale_order:
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'name': 'Quotations',
            'view_mode': 'tree,form',
            'domain': [('inquiry_id', '=', self.id)],
            'context': {'default_inquiry_id': self.id},
            'target': 'current',
        }
        # else:
        #     return True

    def open_view_inquiry_mrp_production(self):
        # mrp_production = self.env['mrp.production'].search([('inquiry_id', '=', self.id)], limit=1)
        # if mrp_production:
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.production',
            'name': 'Work orders',
            'view_mode': 'tree,form',
            'domain': [('inquiry_id', '=', self.id)],
            'context': {'default_inquiry_id': self.id},
            'target': 'current',
        }
        # else:
        #     return True

    @api.depends('bqr_ids')
    def _calc_bqr_count(self):
        for rec in self:
            rec.bqr_count = len(rec.bqr_ids)

    def open_view_inquiry_bqrs(self):
        bqr = self.env['budgetary.quotation.request'].search([('inquiry_id', '=', self.id)], limit=1)
        if bqr:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'budgetary.quotation.request',
                'name': bqr.name,
                'view_type': 'form',
                'view_mode': 'form',
                'res_id': bqr.id,
                'target': 'current',
            }
        else:
            return True

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
            'domain': [('inquiry_id', '=', self.id)],
            'context': {'default_inquiry_id': self.id},
            'target': 'current',
        }

    @api.depends('reserve_ids')
    def _calc_reserve_count(self):
        for rec in self:
            rec.reserve_count = len(rec.reserve_ids)

    def open_view_inquiry_reserve(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'name': 'Reserved',
            'view_mode': 'tree,form',
            'domain': [('inquiry_id', '=', self.id)],
            'context': {'default_inquiry_id': self.id},
            'target': 'current',
        }

    def check_inquiry_requirements(self):
        for line in self.requirement_line_ids:
            if line.state == 'not_done':
                raise ValidationError(_(f'Requirements in line {line.name} not done'))
        self.state = 'initial'

    def back_to_stage(self):
        for rec in self:
            state = self.env.context.get('state')
            print(state)
            rec.state = state

    # @api.onchange('parent_id')
    # def to_review_one(self):
    #     if self.parent_id:
    #         self.parent_id.state = 'review_one'

    def create_review_from_inquiry(self):
        children = self.env['inquiry.inquiry'].search([('parent_id', '=', self.id)])
        new_inquiry_vals = {
            'parent_id': self.id,
            'name': self.name + '/' + str(len(children) + 1),
            'partner_id': self.partner_id.id,
            'job_category': self.job_category,
            'trading_job_category': self.trading_job_category,
            'has_prp': self.has_prp,
            'new_product': self.new_product,
            'new_product_design': self.new_product_design,
        }
        inquiry_obj = self.env['inquiry.inquiry']
        new_inquiry = inquiry_obj.create(new_inquiry_vals)
        self.state = 'review_one'
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'inquiry.inquiry',
            'res_id': new_inquiry.id,
            'name': new_inquiry.name,
            'view_mode': 'form',
            'target': 'current',
        }

    def _compute_children_count(self):
        for rec in self:
            children = self.env['inquiry.inquiry'].search([('parent_id', '=', rec.id)])
            rec.children_count = len(children)

    def open_inquiry_reviews(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'inquiry.inquiry',
            'name': self.name + ' ' + 'Reviews',
            'view_mode': 'tree,form',
            'domain': [('parent_id', '=', self.id)],
            'context': {'default_parent_id': self.id},
            'target': 'current',
        }

    def create_bqr_from_inquiry(self):
        # Create New BQR
        new_bqr = self._create_bqr_from_inquiry()
        # Create BQR Tools & Supplies List
        tools_list = self._prepare_normal_lines(new_bqr, self.tools_supplies_line_ids)
        new_bqr.bqr_tools_supplies_ids = tools_list
        if self.job_category == 'service':
            # Create Service Consumable List
            service_consumable_list = self._prepare_service_consumable_lines(new_bqr)
            new_bqr.bqr_service_consumable_ids = service_consumable_list
            print(service_consumable_list)
            # Create Material List
            material_list = self._prepare_service_material_lines(new_bqr)
            new_bqr.bqr_material_ids = material_list
            # Create operation List
            operation_list = self._prepare_service_operations_lines(new_bqr)
            new_bqr.bqr_operation_ids = operation_list
        if self.job_category == 'trading':
            if self.trading_job_category == 'finished':
                finished_list = self._prepare_normal_lines(new_bqr, self.trading_finished_line_ids)
                new_bqr.bqr_finished_product_ids = finished_list
            elif self.trading_job_category == 'semi_finished':
                semi_finished_list = self._prepare_normal_lines(new_bqr, self.trading_semi_finished_line_ids)
                new_bqr.bqr_semi_finished_product_ids = semi_finished_list
                material_list = self._prepare_bom_material_lines(new_bqr, self.trading_semi_finished_line_ids)
                new_bqr.bqr_material_ids = material_list
                operation_list = self._prepare_operations(new_bqr, self.trading_semi_finished_line_ids)
                new_bqr.bqr_operation_ids = operation_list
        elif self.job_category == 'manufacturing':
            manufacturing_list = self._prepare_normal_lines(new_bqr, self.manufacturing_line_ids)
            new_bqr.bqr_manufacturing_product_ids = manufacturing_list
            material_list = self._prepare_bom_material_lines(new_bqr, self.manufacturing_line_ids)
            new_bqr.bqr_material_ids = material_list
            operation_list = self._prepare_operations(new_bqr, self.manufacturing_line_ids)
            new_bqr.bqr_operation_ids = operation_list
        # Open BQR
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'budgetary.quotation.request',
            'name': new_bqr.name,
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': new_bqr.id,
            'target': 'current',
        }

    def _create_bqr_from_inquiry(self):
        bqr_obj = self.env['budgetary.quotation.request']
        tools_line_list = list()
        bqr_vals = {
            'inquiry_id': self.id,
            'state': 'open',
            'date': self.date,
        }
        try:
            new_bqr = bqr_obj.create(bqr_vals)
            return new_bqr
        except Exception as e:
            print(e)

    def _prepare_normal_lines(self, bqr, lines):
        line_list = list()
        for line in lines:
            moves = self.env['stock.move'].search([('product_id', '=', line.product_id.id)])
            amount = line.product_uom_id._compute_quantity(line.product_qty, line.product_id.uom_id)
            line_vals = (0, 0, {
                'inquiry_id': self.id,
                'bqr_id': bqr.id,
                'product_id': line.product_id.id,
                'warehouse_id': bqr.warehouse_id.id,
                'move_ids': moves,
                'product_uom_id': line.product_id.uom_id.id,
                'product_qty': amount,
            })
            line_list.append(line_vals)
        return line_list

    def _prepare_service_consumable_lines(self, bqr):
        service_consumable_list = list()
        for line in self.service_line_ids:
            if not line.product_id.service_consumable_ids:
                raise ValidationError(_(f'Service have not consumables.'))
            service_consumable = self.env['service.consumable'].search(
                [('product_id', '=', line.product_id.product_tmpl_id.id)], limit=1)

            if service_consumable:
                for line_consumable in service_consumable.consumable_line_ids:
                    # product_obj = self.env['product.product'].search([('product_tmpl_id', '=', line_consumable.product_id.id)])
                    # print(line_consumable.product_id.product_id)
                    moves = self.env['stock.move'].search([('product_id', '=', line_consumable.product_id.id)])
                    amount = line_consumable.product_uom_id._compute_quantity(line_consumable.product_qty,
                                                                              line.product_uom_id)
                    line_vals = (0, 0, {
                        'warehouse_id': bqr.warehouse_id.id,
                        'move_ids': moves,
                        'inquiry_id': self.id,
                        'bqr_id': bqr.id,
                        'product_id': line_consumable.product_id.id,
                        'product_uom_id': line.product_uom_id.id,
                        # 'product_qty': line_consumable.product_qty * line.product_qty,
                        'product_qty': amount * line.product_qty,
                    })
                    pro_obj = self.env['product.product'].search(
                        [('product_tmpl_id', '=', line_consumable.product_id.id)])
                    pro_vals = (0, 0, {
                        'product_id': pro_obj.id,
                        'product_qty': amount * line.product_qty,
                    })
                    service_consumable_list.append(pro_vals)
        return service_consumable_list

    def _prepare_service_material_lines(self, bqr):
        material_list = list()
        print(self.service_line_ids)
        for line in self.service_line_ids:
            service_consumable = self.env['service.consumable'].search(
                [('product_id', '=', line.product_id.product_tmpl_id.id)], limit=1)
            if not service_consumable.consumable_line_ids:
                raise ValidationError(_(f'Service {line.product_id.name} not have consumables.'))
            for line_consumable in service_consumable.consumable_line_ids:
                if not line_consumable.product_id.bom_ids:
                    raise ValidationError(_(f'Consumable {line_consumable.name} not have Materials.'))
                bom_obj = self.env['mrp.bom'].search([('product_tmpl_id', '=', line_consumable.product_id.id)], limit=1)
                for bom_line in bom_obj.bom_line_ids:
                    moves = self.env['stock.move'].search([('product_id', '=', bom_line.product_id.id)])
                    amount = bom_line.product_uom_id._compute_quantity(bom_line.product_qty,
                                                                       bom_line.product_uom_id)
                    line_vals = (0, 0, {
                        'warehouse_id': bqr.warehouse_id.id,
                        'move_ids': moves,
                        'inquiry_id': self.id,
                        'bqr_id': bqr.id,
                        'product_id': bom_line.product_id.id,
                        'product_uom_id': bom_line.product_uom_id.id,
                        # 'product_qty': bom_line.product_qty * line_consumable.product_qty * line.product_qty,
                        'product_qty': amount * line.product_qty,
                    })
                    material_list.append(line_vals)
        return material_list

    def _prepare_service_operations_lines(self, bqr):
        operations_list = list()
        for line in self.service_line_ids:
            service_consumable = self.env['service.consumable'].search(
                [('product_id', '=', line.product_id.product_tmpl_id.id)], limit=1)
            if not service_consumable.consumable_line_ids:
                raise ValidationError(_(f'Service {line.product_id.name} not have consumables.'))
            # operations_list = self._prepare_operations(bqr, service_consumable.consumable_line_ids)
            for line in service_consumable.consumable_line_ids:
                if not line.product_id.bom_ids:
                    raise ValidationError(_(f'Consumable {line.product_id.name} not have BOM.'))
                bom_obj = self.env['mrp.bom'].search([('product_tmpl_id', '=', line.product_id.id)],
                                                     limit=1)
                for operation in bom_obj.operation_ids:
                    line_vals = (0, 0, {
                        'inquiry_id': self.id,
                        'bqr_id': bqr.id,
                        'operation_id': operation.id,
                    })
                    operations_list.append(line_vals)
        return operations_list

    def _prepare_operations(self, bqr, lines):
        operations_list = list()
        for line in lines:
            if not line.product_id.bom_ids:
                raise ValidationError(_(f'Consumable {line.product_id.name} not have BOM.'))
            bom_obj = self.env['mrp.bom'].search([('product_tmpl_id', '=', line.product_id.id)],
                                                 limit=1)
            for operation in bom_obj.operation_ids:
                line_vals = (0, 0, {
                    'inquiry_id': self.id,
                    'bqr_id': bqr.id,
                    'operation_id': operation.id,
                })
                operations_list.append(line_vals)
        return operations_list

    def _prepare_bom_material_lines(self, bqr, lines):
        material_list = list()
        for line in lines:
            bom_obj = self.env['mrp.bom'].search([('product_tmpl_id', '=', line.product_id.product_tmpl_id.id)],
                                                 limit=1)
            man_amount = line.product_uom_id._compute_quantity(line.product_qty,
                                                               line.product_id.uom_id)
            if bom_obj:
                for bom_line in bom_obj.bom_line_ids:
                    moves = self.env['stock.move'].search([('product_id', '=', bom_line.product_id.id)])
                    amount = bom_line.product_uom_id._compute_quantity(bom_line.product_qty,
                                                                       bom_line.product_uom_id)
                    line_vals = (0, 0, {
                        'warehouse_id': bqr.warehouse_id.id,
                        'move_ids': moves,
                        'inquiry_id': self.id,
                        'bqr_id': bqr.id,
                        'product_id': bom_line.product_id.id,
                        'product_uom_id': bom_line.product_uom_id.id,
                        # 'product_qty': bom_line.product_qty * line_consumable.product_qty * line.product_qty,
                        'product_qty': amount * man_amount,
                    })
                    material_list.append(line_vals)
        return material_list

    def apply_extra_margin(self):
        for line in self.service_line_ids:
            line.margin = self.margin
        for line in self.manufacturing_line_ids:
            line.margin = self.margin

    @api.depends('sale_order_ids')
    def _calc_sale_order_count(self):
        for rec in self:
            rec.sale_order_count = len(rec.sale_order_ids)

    def open_view_sale_orders(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'name': 'Quotations',
            'view_mode': 'kanban,tree,form',
            'domain': [('inquiry_id', '=', self.id)],
            'context': {'default_inquiry_id': self.id},
            'target': 'current',
        }

    def create_sale_order_from_service_lines(self):
        sale_order_obj = self.env['sale.order']
        order_lines = list()
        if self.service_line_ids:
            order_lines = self._prepare_sale_order_lines(self.service_line_ids)
        if self.trading_finished_line_ids:
            order_lines = self._prepare_sale_order_lines(self.trading_finished_line_ids)
        if self.trading_semi_finished_line_ids:
            order_lines = self._prepare_sale_order_lines(self.trading_semi_finished_line_ids)
        if self.manufacturing_line_ids:
            order_lines = self._prepare_sale_order_lines(self.manufacturing_line_ids)
        sale_order_vals = {
            'inquiry_id': self.id,
            'partner_id': self.partner_id.id,
            'payment_term_id': self.payment_terms_id.id,
            'order_line': order_lines,
        }
        try:
            new_sale_order = sale_order_obj.create(sale_order_vals)
            self.state = 'final'
        except Exception as e:
            print(e)

    def _prepare_sale_order_lines(self, line_ids):
        order_lines = list()
        for line in line_ids:
            order_lines.append((0, 0, {
                'product_id': line.product_id.product_tmpl_id.id,
                'product_uom': line.product_uom_id.id,
                'product_uom_qty': line.product_qty,
                'price_unit': line.price_with_extra_margin,
            }))
        return order_lines

    @api.depends('manufacturing_order_ids')
    def _calc_manufacturing_orders_count(self):
        for rec in self:
            rec.manufacturing_order_count = len(rec.manufacturing_order_ids)

    def open_view_manufacturing_orders(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.production',
            'name': 'Work Orders',
            'view_mode': 'kanban,tree,form',
            'domain': [('inquiry_id', '=', self.id)],
            'context': {'default_inquiry_id': self.id},
            'target': 'current',
        }

    def create_mrp_production_from_service_lines(self):
        is_order_confirmed = False
        if not self.sale_order_ids:
            raise ValidationError(_(f'There are no sales orders to create WO'))
        else:
            for order in self.sale_order_ids:
                if order.state == 'sale':
                    is_order_confirmed = True
        if not is_order_confirmed:
            raise ValidationError(_(f'There are no confirmed sales orders to create WO'))

        if not self.sale_order_id:
            raise ValidationError(_(f'Please select a sales order to create new work order'))

        mrp_production_obj = self.env['mrp.production']
        move_obj = self.env['stock.picking']
        if self.service_line_ids:
            sale_order_manufacturing_count = self.env['mrp.production'].search(
                [('inquiry_sale_id', '=', self.sale_order_id.id)])
            count = sum(self.sale_order_id.order_line.mapped('product_uom_qty'))
            if sale_order_manufacturing_count >= count:
                raise ValidationError(_(f'You cant create more work orders'))
            move_lins = list()
            for line in self.service_line_ids:
                if line.product_id.service_consumable_ids:
                    for consu in line.product_id.service_consumable_ids[0].consumable_line_ids:
                        old_mrp = self.env['mrp.production'].search(
                            [('inquiry_id', '=', self.id), ('inquiry_sale_id', '=', self.sale_order_id.id),
                             ('product_id', '=', consu.product_id.id)], limit=1)
                        if old_mrp:
                            if old_mrp.product_qty == line.product_qty:
                                raise ValidationError(_(f'WO with all quantity created before'))
                        mrp_production_vals = dict()
                        mrp_production_vals['inquiry_id'] = self.id
                        mrp_production_vals['inquiry_sale_id'] = self.sale_order_id.id
                        mrp_production_vals['product_id'] = consu.product_id.id
                        mrp_production_vals['product_uom_qty'] = consu.product_uom_id.id
                        mrp_production_vals['product_qty'] = line.product_qty

                        new_mrp_production = mrp_production_obj.create(mrp_production_vals)
                        move_lins.append((0, 0, {
                            'location_id': 8,
                            'location_dest_id': 5,
                            'has_tracking': 'serial',
                            'date_deadline': datetime.now(),
                            'name': consu.product_id.name,
                            'product_id': consu.product_id.id,
                            'quantity': line.product_qty,
                            'product_uom_qty': line.product_qty,
                            'product_uom': line.product_uom_id.id
                        }))
                else:
                    raise ValidationError(_(f'Service dont have service consumables'))

            try:
                new_move = move_obj.create({
                    'state': 'draft',
                    'date_deadline': datetime.now(),
                    'partner_id': self.partner_id.id,
                    'inquiry_id': self.id,
                    'picking_type_id': 2,
                    'inquiry_sale_id': self.sale_order_id.id,
                    'origin': self.sale_order_id.name,
                    'sale_id': self.sale_order_id.id,
                    'move_ids_without_package': move_lins
                })
                new_move.sale_id = self.sale_order_id.id
                self.sale_order_id.delivery_count += 1
            except Exception as e:
                print('Error Create Move ------------->', e)
        elif self.trading_semi_finished_line_ids:
            sale_order_manufacturing_count = self.env['mrp.production'].search(
                [('inquiry_sale_id', '=', self.sale_order_id.id)])
            count = sum(self.sale_order_id.order_line.mapped('product_uom_qty'))
            if len(sale_order_manufacturing_count) >= count:
                raise ValidationError(_(f'You cant create more work orders'))
            for line in self.trading_semi_finished_line_ids:
                product = self.env['sale.order.line'].search(
                    [('order_id', '=', self.sale_order_id.id), ('product_id', '=', line.product_id.id)], limit=1)
                mrp_production_vals = dict()
                mrp_production_vals['inquiry_id'] = self.id
                mrp_production_vals['inquiry_sale_id'] = self.sale_order_id.id
                mrp_production_vals['product_id'] = line.product_id.id
                mrp_production_vals['product_uom_qty'] = line.product_uom_id.id
                mrp_production_vals['product_qty'] = product.product_uom_qty or 1
                try:
                    new_mrp_production = mrp_production_obj.create(mrp_production_vals)
                    self.sale_order_id = None
                except Exception as e:
                    print(e)
        elif self.manufacturing_line_ids:
            sale_order_manufacturing_count = self.env['mrp.production'].search(
                [('inquiry_sale_id', '=', self.sale_order_id.id)])
            count = sum(self.sale_order_id.order_line.mapped('product_uom_qty'))
            if len(sale_order_manufacturing_count) >= count:
                raise ValidationError(_(f'You cant create more work orders'))
            for line in self.manufacturing_line_ids:
                product = self.env['sale.order.line'].search(
                    [('order_id', '=', self.sale_order_id.id), ('product_id', '=', line.product_id.id)], limit=1)
                mrp_production_vals = dict()
                mrp_production_vals['inquiry_id'] = self.id
                mrp_production_vals['inquiry_sale_id'] = self.sale_order_id.id
                mrp_production_vals['product_id'] = line.product_id.id
                mrp_production_vals['product_uom_qty'] = line.product_uom_id.id
                mrp_production_vals['product_qty'] = product.product_uom_qty or 1
                try:
                    new_mrp_production = mrp_production_obj.create(mrp_production_vals)
                    self.sale_order_id = None
                except Exception as e:
                    print(e)

        if new_mrp_production and self.tools_supplies_line_ids:
            stock_picking_obj = self.env['stock.picking']
            picking_lines = list()
            for line in self.tools_supplies_line_ids:
                picking_lines.append((0, 0, {
                    'location_id': 8,
                    'location_dest_id': 17,
                    'name': line.product_id.name,
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.product_qty,
                }))
            picking_type = self.env['stock.picking.type'].search([('name', '=', 'Pick Components')], limit=1)
            stock_values = {
                'location_id': 8,
                'location_dest_id': 17,
                'picking_type_id': picking_type.id,
                'move_ids_without_package': picking_lines,
                'inquiry_id': self.id,
                'origin': new_mrp_production.name,
            }
            for line in self.tools_supplies_line_ids:
                stock_move_obj = self.env['stock.move']
                stock_move_vals = {
                    'product_id': line.product_id.id,
                } 
            try:
                stock_picking_obj.create(stock_values)
            except Exception as e:
                print(e)

            for line in self.tools_supplies_line_ids:
                bom_line_vals = {
                    'product_id': line.product_id.id,
                    'name': line.product_id.name,
                    'location_id': 17,
                    'location_dest_id': 15,
                    'product_uom_qty': line.product_qty,
                    'product_uom': line.product_uom_id.id,
                    'picking_type_id': 8,
                }
                try:
                    new_mrp_production.move_raw_ids = [(0, 0, bom_line_vals)]
                except Exception as e:
                    print(e)

    # @api.depends('mrp_eco_ids')
    # def _calc_mrp_eco_count(self):
    #     for rec in self:
    #         rec.mrp_eco_line_count = len(rec.mrp_eco_ids)

    def create_new_plm(self):
        product_obj = self.env['product.template']
        routes = self.env['stock.route'].search([('name', 'in', ['Buy', 'Manufacture'])])
        product_values = {
            'name': self.new_product_name,
            'purchase_ok': False,
            'detailed_type': 'product',
            'route_ids': routes,
        }
        plm_obj = self.env['mrp.eco']
        plm_line_obj = self.env['inquiry.mrp.eco.line']
        try:
            new_product = product_obj.create(product_values)
            plm_values = {
                'name': f'New {self.new_product_name}',
                'product_tmpl_id': new_product.id,
                'stage_id': self.env['mrp.eco.stage'].search([], limit=1).id,
                'type_id': self.env['mrp.eco.type'].search([], limit=1).id,
                'type': 'product',
            }
            new_plm = plm_obj.create(plm_values)
            new_plm_line = plm_line_obj.create({
                'inquiry_id': self.id,
                'mrp_eco_id': new_plm.id,
                'product_id': new_product.id,
            })
        except Exception as e:
            print(e)

    # @api.depends('sale_order_ids')
    # def _compute_rfq_ref_no_date(self):
    #     for rec in self:
    #         sale_order = self.env['sale.order'].search([('inquiry_id', '=', rec.id)], limit=1)
    #         if sale_order:
    #             rec.sale_order_id = sale_order.id
    #             # rec.partner_rfq_ref_no = sale_order.customer_po_no
    #             # rec.partner_rfq_ref_date = sale_order.customer_po_date
    #         else:
    #             rec.sale_order_id = None
    #             # rec.partner_rfq_ref_no = None
    #             # rec.partner_rfq_ref_date = None

    def apply_design_status(self):
        for line in self.design_development_ids:
            line.status = self.design_status
