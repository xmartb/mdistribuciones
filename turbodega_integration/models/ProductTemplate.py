import logging

from odoo import _, fields, models
from odoo.exceptions import UserError

from .TbConexion import api_send_product, api_update_product

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    turbodega_sync = fields.Boolean(string="Sync", default=False)
    turbodega_creation = fields.Boolean(string="Create", default=False)
    turbodega_sync_date = fields.Datetime("datetime")
    turbodega_type_entity = fields.Selection(
        [
            ("turbodega", "Producto turbodega"),
            ("otro", "Otro"),
        ],
        "Tipo",
        default="",
        track_visibility="always",
    )

    resultado = fields.Text(string="Result", readonly="True")

    def api_send(self, tb_data):
        return api_send_product(tb_data, self.company_id.token)

    def api_update_product(self, tb_data):
        return api_update_product(tb_data, self.company_id.token)

    def to_json_turbodega(self):
        producto_1 = self.env["product.template"].browse(self.id)
        producto_product_1 = self.env["product.product"].search(
            [("product_tmpl_id", "=", self.id)]
        )
        if len(producto_product_1) > 1:
            raise UserError(_("template " + producto_1.name + " has variants."))
        pricelist_1 = self.env["product.pricelist.item"].search(
            [("product_tmpl_id", "=", self.id)]
        )
        prices_lines = []
        if pricelist_1:
            for line in pricelist_1:
                tb_prices = {
                    "maxQuantity": 0,
                    "minQuantity": 0,
                    "default": 0,
                    "price": line.fixed_price,
                }
                prices_lines.append(tb_prices)
        tb_data = {}
        # stock_level = "-"
        # if producto_1.type == "product":
        tax = False
        if producto_1.taxes_id:
            tax = producto_1.taxes_id[0].id
        manufacturer = False
        if producto_1.seller_ids:
            manufacturer = producto_1.seller_ids[0].name.name
        stock_level = producto_1.virtual_available
        tb_data = {
            "resourceId": self.company_id.resourceId,
            # "distributorSKU": str(producto_1.id).zfill(5),
            "distributorSKU": str(producto_product_1.id).zfill(5),
            "distributorProductId": producto_1.default_code,
            "openerp_product_uom": producto_1.uom_id.id,
            "name": producto_1.name,
            "displayName": producto_1.name or "",
            "description": producto_1.description or "",
            "manufacturer": manufacturer or "",
            "brand": producto_1.product_brand_id.name or "",
            # "stockLevel": producto_1.qty_available,
            "stockLevel": stock_level,
            "price": producto_product_1.standard_price_tax_included,
            "prices": prices_lines or False,
            "salesUnitPrice": producto_product_1.standard_price_tax_included,
            "salesUnitType": producto_1.uom_id.name or False,
            "salesUnitPerBox": False,
            "weight": producto_1.weight,
            "currency": producto_1.currency_id.name,
            "openerp_tax_id": tax,
        }
        if producto_1.list_price:
            tb_data["prices"] = prices_lines
        return tb_data

    def scheduler_1minute(self):
        self.env["sync.api"].scheduler_1minute(model="product.template")

    def sync_turbodega(self):
        for record in self:
            self.env["sync.api"].sync_turbodega(
                id_turbo=record.id, model="product.template"
            )

    def to_json_validation(self, vals, list_values):
        for data in list_values:
            if vals.get(data, False):
                return True
        return False
