from odoo import fields, models, api, _


class BqrOverHead(models.Model):
    _name = 'bqr.overhead'
    _description = 'BQR Overhead Category'

    name = fields.Char(required=True)


class BqrOverheadLine(models.Model):
    _name = 'bqr.overhead.line'
    _description = 'BQR overhead line'

    bqr_id = fields.Many2one('budgetary.quotation.request')
    bqr_overhead_id = fields.Many2one('bqr.overhead', string=_('Overhead Category'), required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    amount = fields.Float(digits='Product Price')
