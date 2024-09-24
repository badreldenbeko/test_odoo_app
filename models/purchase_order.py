from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class PurchaseManagerApprovals(models.Model):
    _name = 'purchase.manager.approvals'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'Purchase Manager approvals'

    name = fields.Char(required=True)
    first_lvl_amount = fields.Float(digits='Product Price', tracking=True, required=True)
    second_lvl_amount = fields.Float(digits='Product Price', tracking=True, required=True)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    inquiry_id = fields.Many2one('inquiry.inquiry')
    bqr_id = fields.Many2one('budgetary.quotation.request', string=_('Costing'))
    por_id = fields.Many2one('purchase.order.request', string=_('Purchase Request'))
    mode_of_shipping = fields.Char()

    manager_approved = fields.Boolean(copy=False)
    general_manager_approved = fields.Boolean(copy=False)
    approvals_id = fields.Many2one('purchase.manager.approvals')

    def inquiry_manager_approve(self):
        self.manager_approved = True
        utils = self.env['utils.utils']
        utils.send_group_notification(self.env.user, 'purchase.order', self.id, 'admin',
                                      'warning',
                                      'Purchase Approve',
                                      f'PO {self.name} Need Confirmation')

    def inquiry_general_manager_approve(self):
        self.general_manager_approved = True

    def button_confirm(self):
        if self.amount_total >= self.approvals_id.first_lvl_amount and self.amount_total < self.approvals_id.second_lvl_amount and not self.manager_approved:
            raise ValidationError(_(f'Manager Not Approved'))
        if self.amount_total >= self.approvals_id.second_lvl_amount and not self.general_manager_approved:
            raise ValidationError(_(f'General Manager Not Approved'))
        res = super(PurchaseOrder, self).button_confirm()
        return res

    def button_cancel(self):
        res = super(PurchaseOrder, self).button_cancel()
        self.manager_approved = False
        self.general_manager_approved = False
        return res


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    inquiry_id = fields.Many2one('inquiry.inquiry', related='order_id.inquiry_id')

    @api.depends('product_id', 'order_id.partner_id')
    def _compute_analytic_distribution(self):
        for line in self:
            if not line.display_type:
                distribution = self.env['account.analytic.distribution.model']._get_distribution({
                    "product_id": line.product_id.id,
                    "product_categ_id": line.product_id.categ_id.id,
                    "partner_id": line.order_id.partner_id.id,
                    "partner_category_id": line.order_id.partner_id.category_id.ids,
                    "company_id": line.company_id.id,
                })
                line.analytic_distribution = distribution or line.analytic_distribution
            if line.inquiry_id:
                line.analytic_distribution = {str(line.inquiry_id.analytic_account_id.id): 100.0}
