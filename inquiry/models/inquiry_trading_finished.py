from datetime import timedelta
from odoo import fields, models, api, _
from collections import defaultdict
from odoo.exceptions import UserError


class InquiryTradingFinished(models.Model):
    _name = 'inquiry.trading.finished.line'
    _inherit = 'inquiry.tools.supplies'
    _description = 'inquiry trading finished line'

    product_id = fields.Many2one('product.product', string="Product", change_default=True, ondelete='restrict',
                                 index='btree_not_null',
                                 domain="[('detailed_type', '=', 'product'), ('sale_ok', '=', True), ('purchase_ok', '=', True), ('product_tmpl_id.is_semi_finish', '=', False)]")

    total_standard_price = fields.Float(string=_('Total Cost'), digits='Product Price', compute='_calc_prices')
    price_with_margin = fields.Float(string=_('Price Margin'), digits='Product Price', compute='_calc_prices')
    total_price_margin = fields.Float(string=_('Sale Price'), digits='Product Price', compute='_calc_prices')
    margin = fields.Float(string=_('Extra Margin'), digits='Product Price')
    margin_type = fields.Selection(
        selection=[
            ('percentage', _("Percentage")),
            ('amount', _("Amount")),
        ],
        related='inquiry_id.margin_type')
    margin_simple = fields.Char(default=lambda self: self.env.company.currency_id.symbol, compute='_calc_margin_simple')
    price_with_extra_margin = fields.Float(string=_('Price With Extra Margin'), digits='Product Price',
                                           compute='_calc_extra_margin')
    total_with_extra_margin = fields.Float(string=_('Total With Extra Margin'), digits='Product Price',
                                           compute='_calc_extra_margin')

    @api.depends('inquiry_id')
    def _calc_prices(self):
        for rec in self:
            cost = 0.0
            total_cost = 0.0
            price_with_margin = 0.0
            total_price_margin = 0.0
            rec.standard_price = 0.0
            rec.total_standard_price = 0.0
            rec.price_with_margin = 0.0
            rec.total_price_margin = 0.0
            bqr_obj = self.env['budgetary.quotation.request'].search(
                [('inquiry_id', '=', rec.inquiry_id.id), ('state', '=', 'confirmed')], limit=1)
            if bqr_obj:
                for line in bqr_obj.bqr_finished_product_ids:
                    if rec.product_id.id == line.product_id.id:
                        cost += line.standard_price
                        total_cost += line.total_standard_price
                        price_with_margin += line.price_after_margin
                        total_price_margin += line.total_price_after_margin
            rec.standard_price = cost
            rec.total_standard_price = total_cost
            rec.price_with_margin = price_with_margin
            rec.total_price_margin = total_price_margin

    @api.depends('inquiry_id', 'price_with_margin', 'margin')
    def _calc_extra_margin(self):
        for rec in self:
            rec.price_with_extra_margin = 0.0
            rec.total_with_extra_margin = 0.0
            if rec.margin_type == 'amount':
                rec.price_with_extra_margin = rec.price_with_margin + rec.margin
            else:
                rec.price_with_extra_margin = rec.price_with_margin + (rec.margin * rec.price_with_margin / 100)
            rec.total_with_extra_margin = rec.price_with_extra_margin * rec.product_qty

    @api.depends('margin_type')
    def _calc_margin_simple(self):
        for rec in self:
            if rec.margin_type == 'amount':
                rec.margin_simple = rec.env.company.currency_id.symbol
            else:
                rec.margin_simple = '%'

    def _compute_grouped_lines(self):
        grouped_lines = defaultdict(lambda: self.env['inquiry.trading.finished.line'])
        return grouped_lines


class InquiryTradingSemiFinished(models.Model):
    _name = 'inquiry.trading.semi.finished.line'
    _inherit = 'inquiry.tools.supplies'
    _description = 'inquiry.trading.semi.finished.line'

    product_id = fields.Many2one('product.product', string="Product", change_default=True, ondelete='restrict',
                                 index='btree_not_null',
                                 domain="[('detailed_type', '=', 'product'), ('sale_ok', '=', True), ('purchase_ok', '=', True), ('product_tmpl_id.is_semi_finish', '=', True)]")

    total_standard_price = fields.Float(string=_('Total Cost'), digits='Product Price', compute='_calc_prices')
    price_with_margin = fields.Float(string=_('Price Margin'), digits='Product Price', compute='_calc_prices')
    total_price_margin = fields.Float(string=_('Sale Price'), digits='Product Price', compute='_calc_prices')
    margin = fields.Float(string=_('Extra Margin'), digits='Product Price')
    margin_type = fields.Selection(
        selection=[
            ('percentage', _("Percentage")),
            ('amount', _("Amount")),
        ],
        related='inquiry_id.margin_type')
    margin_simple = fields.Char(default=lambda self: self.env.company.currency_id.symbol, compute='_calc_margin_simple')
    price_with_extra_margin = fields.Float(string=_('Price With Extra Margin'), digits='Product Price',
                                           compute='_calc_extra_margin')
    total_with_extra_margin = fields.Float(string=_('Total With Extra Margin'), digits='Product Price',
                                           compute='_calc_extra_margin')

    @api.depends('inquiry_id')
    def _calc_prices(self):
        for rec in self:
            cost = 0.0
            total_cost = 0.0
            price_with_margin = 0.0
            total_price_margin = 0.0
            rec.standard_price = 0.0
            rec.total_standard_price = 0.0
            rec.price_with_margin = 0.0
            rec.total_price_margin = 0.0
            bqr_obj = self.env['budgetary.quotation.request'].search(
                [('inquiry_id', '=', rec.inquiry_id.id), ('state', '=', 'confirmed')], limit=1)
            if bqr_obj:
                for line in bqr_obj.bqr_semi_finished_product_ids:
                    if line.product_id.id == line.product_id.id:
                        cost += line.standard_price
                        total_cost += line.total_standard_price
                        price_with_margin += line.price_after_margin
                        total_price_margin += line.total_price_after_margin
            rec.standard_price = cost
            rec.total_standard_price = total_cost
            rec.price_with_margin = price_with_margin
            rec.total_price_margin = total_price_margin

    @api.depends('inquiry_id', 'price_with_margin', 'margin')
    def _calc_extra_margin(self):
        for rec in self:
            rec.price_with_extra_margin = 0.0
            rec.total_with_extra_margin = 0.0
            if rec.margin_type == 'amount':
                rec.price_with_extra_margin = rec.price_with_margin + rec.margin
            else:
                rec.price_with_extra_margin = rec.price_with_margin + (rec.margin * rec.price_with_margin / 100)
            rec.total_with_extra_margin = rec.price_with_extra_margin * rec.product_qty

    @api.depends('margin_type')
    def _calc_margin_simple(self):
        for rec in self:
            if rec.margin_type == 'amount':
                rec.margin_simple = rec.env.company.currency_id.symbol
            else:
                rec.margin_simple = '%'

    def _compute_grouped_lines(self):
        grouped_lines = defaultdict(lambda: self.env['inquiry.trading.semi.finished.line'])
        return grouped_lines
