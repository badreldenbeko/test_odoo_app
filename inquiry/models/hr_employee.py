from odoo import fields, models, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    sign = fields.Binary()
