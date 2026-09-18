from datetime import date
from enum import Enum

from odoo import _, models, fields, api


class Status(str, Enum):
    NEW = 'new'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'

    @classmethod
    def to_selection(cls):
        return [(status.value, status.name.capitalize()) for status in cls]


class TradeIn(models.Model):
    _name = 'trade_in_program.trade_in'
    _description = 'Trade-In model for managing trade-in offers and requests'
    _rec_name = 'reference'
    _sql_constraints = [
        ('reference_unique', 'unique(reference)', 'Reference must be unique')
    ]

    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    partner_email = fields.Char(related='partner_id.email', string='Email')
    device_id = fields.Many2one('trade_in_program.device', string='Device', required=True)
    condition_id = fields.Many2one('trade_in_program.condition', string='Condition', required=True)

    base_value = fields.Float(readonly=True, copy=False)
    multiplier = fields.Float(readonly=True, copy=False)
    offer_value = fields.Float(compute='_compute_offer', store=True)
    reference = fields.Char(
        string='Reference', required=True, readonly=True, copy=False, index=True,
        default=lambda self: _('New'),
    )
    status = fields.Selection(
        Status.to_selection(),
        string='Status',
    )
    rejection_reason = fields.Text(string='Rejection Reason')

    @api.onchange('device_id', 'condition_id')
    def _onchange_inputs(self):
        self.base_value = self.device_id.base_trade_in_value
        self.multiplier = self.condition_id.multiplier

    @api.constrains('status', 'rejection_reason')
    def _check_rejection_reason(self):
        for rec in self:
            if rec.status == Status.REJECTED.value and not rec.rejection_reason:
                raise models.ValidationError(
                    "A rejection reason is required when the status is set to 'Rejected'.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('device_id') and not vals.get('base_value'):
                vals['base_value'] = self.env['trade_in_program.device'] \
                    .browse(vals['device_id']).base_trade_in_value
            if vals.get('condition_id') and not vals.get('multiplier'):
                vals['multiplier'] = self.env['trade_in_program.condition'] \
                    .browse(vals['condition_id']).multiplier
            if not vals.get('status'):
                vals['status'] = Status.NEW.value
            if vals.get('reference', _('New')) == _('New'):
                vals['reference'] = self.env['ir.sequence'].next_by_code(
                    'trade_in_program.trade_in') or _('New')

        return super().create(vals_list)

    @api.model
    def _calculate_offer(self, base_value, multiplier):
        return base_value * multiplier

    @api.depends('base_value', 'multiplier')
    def _compute_offer(self):
        for rec in self:
            rec.offer_value = rec._calculate_offer(rec.base_value, rec.multiplier)

    def action_approve(self):
        self.status = Status.ACCEPTED.value
        self.rejection_reason = None
        return True

    def action_reject(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Reject Trade-In'),
            'res_model': 'trade_in_program.reject.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_trade_in_id': self.id},
        }
