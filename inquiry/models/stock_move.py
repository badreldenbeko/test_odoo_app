from odoo import fields, models, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    tools_supply_line_id = fields.Many2one('inquiry.tools.supplies')
    service_id = fields.Many2one('product.template', compute='_compute_service')

    @api.depends('product_id')
    def _compute_service(self):
        for rec in self:
            service = None
            consumable_line = self.env['consumable.line'].search(
                [('product_id', '=', rec.product_id.product_tmpl_id.id)], limit=1)
            if consumable_line:
                service = consumable_line.service_consumable_id.product_id.id
            rec.service_id = service
