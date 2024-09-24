from odoo import fields, models, api, _


class ProductCategory(models.Model):
    _inherit = 'product.category'

    code = fields.Char(index=True)
    is_tool_supply = fields.Boolean(_('Tool Or Supply'))
