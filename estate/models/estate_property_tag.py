from odoo import fields, models


class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Estate Property Tag"

    _name_must_be_unique = models.Constraint("UNIQUE(name)", "Name must be unique")

    name = fields.Char(required=True)
