from email.policy import default
from odoo import fields, models, api
from datetime import date,timedelta
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero

class EstateOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate Offers"
    _order = "price desc"

    price = fields.Float()
    status = fields.Selection(
        string='Status',
        selection=[('accepted', 'Accepted'), ('refused', 'Refused')],
        help='Select status of offer',
        copy=False
    )
    partner_id = fields.Many2one("res.partner", string="Partner")
    property_id = fields.Many2one("estate.property", required=True)

    property_type_id = fields.Many2one(
        "property.type", related="property_id.property_type_id", string="Property Type", store=True
    )
    validity = fields.Integer(default=7)
    date_deadline = fields.Date(compute="_compute_validity_date", inverse="_inverse_compute_validity_date")

    @api.model
    def create(self, vals):
        if vals.get("property_id") and vals.get("price"):
            prop = self.env["estate.property"].browse(vals["property_id"])
            # We check if the offer is higher than the existing offers
            if prop.offer_ids:
                max_offer = max(prop.mapped("offer_ids.price"))
                if float_compare(vals["price"], max_offer, precision_rounding=0.01) <= 0:
                    raise UserError("The offer must be higher than %.2f" % max_offer)
            prop.state = "offer_received"
        return super().create(vals)

    @api.depends("create_date", "validity")
    def _compute_validity_date(self):
        for record in self:
            if not record.create_date:
                record.date_deadline = fields.datetime.now() + timedelta(days=record.validity)
            else:
                record.date_deadline = record.create_date + timedelta(days=record.validity)
    
    def _inverse_compute_validity_date(self):
        for offer in self:
            date = offer.create_date.date() if offer.create_date else fields.Date.today()
            offer.validity = (offer.date_deadline - date).days
    
    def offer_accept(self):
        if "accepted" in self.mapped("property_id.offer_ids.status"):
            raise UserError("An offer as already been accepted.")
        self.write(
            {
                "status": "accepted",
            }
        )
        return self.mapped("property_id").write(
            {
                "state": "offer_accepted",
                "selling_price": self.price,
                "buyer": self.partner_id.id,
            }
        )

    def offer_refuse(self):
        self.status = 'refused'
        return True

    
    