# -*- coding: utf-8 -*-
{
    'name': "Trade-in Program",
    'version': '16.0.1.0.0',
    'application': True,
    'installabale': True,
    'summary': """
        This is a trade-in program module for Odoo 16. It allows users to manage trade-in offers and track the status of trade-in requests.""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Vedran Kopanja",
    'website': "https://github.com/vkopanja",

    'category': 'Services',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/condition_views.xml',
        'views/device_views.xml',
        'views/trade_in_views.xml',
        'views/trade_in_menus.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
