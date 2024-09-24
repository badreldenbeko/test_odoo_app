from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class StockPiking(models.Model):
    _inherit = 'stock.picking'

    inquiry_id = fields.Many2one('inquiry.inquiry', required=False, tracking=True)
    inquiry_sale_id = fields.Many2one('sale.order', required=False, tracking=True)
    bqr_id = fields.Many2one('budgetary.quotation.request', required=False, tracking=True)
    por_id = fields.Many2one('purchase.order.request', required=False, tracking=True)

    driver_name = fields.Char()
    driver_mobile = fields.Char()
    driver_id = fields.Char(string=_('Driver ID'), tracking=True)
    driver_comments = fields.Char(string=_('Comments'), tracking=True)
    truck_no = fields.Char(tracking=True)
    well_no = fields.Char(tracking=True)

    shipping_by_name = fields.Char(tracking=True)
    shipping_by_id = fields.Char(tracking=True)

    received_by = fields.Char(tracking=True)
    received_date = fields.Datetime(tracking=True)

    location_checked = fields.Boolean(tracking=True, string='I Check Quantity & Location', help=_('mark this after check the quantity and locations'))

    def create(self, vals_list):
        res = super(StockPiking, self).create(vals_list)
        # if self.location_id.name == 'Receipts':
        utils = self.env['utils.utils']
        utils.send_group_notification(self.env.user, 'stock.picking', 'qc',
                                      'warning',
                                      'Receipt Created', f'New Receipt {res.name} Created')
        return res

    def button_validate(self):
        if not self.location_checked:
            raise ValidationError(_(f'Please Check the quantity and the locations and mark it as checked'))
        return super().button_validate()
