from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Estate Property tutorial"
    _order = "id DESC"

    _ensure_positive_selling_price = models.Constraint(
        "CHECK(selling_price > 0)", "Selling price must be strictly positive"
    )

    _ensure_positive_expected_price = models.Constraint(
        "CHECK(expected_price > 0)", "Expected price must be strictly positive"
    )

    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(
        copy=False, default=fields.Date.add(fields.Date.today(), months=3)
    )
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        [
            ("north", "North"),
            ("south", "South"),
            ("east", "East"),
            ("west", "West"),
        ]
    )
    active = fields.Boolean(default=True)
    state = fields.Selection(
        [
            ("new", "New"),
            ("offer_received", "Offer Received"),
            ("offer_accepted", "Offer Accepted"),
            ("sold", "Sold"),
            ("canceled", "Canceled"),
        ],
        required=True,
        copy=False,
        default="new",
    )

    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
    seller_id = fields.Many2one(
        "res.users", string="Seller", default=lambda self: self.env.user
    )
    buyer_id = fields.Many2one("res.partner", string="Buyer", copy=False)
    tag_ids = fields.Many2many("estate.property.tag", string="Tags")
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")

    total_area = fields.Integer(
        compute="_compute_total_area", string="Total Area (sqm)"
    )

    best_price = fields.Float(string="Best Offer", compute="_compute_best_price")

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for property in self:
            property.total_area = property.living_area + property.garden_area

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for property in self:
            if property.offer_ids:
                property.best_price = max(property.offer_ids.mapped("price"))
            else:
                property.best_price = 0.0

    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = "north"
        else:
            self.garden_area = 0
            self.garden_orientation = None

    def action_sold(self):
        if "canceled" in self.mapped("state"):
            raise UserError("Cancelled properties cannot be sold.")
        return self.write({"state": "sold"})

    def action_cancelled(self):
        if "sold" in self.mapped("state"):
            raise UserError("Sold properties cannot be cancelled.")
        return self.write({"state": "canceled"})

    @api.constrains("selling_price", "expected_price")
    def _check_price_difference(self):
        for property in self:
            if (
                not float_is_zero(property.selling_price, precision_rounding=0.01)
                and float_compare(
                    property.selling_price,
                    property.expected_price * 90.0 / 100.0,
                    precision_rounding=0.01,
                )
                < 0
            ):
                raise ValidationError(
                    "The selling price must be at least 90% of the expected price"
                )

    @api.ondelete(at_uninstall=False)
    def _check_deletion_availability(self):
        for property in self:
            if property.state not in ("new", "canceled"):
                raise UserError("Only new and canceled properties can be deleted.")
