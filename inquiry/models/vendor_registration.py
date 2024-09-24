from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class VendorRegistration(models.Model):
    _name = 'vendor.registration'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'Description'

    reg_no = fields.Char(required=True, tracking=True)
    name = fields.Char(required=True, tracking=True)
    email = fields.Char()
    date = fields.Date()

    supply_chain_manager_id = fields.Many2one('hr.employee', tracking=True)
    general_manager_id = fields.Many2one('hr.employee', tracking=True)

    # LEGAL ENTITY
    contact_person = fields.Many2one('hr.employee', tracking=True)
    address = fields.Char(tracking=True)
    phone = fields.Char(tracking=True)
    mobile = fields.Char(tracking=True)
    fax = fields.Char(tracking=True)

    # LEGAL ENTITY
    is_corporation = fields.Boolean(tracking=True)
    is_partnership = fields.Boolean(tracking=True)
    is_sole_proprietorship = fields.Boolean(tracking=True)
    is_joint_venture = fields.Boolean(tracking=True)
    is_franchise = fields.Boolean(tracking=True)
    is_non_profit = fields.Boolean(tracking=True)

    # type of business
    is_retailer = fields.Boolean(tracking=True)
    is_construction_contractor = fields.Boolean(tracking=True)
    is_distributor_dealer_agent = fields.Boolean(tracking=True)
    is_publication_broadcasting = fields.Boolean(tracking=True)
    is_professional_services = fields.Boolean(tracking=True)
    is_proprietary_products = fields.Boolean(tracking=True)
    is_service_provider = fields.Boolean(tracking=True)
    is_manufacture = fields.Boolean(tracking=True)
    is_consultant = fields.Boolean(tracking=True)
    is_freight_transportation = fields.Boolean(tracking=True)
    is_wholesaler = fields.Boolean(tracking=True)
    is_other = fields.Boolean(tracking=True)

    details_on_service = fields.Html(tracking=True)
    details_of_any_approvals = fields.Html(tracking=True)
    year_of_start = fields.Char(tracking=True)
    commercial_licence = fields.Char(tracking=True)
    business_hours = fields.Char(tracking=True)
    facilities_to_carry = fields.Html(tracking=True)
    branches_out_ksa = fields.Html(tracking=True)
    certificates_validity = fields.Html(tracking=True)
    client_approvals = fields.Html(tracking=True)
    beneficiary_name = fields.Char(tracking=True)
    tax_id = fields.Char(tracking=True)

    on_site_audit = fields.Selection([('yes', 'Yes'), ('no', 'No')], tracking=True)
    first_inspection = fields.Selection([('yes', 'Yes'), ('no', 'No')], tracking=True)

    based_on_proprietary = fields.Selection([('yes', 'Yes'), ('no', 'No')], tracking=True)
    legal_requirements = fields.Selection([('yes', 'Yes'), ('no', 'No')], tracking=True)
    contractual_requirements = fields.Selection([('yes', 'Yes'), ('no', 'No')], tracking=True)

    def create_vendor(self):
        old_vendor = self.env['res.partner'].search([('registration_id', '=', self.id)], limit=1)
        if old_vendor:
            raise ValidationError(_(f'Vendor {old_vendor.name} already created'))
        vendor_obj = self.env['res.partner']
        vendor_values = {
            'registration_id': self.id,
            'is_company': True,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'mobile': self.mobile,
            'street': self.address,
            'supplier_rank': 1,
        }
        new_vendor = vendor_obj.create(vendor_values)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'name': new_vendor.name,
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': new_vendor.id,
            'target': 'current',
        }
