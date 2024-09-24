from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ServiceConsumable(models.Model):
    _name = 'service.consumable'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'Service Consumable'

    sequence = fields.Integer("Sequence", default=10)
    name = fields.Char(
        required=True, copy=False, readonly=True,
        index='trigram',
        tracking=True,
        default=lambda self: _('New Service Consumable'))
    product_id = fields.Many2one('product.template', required=True)
    consumable_line_ids = fields.One2many('consumable.line', 'service_consumable_id')

    @api.model_create_multi
    def create(self, vals_list):
        self.env.registry.clear_cache()
        for vals in vals_list:
            if not vals.get('name') and vals.get('product_id'):
                product = self.env['product.template'].search([('id', '=', vals.get('product_id'))], limit=1)
                product_name = product.name if product else "Product-"
                vals['name'] = product_name + '-' + self.env['ir.sequence'].next_by_code('seq.service.consumable') or _(
                    "New Service Consumable")
        res = super().create(vals_list)
        return res

    # @api.onchange('consumable_line_ids')
    # def _change_consumable_line_ids(self):
    #     for line in self.consumable_line_ids:
    #         if line.product_uom_id.category_id != line.product_id.uom_id.category_id:
    #             raise ValidationError(
    #                 _(f'Consumable Uom "{line.product_uom_id.name}" Not Match Consumable Line Uom "{line.product_id.uom_id.name}"'))


class ConsumableLine(models.Model):
    _name = 'consumable.line'
    _description = 'Consumable Line'

    sequence = fields.Integer("Sequence", default=10)
    service_consumable_id = fields.Many2one('service.consumable', required=True)
    product_id = fields.Many2one('product.template', domain=[('detailed_type', 'in', ['product'])])
    product_uom_category_id = fields.Many2one('uom.category', related='product_id.uom_id.category_id')
    product_uom_id = fields.Many2one('uom.uom', required=True, domain="[('category_id', '=', product_uom_category_id)]")
    product_qty = fields.Float(required=True)
