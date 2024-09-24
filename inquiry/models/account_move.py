from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    sale_order_id = fields.Many2one('sale.order')
    stock_picking_id = fields.Many2one('stock.picking')

    def action_post(self):
        res = super(AccountMove, self).action_post()
        if self.partner_id.country_id.name != 'Saudi Arabia':
            if self.partner_id.landed_cost > 0:
                landed_obj = self.env['stock.landed.cost']
                landed_lines = list()
                for line in self.invoice_line_ids:
                    landed_lines.append((0, 0, {
                        'product_id': line.product_id.id,
                        'price_unit': line.price_subtotal * self.partner_id.landed_cost,
                        'split_method': 'equal',
                    }))
                new_landed_values = {
                    'vendor_bill_id': self.id,
                    'cost_lines': landed_lines,
                }
                new_landed_obj = landed_obj.create(new_landed_values)
        return res
