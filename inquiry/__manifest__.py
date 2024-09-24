# -*- coding: utf-8 -*-

{
    'name': "inquiry",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'bus', 'account', 'account_accountant', 'stock', 'sale_management', 'purchase', 'project',
                'mrp', 'hr'],

    # always loaded
    'data': [
        # Security
        'security/ir.model.access.csv',
        # Data
        'data/account_analytic_plan_data.xml',
        'data/project_realization_plan_requirements.xml',
        'data/scope_of_product.xml',
        'data/initial_review.xml',
        'data/commercial.xml',
        'data/design_development.xml',
        'data/inquiry_qa_qc.xml',
        'data/sequences.xml',
        # Wizards
        'wizards/inquiry_create_wizard.xml',
        'wizards/create_rfq_wizard.xml',
        'wizards/inquiry_follower_wizard.xml',
        ##
        'reports/sa_work_order.xml',
        'reports/inquiry_order_contract_review_report.xml',
        # Views
        'views/vendor_registration.xml',
        'views/res_bank.xml',
        'views/res_partner_bank.xml',
        'views/res_partner.xml',
        'views/res_company.xml',
        'views/hr_employee.xml',
        'views/inquiry_product_group.xml',
        'views/material_grade.xml',
        'views/profile_type.xml',
        'views/product_category.xml',
        'views/product_template.xml',
        'views/service_consumable.xml',
        'views/inquiry_commercial.xml',
        'views/inquiry_design_development.xml',
        'views/inquiry_qa_qc.xml',
        'views/inquiry_followers.xml',
        'views/account_move.xml',
        # 'views/mrp_eco.xml',
        'views/project.xml',
        'views/inquiry.xml',
        'views/project_realization_plan_requirements.xml',
        'views/scope_of_product.xml',
        'views/initial_review.xml',
        'views/budgetary_quotation_request.xml',
        'views/bqr_overhead_category.xml',
        'views/purchase_order_request.xml',
        'views/purchase_order.xml',
        'views/sale_order.xml',
        'views/mrp_production.xml',
        'views/mrp_routing_workcenter.xml',
        'views/stock_picking.xml',
        'views/stock_move_line.xml',
        'views/mrp_workcenter_productivity.xml',
        'views/mrp_workorder.xml',
        # Menu
        'views/menu.xml',
        # Reports
        'reports/customer_profile.xml',
        'reports/product_realization_plan.xml',
        'reports/dots_invoice.xml',

        'reports/sale_quotation.xml',
        'reports/process_traveler_card.xml',
        'reports/pp_ptc_machining.xml',
        'reports/delivery_note.xml',
        'reports/gate_pass.xml',
        'reports/purchase_order.xml',
        'reports/vendor_registration_form.xml',
        'reports/inspection_and_test_plan.xml',
        'reports/manufacturing_process_summary.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'application': True,
    'license': "LGPL-3",
}
