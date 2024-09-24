from odoo import fields, models, api
from collections import defaultdict


class InquiryMachineryLine(models.Model):
    _name = 'inquiry.machinery.line'
    _inherit = 'inquiry.tools.supplies'
    _description = 'inquiry machinery line'

    product_id = fields.Many2one('product.template', domain="[('is_machinery', '=', True)]", string='Machine')
    remarks = fields.Html()

    def _compute_grouped_lines(self):
        grouped_lines = defaultdict(lambda: self.env['inquiry.machinery.line'])
        return grouped_lines
