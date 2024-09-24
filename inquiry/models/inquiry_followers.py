from odoo import fields, models, api, _

ACCEPTANCE_SELECT = [
    ('send', 'Send'),
    ('accept', 'Accept'),
    ('reject', 'Reject'),
]


class InquiryFollowers(models.Model):
    _name = 'inquiry.followers'
    _description = 'Inquiry Followers'

    inquiry_id = fields.Many2one('inquiry.inquiry')
    from_user_id = fields.Many2one('res.users')
    to_user_id = fields.Many2one('res.users', required=True)
    state = fields.Selection(ACCEPTANCE_SELECT, default='send')
    reject_reason = fields.Html()
