from odoo import api, fields, models


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate Property Offer"

    price = fields.Float()
    status = fields.Selection(
        [
            ("accepted", "Accepted"),
            ("refused", "Refused"),
        ],
        copy=False,
    )
    partner_id = fields.Many2one("res.partner", required=True, string="Partner")
    property_id = fields.Many2one("estate.property", required=True, string="Property")
    validity = fields.Integer(default=7, string="Validity (days)")
    date_deadline = fields.Date(
        string="Deadline",
        compute="_compute_date_deadline",
        inverse="_inverse_date_deadline",
    )

    @api.depends("create_date", "validity")
    def _compute_date_deadline(self):
        for offer in self:
            date = fields.Date.today()
            if offer.create_date:
                date = offer.create_date.date()

            offer.date_deadline = fields.Date.add(date, days=offer.validity)

    def _inverse_date_deadline(self):
        for offer in self:
            date = fields.Date.today()
            if offer.create_date:
                date = offer.create_date.date()

            offer.validity = (offer.date_deadline - date).days
