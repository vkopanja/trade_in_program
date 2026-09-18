from enum import Enum

from odoo import models, fields, api


class Status(str, Enum):
    PENDING = 'pending'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'

    @classmethod
    def to_selection(cls):
        return [(status.value, status.name.capitalize()) for status in cls]


class TradeIn(models.Model):
    _name = 'trade_in_program.trade_in'
    _description = 'Trade-In model for managing trade-in offers and requests'

    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    device_id = fields.Many2one('trade_in_program.device', string='Device', required=True)
    condition_id = fields.Many2one('trade_in_program.condition', string='Condition', required=True)

    base_value = fields.Float(readonly=True, copy=False)
    multiplier = fields.Float(readonly=True, copy=False)
    offer_value = fields.Float(compute='_compute_offer', store=True)
    reference = fields.Char(string='Reference')
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
                    "Rejection reason is required when the status is set to 'Rejected'.")

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
                vals['status'] = Status.PENDING.value
        return super().create(vals_list)

    @api.depends('base_value', 'multiplier')
    def _compute_offer(self):
        for rec in self:
            rec.offer_value = rec.base_value * rec.multiplier
