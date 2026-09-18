from odoo import models, fields, api


class Condition(models.Model):
    _name = 'trade_in_program.condition'
    _description = 'Condition model for defining a baseline trade-in value for devices based on their condition'
    _rec_name = 'condition'

    condition = fields.Char(string='Condition', help='Name for the device condition, e.g. Like New, Used...')
    multiplier = fields.Float(string='Multiplier',
                              help='Factor by which the base trade-in value is adjusted based on condition')
