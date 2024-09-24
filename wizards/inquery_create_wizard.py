from odoo import fields, models, api, _


class InquiryCreateWizard(models.TransientModel):
    _name = 'inquiry.create.wizard'
    _description = 'Inquiry Create Wizard'

    partner_id = fields.Many2one('res.partner', required=True, string=_("Customer"))
    job_category = fields.Selection(
        [('trading', 'Trading'), ('service', 'Service'), ('manufacturing', 'Manufacturing'), ('other', 'Other')],
        required=True)
    trading_job_category = fields.Selection([('finished', 'Finished '), ('semi_finished', 'Semi Finished')])
    new_product = fields.Boolean(default=False)
    new_product_design = fields.Selection(
        [('beginning', 'Desired In The Beginning'), ('later', 'Desired In A Later Stage')])
    has_prp = fields.Boolean()

    @api.onchange('job_category')
    def _change_job_category(self):
        if self.job_category != 'trading':
            self.trading_job_category = None
        if self.job_category != 'manufacturing':
            self.new_product = False

    @api.onchange('new_product')
    def _change_new_product(self):
        if not self.new_product:
            self.new_product_design = None

    def create_new_inquiry(self):
        vals = {
            'partner_id': self.partner_id.id,
            'job_category': self.job_category,
            'trading_job_category': self.trading_job_category,
            'new_product': self.new_product,
            'new_product_design': self.new_product_design,
            'has_prp': self.has_prp,
        }
        new_inquiry = self.env['inquiry.inquiry'].create(vals)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'inquiry.inquiry',
            'name': new_inquiry.name,
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': new_inquiry.id,
            'target': 'current',
        }
