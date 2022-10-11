from odoo import fields, models

class PropertyTags(models.Model):
    _name = "property.tag"
    _description = "Property Tags"
    _sql_constraints = [
        ("check_name", "UNIQUE(name)", "The name must be unique"),
    ]
    _order = "name"
    name = fields.Char(required=True)
    color = fields.Integer("Color Index")