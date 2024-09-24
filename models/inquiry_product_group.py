from odoo import fields, models, api, _


class InquiryProductGroup(models.Model):
    _name = 'inquiry.product.group'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'Product Group'

    name = fields.Char(required=True)
    code = fields.Char(
        string=_("Group"),
        required=True, copy=False,
        index='trigram',
        tracking=True,
        default=lambda self: _('New Group'))

    # @api.model_create_multi
    # def create(self, vals_list):
    #     self.env.registry.clear_cache()
    #     for vals in vals_list:
    #         if not vals.get('code'):
    #             vals['code'] = self.env['ir.sequence'].next_by_code('seq.inquiry.product.group') or _("New Group")
    #     res = super(InquiryProductGroup, self).create(vals_list)
    #     return res


class InquiryProductFamily(models.Model):
    _name = 'inquiry.product.family'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'Product Family'

    name = fields.Char(required=True)
    code = fields.Char(
        string=_("Family"),
        required=True, copy=False,
        index='trigram',
        tracking=True,
        default=lambda self: _('New Family'))

    # @api.model_create_multi
    # def create(self, vals_list):
    #     self.env.registry.clear_cache()
    #     for vals in vals_list:
    #         if not vals.get('code'):
    #             vals['code'] = self.env['ir.sequence'].next_by_code('seq.inquiry.product.family') or _("New Family")
    #     res = super(InquiryProductFamily, self).create(vals_list)
    #     return res


class OtherSizeDetails(models.Model):
    _name = 'other.size.details'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'Other Size Details'

    name = fields.Char(required=True)
    code = fields.Char(
        string=_("Other Size Details"),
        required=True, copy=False,
        index='trigram',
        tracking=True,
        default=lambda self: _('New Other Size Details'))

    # /
