from email.policy import default
from odoo import fields, models, api
from datetime import datetime
from datetime import timedelta
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero

class RealEstate(models.Model):
    _name = "estate.property"
    _description = "Real Estate Property Model"
    _sql_constraints = [
        ("check_expected_price", "CHECK(expected_price >= 0)", "The expected price must be strictly positive"),
        ("check_selling_price", "CHECK(selling_price >= 0)", "The offer price must be positive"),
    ]
    _order = "id desc"

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
    active = fields.Boolean(default=True)
    state = fields.Selection(
        string='State',
        selection=[('new', 'New'), ('offer_received', 'Offer Received'), ('offer_accepted', 'Offer Accpeted'), ('sold', 'Sold'), ('cancelled', 'Cancelled')],
        help='Select Orientation',
        required=True,
        copy=False,
        default="new"
    )

    property_type_id = fields.Many2one("property.type", string="Property Type")
    user_id = fields.Many2one("res.users", string="Salesman")
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

    def action_mark_as_sold(self):
        for record in self:
            if record.state != 'cancelled':
                record.state = 'sold'
            else:
                raise UserError('Sold properties cannot be Cancelled')
        return True

    def action_cancel(self):
        for record in self:
            if record.state != 'sold':
                record.state = 'cancelled'
            else:
                raise UserError('Cancelled properties cannot be Sold')
        return True


    @api.constrains("expected_price", "selling_price")
    def _check_price_difference(self):
        for prop in self:
            if (
                not float_is_zero(prop.selling_price, precision_rounding=0.01)
                and float_compare(prop.selling_price, prop.expected_price * 90.0 / 100.0, precision_rounding=0.01) < 0
            ):
                raise ValidationError(
                    "The selling price must be at least 90% of the expected price! "
                    + "You must reduce the expected price if you want to accept this offer."
                )

    def unlink(self):
        if not set(self.mapped("state")) <= {"new", "canceled"}:
            raise UserError("Only new and canceled properties can be deleted.")
        return super().unlink()