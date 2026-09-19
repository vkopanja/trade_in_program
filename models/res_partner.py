from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    trade_in_count = fields.Integer(
        compute='_compute_trade_in_count', groups='trade_in_program.group_trade_in_user')

    def _compute_trade_in_count(self):
        groups = self.env['trade_in_program.trade_in']._read_group(
            domain=[('partner_id', 'in', self.ids)], fields=['partner_id'], groupby=['partner_id'])
        counts = {group['partner_id'][0]: group['partner_id_count'] for group in groups}
        for partner in self:
            partner.trade_in_count = counts.get(partner.id, 0)

    def action_view_trade_ins(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('trade_in_program.trade_in_action')
        action['domain'] = [('partner_id', '=', self.id)]
        # Replaces the menu's default "New" filter, so the list shows every request the button counted
        action['context'] = {'default_partner_id': self.id}
        return action
