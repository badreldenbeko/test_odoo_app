from odoo import fields, models, api, _


class InquiryPlanning(models.Model):
    _inherit = 'inquiry.inquiry'

    contingencies_based_on_ra = fields.Boolean(string=_('Contingencies based on RA'))
    contingencies_based_on_ra_text = fields.Char(compute='_compute_contingencies_based_on_ra_text')
    contingencies_based_on_ra_comments = fields.Html(string=_('Comments'))

    @api.depends('contingencies_based_on_ra')
    def _compute_contingencies_based_on_ra_text(self):
        for rec in self:
            text = 'Not Applicable'
            if not rec.contingencies_based_on_ra:
                text = 'Action Required'
            rec.contingencies_based_on_ra_text = text

    # Availability of Resources

    manpower = fields.Boolean()
    manpower_text = fields.Char(compute='_compute_manpower_text')
    manpower_comments = fields.Html()

    @api.depends('manpower')
    def _compute_manpower_text(self):
        for rec in self:
            text = 'Available'
            if not rec.manpower:
                text = 'To Be Arrange'
            rec.manpower_text = text

    machine = fields.Boolean()
    machine_text = fields.Char(compute='_compute_machine_text')
    machine_comments = fields.Html()

    @api.depends('machine')
    def _compute_machine_text(self):
        for rec in self:
            text = 'Available'
            if not rec.machine:
                text = 'Not Available'
            rec.machine_text = text

    # Raw Material

    material_availability_free_issue = fields.Boolean(string=_('Free Issue'))
    material_availability_supply = fields.Boolean(string=_('Supply'))
    material_availability_comment = fields.Html(string=_('Comments'))

    raw_material_forged = fields.Boolean(string=_('Forged'))
    raw_material_casted = fields.Boolean(string=_('Casted'))
    raw_material_rod_pip = fields.Boolean(string=_('Rod / Pip'))
    raw_material_others = fields.Boolean(string=_('Others'))
    raw_material_comment = fields.Html(string=_('Comments'))

    supply_availability = fields.Selection([('yes', 'Yes'), ('no', 'No')])
    supply_availability_text = fields.Char(compute='_compute_supply_availability_text')
    supply_availability_comment = fields.Html(string=_('Comments'))

    @api.depends('supply_availability')
    def _compute_supply_availability_text(self):
        for rec in self:
            text = 'Available'
            if rec.supply_availability == 'no':
                text = 'Not Available'
            elif rec.supply_availability == 'yes':
                text = 'Available'
            else:
                text = None
            rec.supply_availability_text = text

    supply_imported = fields.Selection([('yes', 'Yes'), ('no', 'No')])
    supply_imported_text = fields.Char(compute='_compute_supply_imported_text')
    supply_imported_comment = fields.Html(string=_('Comments'))

    @api.depends('supply_imported')
    def _compute_supply_imported_text(self):
        for rec in self:
            text = ''
            if rec.supply_imported == 'yes':
                text = 'Yes'
            elif rec.supply_imported == 'no':
                text = 'No'
            else:
                text = None
            rec.supply_imported_text = text

    job_required_by = fields.Date()
    planned_completion_on = fields.Date()
    job_planned_comment = fields.Html(string=_('Comments'))

    additional_drawing_needed = fields.Boolean(string=_('Additional Drawing Needed'), default=False)
    additional_drawing_text = fields.Char(compute='_compute_additional_drawing_text')
    additional_drawing_comment = fields.Html(string=_('Additional Drawing Comments'))

    @api.depends('additional_drawing_needed')
    def _compute_additional_drawing_text(self):
        for rec in self:
            text = 'Yes'
            if not rec.additional_drawing_needed:
                text = 'No'
            rec.additional_drawing_text = text

    drawing_full_set = fields.Boolean(string=_('Full Set'))
    drawing_partial = fields.Boolean(string=_('Partial'))

    drawing_selection_type = fields.Selection([('full', 'Full Set'), ('partial', 'Partial')])

    drawing_type_ga = fields.Boolean(string=_('GA'))
    drawing_type_pid = fields.Boolean(string=_('PID'))
    drawing_type_iso = fields.Boolean(string=_('ISO'))
    drawing_type_shop = fields.Boolean(string=_('SHOP'))
    drawing_type_sketch = fields.Boolean(string=_('Sketch'))
    drawing_type_sketch_ws = fields.Boolean(string=_('Sketch(WS)'))

    planning_additional_comment = fields.Html(string=_('Additional Comments'))
