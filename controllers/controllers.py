from odoo import http
from odoo.http import request


class TradeInProgram(http.Controller):

    @http.route('/trade-in', type='http', auth='public', website=False, csrf=True)
    def form(self, **kw):
        devices = request.env['trade_in_program.device'].sudo().search([])
        conditions = request.env['trade_in_program.condition'].sudo().search([])
        return request.render('trade_in_program.trade_in_form', {
            'devices': devices,
            'conditions': conditions,
        })

    @http.route('/trade-in/quote', type='json', auth='public')
    def quote(self, device_id=None, condition_id=None, **kw):
        device = request.env['trade_in_program.device'].sudo().browse(
            self._safe_int(device_id)).exists()
        condition = request.env['trade_in_program.condition'].sudo().browse(
            self._safe_int(condition_id)).exists()

        if not device or not condition:
            return {'ok': False}

        return {
            'ok': True,
            'value': device.base_trade_in_value * condition.multiplier,
        }

    @staticmethod
    def _safe_int(value):
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
