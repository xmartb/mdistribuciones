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
    last_json = fields.Char(string="json")

    def api_send(self, tb_data):
        if not self.company_id:
            raise UserError(_("Company no selected."))
        return api_send_product(
            tb_data, self.company_id.token, self.company_id.product_url
        )

    def api_update_product(self, tb_data):
        if not self.company_id:
            raise UserError(_("Company no selected."))
        return api_update_product(
            tb_data, self.company_id.token, self.company_id.product_url
        )

    def update_related(self):
        producto_product_1 = self.env["product.product"].search(
            [("product_tmpl_id", "=", self.id)]
        )
        _logger.error(producto_product_1)
        for product_product in producto_product_1:
            mrp_bom_line_1 = self.env["mrp.bom.line"].search(
                [("product_id", "=", product_product.id)]
            )
            _logger.error(mrp_bom_line_1)
            for mrp_bom_line in mrp_bom_line_1:
                mrp_bom_1 = self.env["mrp.bom"].browse(mrp_bom_line.bom_id.id)
                _logger.error(mrp_bom_1)
                self.env["sync.api"].sync_update(
                    id_product=mrp_bom_1.product_tmpl_id.id, model="product.template"
                )
                # self.env["sync.api"].sync_turbodega(
                #     mrp_bom_1.product_tmpl_id.id, "product.template"
                # )

    def to_json_turbodega(self):
        stock_level = 0
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
        tax = False
        if producto_1.taxes_id:
            tax = producto_1.taxes_id[0].id
        manufacturer = False
        if producto_1.seller_ids:
            manufacturer = producto_1.seller_ids[0].name.name
        stock_warehouse_1 = self.env["stock.warehouse"].search(
            [("company_id", "=", producto_1.company_id.id)]
        )
        for warehouse in stock_warehouse_1:
            producto_product_1.with_context(
                warehouse=warehouse.id
            )._compute_quantities()
            stock_level += producto_product_1.with_context(
                warehouse=warehouse.id
            ).virtual_available
        _logger.warning(producto_product_1.virtual_available)
        tb_data = {
            "resourceId": self.company_id.resourceId,
            "distributorSKU": str(producto_product_1.id).zfill(5),
            "distributorProductId": producto_1.default_code,
            "openerp_product_uom": producto_1.uom_id.id,
            "name": producto_1.name,
            "displayName": producto_1.name or "",
            "description": producto_1.description or "",
            "manufacturer": manufacturer or "",
            "brand": producto_1.product_brand_id.name or "",
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
