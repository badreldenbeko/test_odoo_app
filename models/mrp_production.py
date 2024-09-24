import datetime

from odoo import fields, models, api, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    inquiry_id = fields.Many2one('inquiry.inquiry')
    inquiry_sale_id = fields.Many2one('sale.order', required=False)
    specification_to_follow = fields.Html()
    report_comment = fields.Html(string=_('Comment'))

    total_operations_employee_cost = fields.Float(compute='_compute_total_operations_employee_cost',
                                                    digits='Product Price')
    total_operations_workcenter_cost = fields.Float(compute='_compute_total_operations_workcenter_cost',
                                                      digits='Product Price')
    total_operation_cost = fields.Float(compute='_compute_total_operation_cost', digits='Product Price')

    @api.depends('workorder_ids')
    def _compute_total_operation_cost(self):
        for rec in self:
            rec.total_operation_cost = rec.total_operations_employee_cost + rec.total_operations_workcenter_cost

    @api.depends('workorder_ids')
    def _compute_total_operations_employee_cost(self):
        for rec in self:
            rec.total_operations_employee_cost = sum(rec.workorder_ids.mapped('total_employee_cost'))

    @api.depends('workorder_ids')
    def _compute_total_operations_workcenter_cost(self):
        for rec in self:
            rec.total_operations_workcenter_cost = sum(rec.workorder_ids.mapped('workcenter_cost'))

    @api.depends('inquiry_id')
    def _compute_analytic_distribution(self):
        for line in self:
            if line.inquiry_id:
                line.analytic_distribution = {str(line.inquiry_id.analytic_account_id.id): 100.0}

    def button_mark_done(self):
        res = super(MrpProduction, self).button_mark_done()
        utils = self.env['utils.utils']
        if self.inquiry_id:
            for partner in self.inquiry_id.inquiry_followers_ids.mapped('to_user_id').mapped('partner_id'):
                utils.send_notification(self.env.user, partner, 'mrp.production', self.id, 'success',
                                        f'Work order Finished',
                                        f'Work order {self.name} Finished')
        utils.send_group_notification(self.env.user, 'mrp.production', self.id, 'stock',
                                      'success',
                                      'Work order Finished', f'Work order {self.name} Finished')


        dt_obj = datetime.datetime.strptime(str(self.date_finished), "%Y-%m-%d %H:%M:%S")
        date_obj = dt_obj.date()
        new_account_vals = {
            'name': f'[WC] {self.name} - Manpower Cost',
            'amount': self.total_operations_employee_cost * -1,
            'ref': self.name,
            'x_plan7_id': self.inquiry_id.analytic_account_id.id,
            'date': date_obj,
            'unit_amount': 1,
        }
        try:
            new_account = self.env['account.analytic.line'].create(new_account_vals)
            zero_line = self.env['account.analytic.line'].search([('name', '=', new_account.name), ('amount', '=', 0)],
                                                                 limit=1)
            if zero_line:
                zero_line.unlink()
        except Exception as e:
            print(e)
        return res
