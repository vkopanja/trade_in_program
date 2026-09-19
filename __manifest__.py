# -*- coding: utf-8 -*-
{
    'name': "Trade-in Program",
    'version': '16.0.1.0.0',
    'application': True,
    'installable': True,
    'summary': """
        This is a trade-in program module for Odoo 16. It allows users to manage trade-in offers and track the status of trade-in requests.""",

    'description': """
        This module provides a comprehensive solution for managing trade-in offers and tracking the status of trade-in requests within Odoo 16. It includes features such as creating and managing trade-in offers, tracking the status of trade-in requests, and providing a seamless user experience for both customers and administrators.
    """,

    'author': "Vedran Kopanja",
    'website': "https://github.com/vkopanja",

    'category': 'Services',
    'license': 'LGPL-3',

    'depends': ['website'],

    'data': [
        'security/trade_in_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'wizard/trade_in_reject_wizard_views.xml',
        'views/condition_views.xml',
        'views/device_views.xml',
        'views/trade_in_views.xml',
        'views/res_partner_views.xml',
        'views/trade_in_menus.xml',
        'views/trade_in_customer_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'trade_in_program/static/src/js/trade_in_form.js',
            'trade_in_program/static/src/scss/trade_in.scss',
        ],
    },
    'demo': [
        'demo/demo.xml',
    ],
}
