from odoo import fields, models, api


class BqrOperationLine(models.Model):
    _name = 'bqr.operations.line'
    _description = 'bqr operations line'

    sequence = fields.Integer(default=10)
    inquiry_id = fields.Many2one('inquiry.inquiry')
    bqr_id = fields.Many2one('budgetary.quotation.request')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    operation_id = fields.Many2one('mrp.routing.workcenter')
    name = fields.Char(related='operation_id.name')
    workcenter_id = fields.Many2one('mrp.workcenter', related='operation_id.workcenter_id')
    operation_time = fields.Float(digits='Product_price', compute='_calc_operation_time', store=True)
    employee_ratio = fields.Float(compute='_compute_employee_ratio', store=True)
    workcenter_cost = fields.Float(digits='Product_price', compute='_calc_costs', store=True)
    total_workcenter_cost = fields.Float(digits='Product_price', compute='_calc_costs', store=True)
    employee_cost = fields.Float(digits='Product_price', compute='_calc_costs', store=True)
    total_employee_cost = fields.Float(digits='Product_price', compute='_calc_costs', store=True)
    total_cost = fields.Float(digits='Product_price', compute='_calc_costs', store=True)
    margin = fields.Float(digits='Product_price')
    after_margin = fields.Float(digits='Product_price', compute='_calc_after_margin', store=True)
    quantity = fields.Float(digits='Product_price', compute='_calc_quantity_price_after_margin')
    quantity_price_after_margin = fields.Float(compute='_calc_quantity_price_after_margin')

    @api.depends('operation_id')
    def _compute_employee_ratio(self):
        for rec in self:
            rec.employee_ratio = rec.operation_id.employee_ratio

    @api.depends('operation_id')
    def _calc_costs(self):
        for rec in self:
            min_cost = rec.operation_id.workcenter_id.costs_hour / 60
            rec.workcenter_cost = min_cost * (
                    rec.operation_id.time_cycle_manual + rec.workcenter_id.time_start + rec.workcenter_id.time_stop)
            rec.total_workcenter_cost = rec.workcenter_cost * rec.quantity
            emp_min_cost = (rec.operation_id.employee_ratio * rec.operation_id.workcenter_id.employee_costs_hour) / 60
            rec.employee_cost = emp_min_cost * (
                    rec.operation_id.time_cycle_manual + rec.workcenter_id.time_start + rec.workcenter_id.time_stop)
            rec.total_employee_cost = rec.employee_cost * rec.quantity
            rec.total_cost = rec.workcenter_cost + rec.employee_cost

    @api.depends('operation_id')
    def _calc_operation_time(self):
        for rec in self:
            rec.operation_time = rec.operation_id.time_cycle_manual + rec.workcenter_id.time_start + rec.workcenter_id.time_stop

    @api.depends('bqr_id.o_margin_type', 'total_cost', 'bqr_id.o_margin')
    def _calc_after_margin(self):
        for rec in self:
            price_after_margin = 0.0
            if rec.bqr_id.o_margin_type == 'percentage':
                price_after_margin = rec.total_cost + (rec.total_cost * rec.bqr_id.o_margin / 100)
            elif rec.bqr_id.o_margin_type == 'amount':
                price_after_margin = rec.total_cost + rec.bqr_id.o_margin
            rec.after_margin = price_after_margin

    @api.depends('bqr_id.bqr_service_consumable_ids', 'bqr_id.bqr_semi_finished_product_ids',
                 'bqr_id.bqr_manufacturing_product_ids', 'quantity', 'after_margin')
    def _calc_quantity_price_after_margin(self):
        for rec in self:
            quantity = 0.0
            quantity_price_after_margin = 0.0
            if rec.bqr_id.bqr_service_consumable_ids:
                for line in rec.bqr_id.bqr_service_consumable_ids:
                    bom_obj = self.env['mrp.bom'].search([('product_tmpl_id', '=', line.product_id.product_tmpl_id.id)],
                                                         limit=1)
                    if rec.operation_id.id in bom_obj.operation_ids.ids:
                        quantity = line.product_qty
                        quantity_price_after_margin = rec.after_margin * line.product_qty
            if rec.bqr_id.bqr_semi_finished_product_ids:
                for line in rec.bqr_id.bqr_semi_finished_product_ids:
                    bom_obj = self.env['mrp.bom'].search([('product_tmpl_id', '=', line.product_id.product_tmpl_id.id)],
                                                         limit=1)
                    if rec.operation_id.id in bom_obj.operation_ids.ids:
                        print(bom_obj)
                        quantity = line.product_qty
                        quantity_price_after_margin = rec.after_margin * line.product_qty
            if rec.bqr_id.bqr_manufacturing_product_ids:
                for line in rec.bqr_id.bqr_manufacturing_product_ids:
                    bom_obj = self.env['mrp.bom'].search([('product_tmpl_id', '=', line.product_id.product_tmpl_id.id)],
                                                         limit=1)
                    if rec.operation_id.id in bom_obj.operation_ids.ids:
                        quantity = line.product_qty
                        quantity_price_after_margin = rec.after_margin * line.product_qty
            rec.quantity = quantity
            rec.quantity_price_after_margin = quantity_price_after_margin
