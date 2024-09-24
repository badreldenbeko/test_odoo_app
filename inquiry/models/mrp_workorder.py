from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    responsible = fields.Many2one('hr.employee', string=_('Responsible Employer'))
    department_id = fields.Many2one('hr.department', related='operation_id.department_id')
    drawing_no = fields.Char(compute='_compute_responsible_drawing_no')
    work_instructions = fields.Char(compute='_compute_responsible_drawing_no')
    acceptance_criteria = fields.Char(compute='_compute_responsible_drawing_no')
    qc_intervention = fields.Char(compute='_compute_responsible_drawing_no')

    acc_rej = fields.Boolean(default=False, compute='_compute_acc_rej')
    acc_rej_emp = fields.Many2one('hr.employee', compute='_compute_acc_rej_emp')

    acc_remarks = fields.Char()

    inquiry_id = fields.Many2one('inquiry.inquiry', compute='_compute_inquiry_id')

    employee_count = fields.Integer(compute='_compute_employee_count')
    total_employee_cost = fields.Float(compute='_compute_total_employee_cost', digits='Product Price')
    workcenter_cost = fields.Float(compute='_compute_workcenter_cost', digits='Product Price')
    total_cost = fields.Float(compute='_compute_total_cost', digits='Product Price')
    inquiry_sale_id = fields.Many2one('sale.order', compute='_compute_inquiry_sale_id')

    @api.depends('production_id')
    def _compute_inquiry_sale_id(self):
        for rec in self:
            rec.inquiry_sale_id = rec.production_id.inquiry_sale_id or None

    @api.depends('time_ids')
    def _compute_employee_count(self):
        for rec in self:
            rec.employee_count = (len(rec.time_ids))

    @api.depends('total_employee_cost', 'workcenter_cost')
    def _compute_total_cost(self):
        for rec in self:
            rec.total_cost = rec.total_employee_cost + rec.workcenter_cost

    @api.depends('time_ids')
    def _compute_total_employee_cost(self):
        for rec in self:
            cost = 0.0
            for line in rec.time_ids:
                cost += line.real_employee_cost
            rec.total_employee_cost = cost

    @api.depends('workcenter_id')
    def _compute_workcenter_cost(self):
        for rec in self:
            rec.workcenter_cost = (rec.duration / 60) * rec.workcenter_id.costs_hour

    @api.depends('production_id')
    def _compute_inquiry_id(self):
        for rec in self:
            rec.inquiry_id = rec.production_id.inquiry_id or None

    @api.depends('name')
    def _compute_responsible_drawing_no(self):
        for rec in self:
            # rec.responsible = rec.operation_id.responsible.id or None
            rec.drawing_no = rec.operation_id.drawing_no or None
            rec.work_instructions = rec.operation_id.work_instructions or None
            rec.acceptance_criteria = rec.operation_id.acceptance_criteria or None
            rec.qc_intervention = rec.operation_id.qc_intervention or None

    def button_start(self):
        if len(self.time_ids) >= self.operation_id.employee_ratio:
            raise ValidationError(_('No More Employees Can Start'))
        for line in self.blocked_by_workorder_ids:
            if line.progress < 100:
                raise ValidationError(_(f'There is a dependency operation not finished.'))
        return super(MrpWorkorder, self).button_start()

    @api.depends('blocked_by_workorder_ids')
    def _compute_acc_rej(self):
        for rec in self:
            if rec.blocked_by_workorder_ids:
                rec.acc_rej = True
            else:
                rec.acc_rej = False

    @api.depends('time_ids')
    def _compute_acc_rej_emp(self):
        for rec in self:
            if rec.time_ids:
                rec.acc_rej_emp = rec.time_ids[0].user_id.id
            else:
                rec.acc_rej_emp = None
