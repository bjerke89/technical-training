from odoo import fields, models
from datetime import datetime
from datetime import timedelta

class RealEstate(models.Model):
    _name = "estate.property"
    _description = "Real Estate Property Model"

    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(copy=False,default=lambda self: fields.datetime.now() + timedelta(days=90))
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(copy=False,readonly=True)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        string='Orientation',
        selection=[('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')],
        help='Select Orientation'
    )
    active = fields.Boolean()
    state = fields.Selection(
        string='State',
        selection=[('new', 'New'), ('offer_received', 'Offer Received'), ('offer_accpeted', 'Offer Accpeted'), ('sold', 'Sold'), ('cancelled', 'Cancelled')],
        help='Select Orientation',
        required=True,
        copy=False
    )

