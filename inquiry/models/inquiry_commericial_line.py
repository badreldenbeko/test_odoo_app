from odoo import fields, models, api


class InquiryCommercial(models.Model):
    _name = 'inquiry.commercial'
    _description = 'Inquiry Commercial'

    name = fields.Char(required=True, translate=True)


class InquiryCommercialLine(models.Model):
    _name = 'inquiry.commercial.line'
    _description = 'Inquiry Commercial Line'

    inquiry_id = fields.Many2one('inquiry.inquiry')
    commercial_id = fields.Many2one('inquiry.commercial', required=True)
    satisfied = fields.Boolean()
    not_satisfied = fields.Boolean()
    comments = fields.Html()

    @api.onchange('satisfied')
    def _change_satisfied(self):
        if self.satisfied:
            if self.not_satisfied:
                self.not_satisfied = False
        else:
            self.not_satisfied = True

    @api.onchange('not_satisfied')
    def _change_not_satisfied(self):
        if self.not_satisfied:
            if self.satisfied:
                self.satisfied = False
        else:
            self.satisfied = True
