from odoo import fields, models, api, _


class InquiryFollowerWizard(models.TransientModel):
    _name = 'inquiry.follower.wizard'
    _description = 'Inquiry Follower Wizard'

    user_id = fields.Many2one('res.users', required=True)

    def add_inquiry_follower(self):
        inquiry_id = self._context.get('inquiry_id')
        inquiry_obj = self.env['inquiry.inquiry'].search([('id', '=', inquiry_id)], limit=1)
        utils = self.env['utils.utils']
        if inquiry_obj and self.user_id:
            old_follow_request = self.env['inquiry.followers'].search(
                [('inquiry_id', '=', inquiry_obj.id), ('to_user_id', '=', self.user_id.id),
                 ('from_user_id', '=', self.env.user.id)], limit=1)
            follow_line_obj = self.env['inquiry.followers']
            follow_line_vals = {
                'inquiry_id': inquiry_obj.id,
                'to_user_id': self.user_id.id,
                'from_user_id': self.env.user.id,
            }
            if old_follow_request:
                # utils.send_notification(partner_id=self.env.user.partner_id, record_id=inquiry_obj.id, message_title='Follow Request',
                #                         message_body=f'You send follow request to {self.user_id.name} for {inquiry_obj.name}')
                return True
            else:
                try:
                    follow_line_obj.create(follow_line_vals)
                    utils.send_notification(self.user_id.partner_id, 'success', 'Follow Request',
                                            f'You have received follow request from {self.env.user.name} for {inquiry_obj.name}')
                    # utils.send_notification(partner_id=self.env.user.partner_id, record_id=inquiry_obj.id, message_title='Follow Request',
                    #                         message_body=f'You successfully send follow request to {self.user_id.name} for {inquiry_obj.name}')
                    return True
                except Exception as e:
                    print(e)
