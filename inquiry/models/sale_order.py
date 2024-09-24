from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    inquiry_id = fields.Many2one('inquiry.inquiry')
    customer_po_no = fields.Char()
    customer_po_date = fields.Date()
    customer_po_file = fields.Binary()
    partner_rfq_ref_no = fields.Char(string=_('RFQ/REF NO.'), related='inquiry_id.partner_rfq_ref_no')
    rfq_ref_date = fields.Date(string=_('RFQ/REF Date'), related='inquiry_id.partner_rfq_ref_date')
    material_provided_by = fields.Text()

    wo_ids = fields.One2many('stock.picking', 'inquiry_sale_id')

    # Post order review
    sale_manager_id = fields.Many2one('hr.employee')
    sale_post_review = fields.Boolean(default=False)
    sale_post_review_comment = fields.Html()

    technical_manager_id = fields.Many2one('hr.employee')
    technical_post_review = fields.Boolean(default=False)
    technical_post_review_comment = fields.Html()

    operation_manager_id = fields.Many2one('hr.employee')
    operation_post_review = fields.Boolean(default=False)
    operation_post_review_comment = fields.Html()

    qa_qc_manager_id = fields.Many2one('hr.employee')
    qa_qc_post_review = fields.Boolean(default=False)
    qa_qc_post_review_comment = fields.Html()

    pr_manager_id = fields.Many2one('hr.employee')
    pr_post_review = fields.Boolean(default=False)
    pr_post_review_comment = fields.Html()

    def create(self, vals_list):
        res = super(SaleOrder, self).create(vals_list)
        if self.inquiry_id:
            self.inquiry_id.state = 'final'
        return res

    def action_confirm(self):
        check = True
        all_review = True
        utils = self.env['utils.utils']
        if all([self.sale_post_review, self.technical_post_review, self.operation_post_review, self.qa_qc_post_review]):
            all_review = True
        else:
            all_review = False
        if not self.customer_po_no or not self.customer_po_file or self.inquiry_id.state != 'final':
            check = False
        else:
            for partner in self.inquiry_id.inquiry_followers_ids.mapped('to_user_id').mapped('partner_id'):
                utils.send_notification(partner, 'success',
                                        f'Quotation Confirmed',
                                        f'Quotation {self.name} Confirmed')
        if not check:
            raise ValidationError(
                _(f'The Inquiry not in Contract Done state or The customer po or attach po file not uploaded.'))
        else:
            self.inquiry_id.state = 'done'
        if not all_review:
            raise ValidationError(
                _(f'Must have post order review from others page.'))
        res = super(SaleOrder, self).action_confirm()
        for partner in self.inquiry_id.inquiry_followers_ids.mapped('to_user_id').mapped('partner_id'):
            utils.send_notification(partner, 'success',
                                    f'Quotation Confirmed',
                                    f'Quotation {self.name} Confirmed')
        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    inquiry_id = fields.Many2one('inquiry.inquiry', related='order_id.inquiry_id')

    @api.depends('order_id.partner_id', 'product_id')
    def _compute_analytic_distribution(self):
        for line in self:
            if not line.display_type:
                distribution = line.env['account.analytic.distribution.model']._get_distribution({
                    "product_id": line.product_id.id,
                    "product_categ_id": line.product_id.categ_id.id,
                    "partner_id": line.order_id.partner_id.id,
                    "partner_category_id": line.order_id.partner_id.category_id.ids,
                    "company_id": line.company_id.id,
                })
                line.analytic_distribution = distribution or line.analytic_distribution
            if line.inquiry_id:
                line.analytic_distribution = {str(line.inquiry_id.analytic_account_id.id): 100.0}
