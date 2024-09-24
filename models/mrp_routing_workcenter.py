from odoo import fields, models, api, _


class MrpRoutingWorkcenter(models.Model):
    _inherit = 'mrp.routing.workcenter'
    _description = 'Mrp Routing Workcenter'

    responsible = fields.Many2one('hr.employee', string=_('Responsible Employer'))
    department_id = fields.Many2one('hr.department')
    drawing_no = fields.Char()

    work_instructions = fields.Char()
    acceptance_criteria = fields.Char()
    qc_intervention = fields.Char()
