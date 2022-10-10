from odoo import fields, models

class PropertyTags(models.Model):
    _name = "property.tag"
    _description = "Property Tags"

    name = fields.Char(required=True)