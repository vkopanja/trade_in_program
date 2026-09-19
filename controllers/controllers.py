import re
import uuid

import psycopg2

from odoo import http
from odoo.http import request
from odoo.tools import escape_psql

EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
TOKEN_RE = re.compile(r'^[0-9a-f]{32}$')
TOKEN_CONSTRAINT = 'trade_in_program_trade_in_submission_token_unique'
MAX_NAME_LENGTH = 100

ERROR_MESSAGES = {
    'name': 'Please enter your name.',
    'name_len': 'Name must be less than or equal to %(max)s characters.',
    'email': "Please enter a valid email address.",
    'invalid': "Something went wrong. Please try another value.",
}


class TradeInProgram(http.Controller):

    @http.route('/trade-in', type='http', auth='public', website=True, csrf=True)
    def form(self, submitted=None, error=None, **kw):
        return self._render_form(
            reference=self._find_submitted_reference(submitted),
            error_message=ERROR_MESSAGES.get(error, ERROR_MESSAGES['invalid']) if error else None,
        )

    @http.route("/trade-in/submit", type='http', auth='public', methods=['POST'], website=True, csrf=True)
    def submit(self, **post):
        token = post.get('submission_token') or ''
        if not TOKEN_RE.match(token):
            token = uuid.uuid4().hex

        TradeIn = request.env['trade_in_program.trade_in'].sudo()
        if TradeIn.search_count([('submission_token', '=', token)]):
            return request.redirect('/trade-in?submitted=%s' % token)

        errors = {}

        email = (post.get('customer_email') or '').strip()
        name = (post.get('customer_name') or '').strip()

        if not EMAIL_RE.match(email):
            errors['email'] = ERROR_MESSAGES['email']
        if not name:
            errors['customer_name'] = ERROR_MESSAGES['name']
        if len(name) > MAX_NAME_LENGTH:
            errors['customer_name'] = ERROR_MESSAGES['name_len'] % {'max': MAX_NAME_LENGTH}

        device = self._find_active_device(self._safe_int(post.get('device_id')))
        condition = request.env['trade_in_program.condition'].sudo().browse(
            self._safe_int(post.get('condition_id'))).exists()
        if not device or not condition:
            errors['invalid'] = ERROR_MESSAGES['invalid']

        if errors:
            return self._render_form(form_values=post, form_errors=errors)

        try:
            with request.env.cr.savepoint():
                Partner = request.env['res.partner'].sudo()
                partner = Partner.search([('email', '=ilike', escape_psql(email))], limit=1)
                if not partner:
                    partner = Partner.create({'name': name, 'email': email})

                TradeIn.create({
                    'partner_id': partner.id,
                    'customer_name': name,
                    'customer_email': email,
                    'device_id': device.id,
                    'condition_id': condition.id,
                    'submission_token': token,
                })
        except psycopg2.errors.UniqueViolation as exc:
            # A simultaneous submit of the same form was saved first; show its result instead.
            if exc.diag.constraint_name != TOKEN_CONSTRAINT:
                raise
        return request.redirect('/trade-in?submitted=%s' % token)

    @http.route('/trade-in/quote', type='json', auth='public')
    def quote(self, device_id=None, condition_id=None, **kw):
        device = self._find_active_device(self._safe_int(device_id))
        condition = request.env['trade_in_program.condition'].sudo().browse(
            self._safe_int(condition_id)).exists()

        if not device or not condition:
            return {'ok': False}

        return {
            'ok': True,
            'value': request.env['trade_in_program.trade_in']._calculate_offer(device.base_trade_in_value,
                                                                               condition.multiplier)
        }

    def _render_form(self, form_values=None, form_errors=None, **kw):
        devices = request.env['trade_in_program.device'].sudo().search([])
        conditions = request.env['trade_in_program.condition'].sudo().search([])

        return request.render('trade_in_program.trade_in_form', {
            'devices': devices,
            'conditions': conditions,
            'max_name_length': MAX_NAME_LENGTH,
            'submission_token': uuid.uuid4().hex,
            'form_values': form_values or {},
            'form_errors': form_errors or {},
            **kw,
        })

    @staticmethod
    def _safe_int(value):
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _find_submitted_reference(token):
        if not token or not TOKEN_RE.match(token):
            return None
        trade_in = request.env['trade_in_program.trade_in'].sudo().search(
            [('submission_token', '=', token)], limit=1)
        return trade_in.reference

    @staticmethod
    def _find_active_device(device_id):
        return request.env['trade_in_program.device'].sudo().search([('id', '=', device_id)], limit=1)
