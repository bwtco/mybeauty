# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'Invoice report customization',
    'version': '1.4',
    'category': 'Account',
    'summary': '',
    'description': """
    """,
    'depends': ['base','account'],
    'data': [
        'report/report_paperformat_data.xml',
        'report/report_templates.xml',
        'report/report_invoice.xml',
        'views/res_company_views.xml',
        'views/res_bank_view.xml'
    ],
    'images': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
