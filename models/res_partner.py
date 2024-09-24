from collections import defaultdict

from odoo import fields, models, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    code = fields.Char(
        required=True, copy=False, readonly=True,
        index='trigram',
        tracking=True,
        default=lambda self: _('New Partner'))
    fax = fields.Char(string=_('Fax'))
    landed_cost = fields.Float(string=_('Landed Cost'), widget='percentage')
    p_box_no = fields.Char(string=_('P.Box No.'))
    registration_id = fields.Many2one('vendor.registration')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('code', _("New Partner")) == _("New Partner"):
                if vals.get('supplier_rank'):
                    vals['code'] = self.env['ir.sequence'].next_by_code('seq.vendor.code') or _("New Partner")
                else:
                    vals['code'] = self.env['ir.sequence'].next_by_code('seq.customer.code') or _("New Partner")
        return super().create(vals_list)
    # Vendor Report Fields

    def _prepare_display_address(self, without_company=False):
        # get the information that will be injected into the display format
        # get the address format
        address_format = self._get_address_format()
        args = defaultdict(str, {
            'state_code': self.state_id.code or '',
            'state_name': self.state_id.name or '',
            'country_code': self.country_id.code or '',
            'country_name': self._get_country_name(),
            'company_name': self.commercial_company_name or '',
        })
        for field in self._formatting_address_fields():
            args[field] = getattr(self, field) or ''
        if without_company:
            args['company_name'] = ''
        elif self.commercial_company_name:
            # address_format = '%(company_name)s\n' + address_format
            address_format = address_format
        return address_format, args
