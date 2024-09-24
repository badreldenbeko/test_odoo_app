from odoo import fields, models, api


class InitialReview(models.Model):
    _name = 'initial.review'
    _description = 'Initial review'

    name = fields.Char(required=True, translate=True)


class InitialReviewLine(models.Model):
    _name = 'initial.review.line'
    _description = 'Initial review line'

    STATUS_SELECTION = [
        ('y', '(Y) - "Reviewed and found"'),
        ('n', '(N) - "Requirement cannot be met"'),
        ('na', '(N/A) - "Not applicable"'),
    ]

    inquiry_id = fields.Many2one('inquiry.inquiry', required=True)
    initial_review_id = fields.Many2one('initial.review', required=True)
    status = fields.Selection(STATUS_SELECTION)

    def reset_review(self):
        self.status = None
        return True
