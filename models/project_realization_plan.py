from odoo import fields, models, api


class ProjectRealizationPlanRequirements(models.Model):
    _name = 'project.realization.plan.requirements'
    _description = 'Description'

    name = fields.Char(required=True, translate=True)


class ProjectRealizationPlan(models.Model):
    _name = 'project.realization.plan'
    _description = 'Project Realization Plan'

    inquiry_id = fields.Many2one('inquiry.inquiry', required=True)
    prp_requirements = fields.Many2one('project.realization.plan.requirements', required=True)
    result_of_requirement = fields.Char()
    responsibility = fields.Char()
    target_date = fields.Date()
    final_output_of_planning = fields.Char()
    remarks = fields.Html()
