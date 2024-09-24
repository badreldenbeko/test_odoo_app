from odoo import fields, models, api


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    heat_no = fields.Char()


class StockLot(models.Model):
    _inherit = 'stock.lot'

    heat_no = fields.Char(compute='_compute_heat_no')

    @api.depends('name')
    def _compute_heat_no(self):
        for rec in self:
            move_line = self.env['stock.move.line'].search([('lot_name', '=', rec.name)], limit=1)
            rec.heat_no = move_line.heat_no
