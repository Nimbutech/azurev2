# -*- coding: utf-8 -*-
{
    'name': "custom_crm",

    'summary': """
        Módulo personalizado de crm para nimbutech""",

    'description': """
        Módulo personalizado de crm para nimbutech""",
    'author': "Nimbutech",
    'website': "https://www.nimbutech.com",

    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['crm','helpdesk'], 

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'wizard/crm_bant_view.xml',
        'views/templates.xml',
        'wizard/crm_lead_convert2ticket_views.xml'
    ], 
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
