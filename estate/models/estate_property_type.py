from odoo import fields, models


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Estate Property Type"

    _name_must_be_unique = models.Constraint("UNIQUE(name)", "Name must be unique")

    name = fields.Char(required=True)
