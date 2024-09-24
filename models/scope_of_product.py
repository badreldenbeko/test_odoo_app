from odoo import fields, models, api, _


class ScopeOfProduct(models.Model):
    _name = 'scope.of.product'
    _description = 'Scope of product'

    name = fields.Char(required=True, translate=True)


class ScopeOfProductLine(models.Model):
    _name = 'scope.of.product.line'
    _description = 'Scope of product line'

    inquiry_id = fields.Many2one('inquiry.inquiry')
    scope_of_product_id = fields.Many2one('scope.of.product')
    is_checked = fields.Boolean()
