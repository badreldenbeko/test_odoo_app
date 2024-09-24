from odoo import fields, models, api


class DesignDevelopment(models.Model):
    _name = 'design.development'
    _description = 'Design & Development'

    name = fields.Char(required=True, translate=True)
    selection_label = fields.Char(required=True, translate=True)


class DesignDevelopmentLine(models.Model):
    _name = 'design.development.line'
    _description = 'Design & Development Line'

    inquiry_id = fields.Many2one('inquiry.inquiry')
    design_development_id = fields.Many2one('design.development', required=True)
    selection_label = fields.Char(compute='_compute_selection_label')
    status = fields.Selection([('not', 'Not Applicable'), ('yes', 'Yes'), ('no', 'No')], default='not')
    comments = fields.Html()

    @api.depends('status', 'design_development_id.selection_label')
    def _compute_selection_label(self):
        for rec in self:
            # 'design_development_id.selection_label'
            if rec.status == 'yes':
                rec.selection_label = f'{rec.design_development_id.selection_label}'
            elif rec.status == 'no':
                rec.selection_label = f'Not {rec.design_development_id.selection_label}'
            else:
                rec.selection_label = 'Not Applicable'
