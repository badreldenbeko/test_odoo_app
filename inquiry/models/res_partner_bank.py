from odoo import fields, models, api, _


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    branch = fields.Char(string=_('Branch'))
    swift = fields.Char(string=_('SWIFT / IBAN'))
