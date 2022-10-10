from odoo import fields, models

class PropertyType(models.Model):
    _name = "property.type"
    _description = "Property Types"

    name = fields.Char(required=True)