from odoo import fields, models, api


class InquiryMrpEcoLine(models.Model):
    _name = 'inquiry.mrp.eco.line'
    _description = 'Inquiry Mrp Eco Line'

    inquiry_id = fields.Many2one('inquiry.inquiry')
    mrp_eco_id = fields.Many2one('mrp.eco')
    product_id = fields.Many2one('product.template')
    state = fields.Many2one('mrp.eco.stage', related='mrp_eco_id.stage_id')
