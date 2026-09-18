# -*- coding: utf-8 -*-
# from odoo import http


# class TradeInProgram(http.Controller):
#     @http.route('/trade_in_program/trade_in_program', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/trade_in_program/trade_in_program/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('trade_in_program.listing', {
#             'root': '/trade_in_program/trade_in_program',
#             'objects': http.request.env['trade_in_program.trade_in_program'].search([]),
#         })

#     @http.route('/trade_in_program/trade_in_program/objects/<model("trade_in_program.trade_in_program"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('trade_in_program.object', {
#             'object': obj
#         })
