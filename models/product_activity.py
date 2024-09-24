from odoo import fields, models, api, _


class ProductActivity(models.Model):
    _name = 'product.activity'
    _description = 'Product Activity'

    product_id = fields.Many2one('product.template')
    serial = fields.Integer(default=1)
    activity_description = fields.Char()
    characteristics = fields.Char(string=_('Characteristics to be verified'))
    reference_document = fields.Char(string=_('Reference Document & Acceptance Standard/Criteria'))
    verifying_document = fields.Char(string=_('Verifying Document / Record'))
    qa_qc = fields.Char(string=_('DOT QA/QC'))
    wft = fields.Char()

