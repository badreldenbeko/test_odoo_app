from odoo import fields, models, api


class MrpEco(models.Model):
    _inherit = 'mrp.eco'

    inquiry_id = fields.Many2one('inquiry.inquiry')

    def approve(self):
        res = super(MrpEco, self).approve()
        utils = self.env['utils.utils']
        utils.send_group_notification(self.env.user, 'mrp.eco', self.id, 'sales',
                                      'success',
                                      'Effective', f'New effective product {self.name}')
        utils.send_group_notification(self.env.user, 'mrp.eco', self.id, 'purchase',
                                      'success',
                                      'Effective', f'New effective product {self.name}')
        utils.send_group_notification(self.env.user, 'mrp.eco', self.id, 'stock',
                                      'success',
                                      'Effective', f'New effective product {self.name}')
        utils.send_group_notification(self.env.user, 'mrp.eco', self.id, 'manufacturing',
                                      'success',
                                      'Effective', f'New effective product {self.name}')
        utils.send_group_notification(self.env.user, 'mrp.eco', self.id, 'plm',
                                      'success',
                                      'Effective', f'New effective product {self.name}')
        return res