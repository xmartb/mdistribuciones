from odoo import api, fields, models

import odoo.addons.decimal_precision as dp


class ProductProduct(models.Model):
    _inherit = "product.product"

    # Column Section
    standard_price_tax_included = fields.Float(
        compute="_compute_standard_price_tax_included",
        string="Precios incluidos",
        digits=dp.get_precision("Product Price"),
        help="Precio con impuestos incluidos.",
    )

    @api.depends("standard_price", "taxes_id")
    def _compute_standard_price_tax_included(self):
        for product in self:
            info = product.taxes_id.compute_all(
                product.lst_price, quantity=1, product=product
            )
            product.standard_price_tax_included = info["total_included"]
