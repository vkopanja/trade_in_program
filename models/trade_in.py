from odoo import _, models, fields, api
from odoo.exceptions import UserError, ValidationError

TRADE_IN_STATES = [
    ('new', 'New'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
]


class TradeIn(models.Model):
    _name = 'trade_in_program.trade_in'
    _description = 'Trade-In model for managing trade-in offers and requests'
    _rec_name = 'reference'
    _sql_constraints = [
        ('reference_unique', 'unique(reference)', 'Reference must be unique'),
        ('submission_token_unique', 'unique(submission_token)', 'This form has already been submitted'),
    ]

    partner_id = fields.Many2one('res.partner', string='Contact', required=True)
    # Contact details as the customer entered them; suggested from the contact when created in the backend
    customer_name = fields.Char(string='Customer Name', required=True, compute='_compute_customer_contact',
                                store=True, readonly=False, precompute=True)
    customer_email = fields.Char(string='Customer Email', required=True, compute='_compute_customer_contact',
                                 store=True, readonly=False, precompute=True)
    device_id = fields.Many2one('trade_in_program.device', string='Device', required=True)
    condition_id = fields.Many2one('trade_in_program.condition', string='Condition', required=True)

    base_value = fields.Float(readonly=True, copy=False)
    multiplier = fields.Float(string='Payout', readonly=True, copy=False)
    offer_value = fields.Float(compute='_compute_offer', store=True)
    reference = fields.Char(
        string='Reference', required=True, readonly=True, copy=False, index=True,
        default=lambda self: _('New'),
    )
    state = fields.Selection(
        TRADE_IN_STATES, string='Status', default='new', required=True, readonly=True, copy=False,
    )
    rejection_reason = fields.Text(string='Rejection Reason')
    # One-time token of the website form that created the request, so a resubmit doesn't create a duplicate
    submission_token = fields.Char(readonly=True, copy=False)

    @api.depends('partner_id')
    def _compute_customer_contact(self):
        for rec in self:
            rec.customer_name = rec.partner_id.name
            rec.customer_email = rec.partner_id.email

    @api.onchange('device_id', 'condition_id')
    def _onchange_inputs(self):
        self.base_value = self.device_id.base_trade_in_value
        self.multiplier = self.condition_id.multiplier

    @api.constrains('state', 'rejection_reason')
    def _check_rejection_reason(self):
        for rec in self:
            if rec.state == 'rejected' and not rec.rejection_reason:
                raise ValidationError(_("A rejection reason is required when the status is set to 'Rejected'."))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('device_id') and not vals.get('base_value'):
                vals['base_value'] = self.env['trade_in_program.device'] \
                    .browse(vals['device_id']).base_trade_in_value
            if vals.get('condition_id') and not vals.get('multiplier'):
                vals['multiplier'] = self.env['trade_in_program.condition'] \
                    .browse(vals['condition_id']).multiplier
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
        if self.filtered(lambda r: r.state != 'new'):
            raise UserError(_("Only new requests can be approved."))
        self.write({'state': 'approved'})

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
