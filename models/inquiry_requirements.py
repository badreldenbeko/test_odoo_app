from odoo import fields, models, api


class InquiryRequirements(models.Model):
    _name = 'inquiry.requirements'
    _description = 'Inquiry requirements'

    name = fields.Char(required=True)
    inquiry_id = fields.Many2one('inquiry.inquiry')
    sequence = fields.Integer(default=1)
    requirement_type = fields.Selection([('file', 'File'), ('info', 'Information')], default='info')
    info = fields.Text()
    file = fields.Binary()
    image = fields.Binary()
    attach_type = fields.Selection([('pdf', 'PDF'), ('image', 'Image')], default='pdf')
    state = fields.Selection([('done', 'Done'), ('not_done', 'Not Done')], default='not_done',
                             compute='_calc_requirement_state', store=True)

    @api.depends('requirement_type', 'info', 'file', 'image')
    def _calc_requirement_state(self):
        for rec in self:
            if rec.requirement_type == 'file':
                if rec.attach_type == 'pdf':
                    if not rec.file:
                        rec.state = 'not_done'
                    else:
                        rec.state = 'done'
                elif rec.attach_type == 'image':
                    if not rec.image:
                        rec.state = 'not_done'
                    else:
                        rec.state = 'done'
            elif rec.requirement_type == 'info':
                info_text = rec.info.rstrip() if rec.info else ''
                if not info_text:
                    rec.state = 'not_done'
                else:
                    rec.state = 'done'

    @api.onchange('attach_type')
    def _change_attach_type(self):
        if self.attach_type == 'pdf':
            self.image = None
        elif self.attach_type == 'image':
            self.file = None
