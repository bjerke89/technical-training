from odoo import fields, models, api
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

    property_type_id = fields.Many2one("property.type", string="Property Type")
    salesman = fields.Many2one("res.users", string="Salesman")
    buyer = fields.Many2one("res.partner", string="Buyer")
    tags = fields.Many2many("property.tag", string="Property Tags")
    offer_ids = fields.One2many("estate.property.offer", "property_id")
    total_area = fields.Float(compute="_compute_total_area", digits=(12,0))
    best_offer = fields.Float(compute="_highest_offer", digits=(12,2))
    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area


    @api.depends("offer_ids")
    def _highest_offer(self):
        for record in self:
            if len(record.offer_ids) > 0:
                record.best_offer = max(record.offer_ids.mapped('price'))
            else:
                record.best_offer = 0


    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden == True:
            self.garden_orientation = 'north'
            self.garden_area = '10'
        else:
           self.garden_orientation = ''
           self.garden_area = ''