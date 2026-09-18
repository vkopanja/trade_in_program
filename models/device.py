from odoo import models, fields


class Device(models.Model):
    _name = 'trade_in_program.device'
    _description = 'Device model for managing trade-in devices'
    _rec_name = 'model_name'

    model_name = fields.Char(string='Device Name', required=True, help='Name of the device, e.g. iPhone 12, Samsung Galaxy S21...')
    base_trade_in_value = fields.Float(string='Base Trade-In Value', required=True)
    active = fields.Boolean(string='Active', default=True, help='Indicates whether the device is active for trade-in offers')