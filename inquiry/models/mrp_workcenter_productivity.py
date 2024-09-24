from odoo import fields, models, api


class ModelName(models.Model):
    _inherit = 'mrp.workcenter.productivity'

    real_employee_cost = fields.Float(digits='Product Price', compute='_compute_real_employee_cost')
    inquiry_id = fields.Many2one('inquiry.inquiry', compute='_compute_inquiry_id')

    @api.depends('production_id')
    def _compute_inquiry_id(self):
        for rec in self:
            rec.inquiry_id = rec.production_id.inquiry_id or None

    @api.depends('employee_id', 'duration')
    def _compute_real_employee_cost(self):
        for rec in self:
            cost = 0.0
            cost = rec.employee_id.hourly_cost * (rec.duration / 60)
            rec.real_employee_cost = cost
