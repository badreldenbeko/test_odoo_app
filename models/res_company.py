from odoo import fields, models, api, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    fax = fields.Char()
    p_box_no = fields.Char(string=_('P.Box No.'))
