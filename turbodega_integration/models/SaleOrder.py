import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    turbodega_sync = fields.Boolean(string="Sync", default=False)
    turbodega_sync_date = fields.Datetime("datetime")

    def api_send(self, tb_data):
        # client = TBClient()
        # return client._tb_send_product(tb_data)
        return True

    @api.model
    def create(self, vals):
        result = super(SaleOrder, self).create(vals=vals)
        # self.env["sync.api"].with_delay().sync_api(
        #     id_product=result.id, model="sale.order"
        # )
        # self.env["sync.api"].sync_api(id_product=result.id, model="sale.order")
        _logger.error(vals)
        return result

    # def write(self, vals):
    #     result = super(SaleOrder, self).write(vals)
    #     if not vals.get("turbodega_sync", False):
    #         if not vals.get("turbodega_sync_date", False):
    #             self.env["sync.api"].sync_api(self.id, model="sale.order")
    #     return result

    # def to_json_turbodega(self):
    #     so_1 = self.env["sale.order"].browse(self.id)

    #     items = []
    #     if so_1:
    #         for line in so_1.order_line:
    #             tb_product = {
    #                 "name": line.product_id.name,
    #                 "code": line.product_id.code,
    #             }
    #             tb_items = {
    #                 "product": tb_product,
    #                 "quantity": line.product_uom_qty,
    #                 "price": line.price_unit,
    #                 "discount": line.discount,
    #                 "total": line.price_total,
    #             }
    #             items.append(tb_items)

    #     tb_store = {
    #         "code": so_1.partner_id.vat,
    #         "name": so_1.partner_id.name,
    #         "status": so_1.partner_id.active,
    #     }
    #     tb_data = {
    #         "code": so_1.name,
    #         "store": tb_store,
    #         "items": items,
    #         "totalprice": so_1.amount_total,
    #         "orderdate": so_1.date_order,
    #         "notes": so_1.note,
    #     }
    #     return tb_data
