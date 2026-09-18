import re

from odoo import http
from odoo.http import request
from odoo.tools import escape_psql

EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
REFERENCE_RE = re.compile(r'^TI/\d{4}/\d{5,}$')

ERROR_MESSAGES = {
    'email': "Please enter a valid email address.",
    'invalid': "Something went wrong. Please try again later.",
}


class TradeInProgram(http.Controller):

    @http.route('/trade-in', type='http', auth='public', website=False, csrf=True)
    def form(self, submitted=None, error=None, **kw):
        devices = request.env['trade_in_program.device'].sudo().search([])
        conditions = request.env['trade_in_program.condition'].sudo().search([])
        return request.render('trade_in_program.trade_in_form', {
            'devices': devices,
            'conditions': conditions,
            'reference': submitted if submitted and REFERENCE_RE.match(submitted) else None,
            'error_message': ERROR_MESSAGES.get(error, ERROR_MESSAGES['invalid']) if error else None,
        })

    @http.route("/trade-in/submit", type='http', auth='public', methods=['POST'], csrf=True)
    def submit(self, **post):
        email = (post.get('customer_email') or '').strip()
        name = (post.get('customer_name') or '').strip()
        if not name or not EMAIL_RE.match(email):
            return request.redirect('/trade-in?error=email')

        device = request.env['trade_in_program.device'].sudo().browse(
            self._safe_int(post.get('device_id'))).exists()
        condition = request.env['trade_in_program.condition'].sudo().browse(
            self._safe_int(post.get('condition_id'))).exists()
        if not device or not condition:
            return request.redirect('/trade-in?error=invalid')

        Partner = request.env['res.partner'].sudo()
        partner = Partner.search([('email', '=ilike', escape_psql(email))], limit=1)
        if not partner:
            partner = Partner.create({'name': name, 'email': email})

        trade_in = request.env['trade_in_program.trade_in'].sudo().create({
            'partner_id': partner.id,
            'device_id': device.id,
            'condition_id': condition.id,
        })
        return request.redirect('/trade-in?submitted=%s' % trade_in.reference)

    @http.route('/trade-in/quote', type='json', auth='public')
    def quote(self, device_id=None, condition_id=None, **kw):
        device = request.env['trade_in_program.device'].sudo().browse(
            self._safe_int(device_id)).exists()
        condition = request.env['trade_in_program.condition'].sudo().browse(
            self._safe_int(condition_id)).exists()

        if not device or not condition or not device.active:
            return {'ok': False}

        return {
            'ok': True,
            'value': request.env['trade_in_program.trade_in']._calculate_offer(device.base_trade_in_value,
                                                                               condition.multiplier)
        }

    @staticmethod
    def _safe_int(value):
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
