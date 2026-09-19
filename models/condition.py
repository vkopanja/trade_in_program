from odoo import models, fields


class Condition(models.Model):
    _name = 'trade_in_program.condition'
    _description = 'Condition model for defining a baseline trade-in value for devices based on their condition'
    _rec_name = 'condition'
    _order = 'sequence, id'
    _sql_constraints = [
        ('multiplier_range', 'CHECK(multiplier >= 0 AND multiplier <= 1)',
         'The payout must be between 0% and 100%.'),
    ]

    condition = fields.Char(string='Condition', required=True,
                            help='Name for the device condition, e.g. Like New, Used...')
    multiplier = fields.Float(string='Payout', required=True,
                              help='Share of the device base trade-in value paid for this condition')
    sequence = fields.Integer(default=10)
