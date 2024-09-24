from odoo import fields, models, api, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    material_grade_id = fields.Many2one('material.grade')
    profile_type_id = fields.Many2one('profile.type')
    service_consumable_ids = fields.One2many('service.consumable', 'product_id')
    service_consumable_count = fields.Integer(compute='_compute_service_consumable_count')
    is_semi_finish = fields.Boolean(default=False)
    is_machinery = fields.Boolean(default=False)
    product_activity_ids = fields.One2many('product.activity', 'product_id')
    tc_number = fields.Char()
    drawing_no = fields.Char()

    # new fields
    gr = fields.Many2one('inquiry.product.group', string=_('Group'))
    inquiry_family = fields.Many2one('inquiry.product.family')
    outside_dia = fields.Char()
    inside_dia = fields.Char()
    height = fields.Float(digits='Product Price')
    thickness = fields.Float(digits='Product Price')
    inch_dia = fields.Float(digits='Product Price')
    # other_size_details = fields.Char()
    other_size_details = fields.Many2one('other.size.details')
    extended_price_sar = fields.Float(digits='Product Price')
    machine_name = fields.Char()
    manufacturer_part_number = fields.Char()
    manufacturer_name = fields.Char()
    asset_number = fields.Char()
    remarks = fields.Html()
    control_number = fields.Integer()
    dots_product_code = fields.Char(string=_('Product Code'))
    # default_code = fields.Char(compute='_compute_dots_product_code', index=True)

    # @api.depends('categ_id', 'inquiry_family', 'material_grade_id', 'other_size_details')
    # def _compute_dots_product_code(self):
    #     for rec in self:
    #         code = ''
    #         code += rec.categ_id.code or ''
    #         code += rec.inquiry_family.code or ''
    #         code += rec.material_grade_id.code or ''
    #         code += rec.other_size_details.code or ''
    #         rec.dots_product_code = code
            # rec.default_code = code

    def _compute_service_consumable_count(self):
        for product in self:
            product.service_consumable_count = len(product.service_consumable_ids)

    def open_service_consumable_view(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'service.consumable',
            'name': 'Service Consumables',
            'view_mode': 'tree,form',
            'domain': [('product_id', '=', self.id)],
            'context': {'default_product_id': self.id},
            'target': 'current',
        }
