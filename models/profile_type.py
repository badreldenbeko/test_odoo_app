from odoo import fields, models, api, _


class ProfileType(models.Model):
    _name = 'profile.type'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'Profile Type'

    name = fields.Char()
    code = fields.Char(
        string=_("Profile Type"),
        required=True, copy=False,
        index='trigram',
        tracking=True,
        default=lambda self: _('New Profile Type'))

    # @api.model_create_multi
    # def create(self, vals_list):
    #     self.env.registry.clear_cache()
    #     for vals in vals_list:
    #         if not vals.get('code'):
    #             vals['code'] = self.env['ir.sequence'].next_by_code('seq.profile.type') or _("New Profile Type")
    #     res = super(ProfileType, self).create(vals_list)
    #     return res
