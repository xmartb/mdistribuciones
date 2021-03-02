# import tb_conexion
import json
import logging
from datetime import datetime

from odoo import fields, models

from .TbConexion import api_get_resourceid

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = "res.company"

    resourceId = fields.Char(string="ResourceId", readonly="True")
    token = fields.Char(string="Token")
    turbodega_sync = fields.Boolean(string="Sync", default=False)
    turbodega_sync_date = fields.Datetime("datetime")

    def obtain_resourceId(self):
        for record in self:
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
                tb_data, record.token
            )
            if return_value:
                json_data = json.loads(json_message)
                record.resourceId = json_data["resourceId"]
                record.turbodega_sync = True
                record.turbodega_sync_date = datetime.now()
                transaccion_status = "done"
            else:
                transaccion_status = "error"
                error_data = json_message["faultcode"]
            event_obj.update(
                {
                    "json_out": json.dumps(json_message, indent=4, sort_keys=True),
                    "error_details": error_data,
                    "stages_id": transaccion_status,
                    "endpoint": url_endpoint,
                }
            )
