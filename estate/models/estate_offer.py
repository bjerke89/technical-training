from email.policy import default
from odoo import fields, models, api
from datetime import date,timedelta

class EstateOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate Offers"

    price = fields.Float()
    status = fields.Selection(
        string='Status',
        selection=[('accpeted', 'Accepted'), ('refused', 'Refused')],
        help='Select status of offer',
        copy=False
    )
    partner_id = fields.Many2one("res.partner", string="Partner")
    property_id = fields.Many2one("estate.property", required=True)
    validity = fields.Integer(default=7)
    date_deadline = fields.Date(compute="_compute_validity_date", inverse="_inverse_compute_validity_date")

    @api.depends("create_date", "validity")
    def _compute_validity_date(self):
        for record in self:
            if not record.create_date:
                record.date_deadline = fields.datetime.now() + timedelta(days=record.validity)
            else:
                record.date_deadline = record.create_date + timedelta(days=record.validity)
    
    def _inverse_compute_validity_date(self):
        for record in self:
            if not record.date_deadline:
                record.date_deadline = record.date_deadline
            else:
                record.date_deadline = fields.datetime.now()
    