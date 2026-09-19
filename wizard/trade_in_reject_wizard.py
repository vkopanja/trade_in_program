from odoo import _, fields, models
from odoo.exceptions import UserError


class TradeInRejectWizard(models.TransientModel):
    _name = 'trade_in_program.reject.wizard'
    _description = 'Reject Trade-In request'

    trade_in_id = fields.Many2one('trade_in_program.trade_in', required=True)
    rejection_reason = fields.Text(string='Rejection Reason', required=True)

    def action_reject(self):
        self.ensure_one()

        if not self.rejection_reason or not self.rejection_reason.strip():
            raise UserError(_("Please enter a rejection reason"))
        if self.trade_in_id.state != 'new':
            raise UserError(_(
                "%(reference)s has already been processed and can no longer be rejected.",
                reference=self.trade_in_id.reference,
            ))

        self.trade_in_id.write({
            'state': 'rejected',
            'rejection_reason': self.rejection_reason
        })
