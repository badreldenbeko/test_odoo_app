from odoo import fields, models, api, _


class MaterialGrade(models.Model):
    _name = 'material.grade'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'Material Grade'

    name = fields.Char(required=True)
    code = fields.Char(
        string=_("Material Grade"),
        required=True, copy=False,
        index='trigram',
        tracking=True,
        default=lambda self: _('New Material Grade'))

    # @api.model_create_multi
    # def create(self, vals_list):
    #     self.env.registry.clear_cache()
    #     for vals in vals_list:
    #         if not vals.get('code'):
    #             vals['code'] = self.env['ir.sequence'].next_by_code('seq.material.grade') or _("New Material Grade")
    #     res = super(MaterialGrade, self).create(vals_list)
    #     return res
