from odoo import fields, models, api


class InquiryQaQc(models.Model):
    _name = 'inquiry.qa.qc'
    _description = 'Inquiry QA/Qc'

    name = fields.Char(required=True, translate=True)


class InquiryQaQcLine(models.Model):
    _name = 'inquiry.qa.qc.line'
    _description = 'Inquiry QA/Qc Line'

    inquiry_id = fields.Many2one('inquiry.inquiry')
    qa_qc_id = fields.Many2one('inquiry.qa.qc')
    status = fields.Boolean()
    comments = fields.Html()
