# import tb_conexion
import json
import logging
from datetime import datetime

from odoo import _, fields, models
from odoo.exceptions import UserError

from .TbConexion import api_get_resourceid

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = "res.company"

    product_url = fields.Char(
        string="Url Product", default="https://dev.turbodega.com/api/dc/products"
    )
    partner_url = fields.Char(
        string="Url Partner", default="https://dev.turbodega.com/api/dc/stores"
    )
    resourceId_url = fields.Char(
        string="Url ResourceId", default="https://dev.turbodega.com/api/dc"
    )
    resourceId = fields.Char(string="ResourceId", readonly="True")
    token = fields.Char(string="Token")
    default_location = fields.Many2one("stock.location")
    turbodega_sync = fields.Boolean(string="Sync", default=False)
    turbodega_sync_date = fields.Datetime("datetime")

    def obtain_resourceId(self):
        for record in self:
            if not record.token:
                raise UserError(_("No token available."))
            transaccion_status = ""
            record.resourceId = ""
            error_data = ""
            tb_data = {}
            log_data = {
                "name": "sync",
                "model_type": "res.company",
                "type_operation": "GET",
                "json_in": json.dumps(tb_data, indent=4, sort_keys=True),
                "stages_id": "new",
            }
            event_obj = self.env["logs.request"].sudo().create(log_data)
            return_value, json_message, url_endpoint = api_get_resourceid(
                tb_data, record.token, record.resourceId_url
            )
            json_data = json.loads(json_message)
            if return_value:
                record.resourceId = json_data.get("resourceId", False)
                record.turbodega_sync = True
                record.turbodega_sync_date = datetime.now()
                transaccion_status = "done"
            else:
                transaccion_status = "error"
                error_data = json_data.get("message", False)
            event_obj.update(
                {
                    "json_out": json.dumps(json_message, indent=4, sort_keys=True),
                    "error_details": error_data,
                    "stages_id": transaccion_status,
                    "endpoint": url_endpoint,
                }
            )
