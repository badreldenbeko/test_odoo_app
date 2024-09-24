from odoo import fields, models, api, _


class ProjectProject(models.Model):
    _inherit = 'project.project'

    inquiry_id = fields.Many2one('inquiry.inquiry', string=_('Inquiry'))
