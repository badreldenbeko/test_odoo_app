from odoo import fields, models, api, _


class BqrRevision(models.Model):
    _name = 'bqr.revision'
    _description = 'BQR Revision'

    name = fields.Char(
        required=True, copy=False, readonly=True,
        index='trigram',
        tracking=True,
        default=lambda self: _('New Revision'))
    bqr_id = fields.Many2one('budgetary.quotation.request')
    date = fields.Date()
    m_margin = fields.Float(string=_('Margin'), digits='Product Price')
    m_margin_on = fields.Selection(
        selection=[
            ('cost', _("Cost")),
            ('min_price', _("Min Price")),
            ('avg_price', _("Avg Price")),
            ('max_price', _("Max Price")),
            ('confirmed', _("Confirmed")),
        ],
        string=_("Margin On"), copy=False, tracking=True, default='cost')
    m_margin_type = fields.Selection(
        selection=[
            ('percentage', _("Percentage")),
            ('amount', _("Amount")),
        ],
        string=_("Margin Type"), copy=False, tracking=True, default='percentage')
    t_margin = fields.Float(string=_('Margin'), digits='Product Price')
    t_margin_on = fields.Selection(
        selection=[
            ('cost', _("Cost")),
            ('min_price', _("Min Price")),
            ('avg_price', _("Avg Price")),
            ('max_price', _("Max Price")),
            ('confirmed', _("Confirmed")),
        ],
        string=_("Margin On"), copy=False, tracking=True, default='cost')
    t_margin_type = fields.Selection(
        selection=[
            ('percentage', _("Percentage")),
            ('amount', _("Amount")),
        ],
        string=_("Margin Type"), copy=False, tracking=True, default='percentage')
    fp_margin = fields.Float(string=_('Margin'), digits='Product Price')
    fp_margin_on = fields.Selection(
        selection=[
            ('cost', _("Cost")),
            ('min_price', _("Min Price")),
            ('avg_price', _("Avg Price")),
            ('max_price', _("Max Price")),
            ('confirmed', _("Confirmed")),
        ],
        string=_("Margin On"), copy=False, tracking=True, default='cost')
    fp_margin_type = fields.Selection(
        selection=[
            ('percentage', _("Percentage")),
            ('amount', _("Amount")),
        ],
        string=_("Margin Type"), copy=False, tracking=True, default='percentage')
    sfp_margin = fields.Float(string=_('Margin'), digits='Product Price')
    sfp_margin_on = fields.Selection(
        selection=[
            ('cost', _("Cost")),
            ('min_price', _("Min Price")),
            ('avg_price', _("Avg Price")),
            ('max_price', _("Max Price")),
            ('confirmed', _("Confirmed")),
        ],
        string=_("Margin On"), copy=False, tracking=True, default='cost')
    sfp_margin_type = fields.Selection(
        selection=[
            ('percentage', _("Percentage")),
            ('amount', _("Amount")),
        ],
        string=_("Margin Type"), copy=False, tracking=True, default='percentage')
    mm_margin = fields.Float(string=_('Margin'), digits='Product Price')
    mm_margin_on = fields.Selection(
        selection=[
            ('cost', _("Cost")),
            ('min_price', _("Min Price")),
            ('avg_price', _("Avg Price")),
            ('max_price', _("Max Price")),
            ('confirmed', _("Confirmed")),
        ],
        string=_("Margin On"), copy=False, tracking=True, default='cost')
    mm_margin_type = fields.Selection(
        selection=[
            ('percentage', _("Percentage")),
            ('amount', _("Amount")),
        ],
        string=_("Margin Type"), copy=False, tracking=True, default='percentage')
    o_margin = fields.Float(string=_('Margin'), digits='Product Price')
    o_margin_type = fields.Selection(
        selection=[
            ('percentage', _("Percentage")),
            ('amount', _("Amount")),
        ],
        string=_("Margin Type"), copy=False, tracking=True, default='amount')

    @api.model_create_multi
    def create(self, vals_list):
        self.env.registry.clear_cache()
        for vals in vals_list:
            if not vals.get('name') and vals.get('bqr_id'):
                bqr = self.env['budgetary.quotation.request'].search([('id', '=', vals.get('bqr_id'))], limit=1)
                if bqr:
                    vals['name'] = bqr.name + '-' + self.env['ir.sequence'].next_by_code(
                        'seq.bqr.revision') or _("New Revision")
                else:
                    vals['name'] = self.env['ir.sequence'].next_by_code('seq.bqr.revision') or _("New Revision")
        res = super().create(vals_list)
        return res

    def apply_revision(self):
        self.bqr_id.m_margin = self.m_margin
        self.bqr_id.m_margin_on = self.m_margin_on
        self.bqr_id.m_margin_type = self.m_margin_type

        self.bqr_id.t_margin = self.t_margin
        self.bqr_id.t_margin_on = self.t_margin_on
        self.bqr_id.t_margin_type = self.t_margin_type

        self.bqr_id.fp_margin = self.fp_margin
        self.bqr_id.fp_margin_on = self.fp_margin_on
        self.bqr_id.fp_margin_type = self.fp_margin_type

        self.bqr_id.sfp_margin = self.sfp_margin
        self.bqr_id.sfp_margin_on = self.sfp_margin_on
        self.bqr_id.sfp_margin_type = self.sfp_margin_type

        self.bqr_id.mm_margin = self.mm_margin
        self.bqr_id.mm_margin_on = self.mm_margin_on
        self.bqr_id.mm_margin_type = self.mm_margin_type

        self.bqr_id.o_margin = self.o_margin
        self.bqr_id.o_margin_type = self.o_margin_type

        self.bqr_id.change_all_material_margin()
        self.bqr_id.change_all_tools_margin()
        self.bqr_id.change_all_semi_finish_product_margin()
        self.bqr_id.change_all_finish_product_margin()
        self.bqr_id.change_all_operation_margin()

        return True
