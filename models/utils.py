from odoo import fields, models, api, _


class InquiryUtils(models.Model):
    _name = 'utils.utils'
    _description = 'Inquiry Utilities'

    def send_notification(self, partner, message_type='success', message_title='Message title',
                          message_body='Message Body Text', sticky=True):
        self.env['bus.bus']._sendone(partner, 'simple_notification', {
            'type': message_type,
            'title': _(message_title),
            'message': _(message_body),
            'sticky': sticky,
        })
        # self.create_notification_record(author, message_title, model, res_id, message_body, author, [partner])

    def send_group_notification(self, author, model, users_group, message_type='success',
                                message_title='Message title',
                                message_body='Message Body Text', sticky=True, link=None):
        if users_group == 'admin':
            group_users = self.env.ref('base.group_system').users
            group_partners = self.env.ref('base.group_system').users.mapped('partner_id')
            for partner in group_partners:
                self.env['bus.bus']._sendone(partner, 'simple_notification', {
                    'type': message_type,
                    'title': _(message_title),
                    'message': _(message_body),
                    'link': link,
                    'sticky': sticky,
                })
        elif users_group == 'sales':
            group_users = self.env.ref('purchase.group_purchase_user').users
            group_partners = self.env.ref('purchase.group_purchase_user').users.mapped('partner_id')
            for partner in group_partners:
                self.env['bus.bus']._sendone(partner, 'simple_notification', {
                    'type': message_type,
                    'title': _(message_title),
                    'message': _(message_body),
                    'link': link,
                    'sticky': sticky,
                })
                # self.create_notification_record(author, message_title, model, res_id, message_body, [author],
                #                             group_users)
        elif users_group == 'purchase':
            group_users = self.env.ref('purchase.group_purchase_user').users
            group_partners = self.env.ref('purchase.group_purchase_user').users.mapped('partner_id')
            for partner in group_partners:
                self.env['bus.bus']._sendone(partner, 'simple_notification', {
                    'type': message_type,
                    'title': _(message_title),
                    'message': _(message_body),
                    'sticky': sticky,
                })
                # self.create_notification_record(author, message_title, model, res_id, message_body, [author],
                #                                 group_users)
        elif users_group == 'manufacturing':
            group_users = self.env.ref('mrp.group_mrp_user').users
            group_partners = self.env.ref('mrp.group_mrp_user').users.mapped('partner_id')
            for partner in group_partners:
                self.env['bus.bus']._sendone(partner, 'simple_notification', {
                    'type': message_type,
                    'title': _(message_title),
                    'message': _(message_body),
                    'sticky': sticky,
                })
                # self.create_notification_record(author, message_title, model, res_id, message_body, [author],
                #                                 group_users)
        elif users_group == 'stock':
            group_users = self.env.ref('stock.group_stock_user').users
            group_partners = self.env.ref('stock.group_stock_user').users.mapped('partner_id')
            for partner in group_partners:
                self.env['bus.bus']._sendone(partner, 'simple_notification', {
                    'type': message_type,
                    'title': _(message_title),
                    'message': _(message_body),
                    'sticky': sticky,
                })
                # self.create_notification_record(author, message_title, model, res_id, message_body, [author],
                #                                 group_users)
        elif users_group == 'qc':
            group_users = self.env.ref('quality.group_quality_user').users
            group_partners = self.env.ref('quality.group_quality_user').users.mapped('partner_id')
            for partner in group_partners:
                self.env['bus.bus']._sendone(partner, 'simple_notification', {
                    'type': message_type,
                    'title': _(message_title),
                    'message': _(message_body),
                    'sticky': sticky,
                })
                # self.create_notification_record(author, message_title, model, res_id, message_body, [author],
                #                                 group_users)

    def create_notification_record(self, author, subject, model, res_id, body, partner_ids,
                                   notification_ids):
        partners = list()
        for partner in notification_ids:
            partners.append((0, 0, {
                'res_partner_id': partner.id,
                'notification_type': 'email',
                'notification_status': 'bounce',
            }))
        message_obj = self.env['mail.message']
        message_values = {
            'subject': subject,
            'author_id': author.id,
            'message_type': 'user_notification',
            'is_internal': True,
            'model': model,
            'res_id': res_id,
            'body': body,
            'partner_ids': self.env['res.partner'].search([('user_ids', 'in', [user.id for user in partner_ids])]),
            'notified_partner_ids': self.env['res.partner'].search([('user_ids', 'in', [user.id for user in partner_ids])]),
            'notification_ids': partners,
        }
        try:
            new_message = message_obj.create(message_values)
            notification_obj = self.env['mail.notification']
            notification_values = {
                'mail_message_id': new_message.id,
                'notification_type': 'email',
                'res_partner_id': author.id,
                'failure_type': 'mail_bounce',
            }
            new_notification = notification_obj.create(notification_values)
            print('Created new notification successfully')
        except Exception as e:
            print(e)
