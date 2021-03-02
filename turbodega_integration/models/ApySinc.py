# import tb_conexion
import json
import logging
from datetime import datetime

from odoo import _, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SyncApi(models.Model):
    _name = "sync.api"

    def sync_api(self, id_product=None, model=None):
        error_data = ""
        model_1 = self.env[model].browse(id_product)
        _logger.error(model_1)
        if model_1.turbodega_type_entity == "turbodega":
            _logger.warning(model_1)
            tb_data = model_1.to_json_turbodega()
            log_data = {
                "name": "sync",
                "model_type": model,
                "type_operation": "POST",
                "json_in": json.dumps(tb_data, indent=4, sort_keys=True),
                "stages_id": "new",
            }
            event_obj = self.env["logs.request"].sudo().create(log_data)
            return_value, json_message, url_endpoint = model_1.api_send(tb_data)
            error_data = ""
            if return_value:
                model_1.turbodega_sync = True
                model_1.turbodega_creation = True
                model_1.turbodega_sync_date = datetime.now()
                transaccion_status = "done"
                json_message = json.loads(json_message)
                if model == "res.partner":
                    model_1.ref = json_message.get("id", False)
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

    def sync_update(self, id_product=None, model=None):
        error_data = ""
        model_1 = self.env[model].browse(id_product)
        if model_1.turbodega_type_entity == "turbodega" and model_1.turbodega_creation:
            tb_data = model_1.to_json_turbodega()
            log_data = {
                "name": "sync",
                "model_type": model,
                "type_operation": "PUT",
                "json_in": json.dumps(tb_data, indent=4, sort_keys=True),
                "stages_id": "new",
            }
            event_obj = self.env["logs.request"].sudo().create(log_data)
            return_value, json_message, url_endpoint = model_1.api_update_product(
                tb_data
            )
            json_message = json.loads(json_message)
            error_data = ""
            if return_value:
                model_1.turbodega_sync = True
                model_1.turbodega_sync_date = datetime.now()
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

    def scheduler_1minute(self, model=None):
        _logger.error(model)
        list_productos = self.env[model].search(
            [
                ("turbodega_creation", "=", False),
                ("turbodega_type_entity", "=", "turbodega"),
            ]
        )
        for data in list_productos:
            _logger.warning("2.1")
            self.env["sync.api"].sync_api(id_product=data.id, model=model)
        list_productos = self.env[model].search(
            [
                ("turbodega_creation", "=", True),
                ("turbodega_sync", "=", False),
                ("turbodega_type_entity", "=", "turbodega"),
            ]
        )
        for data in list_productos:
            self.env["sync.api"].sync_update(id_product=data.id, model=model)

    def sync_turbodega(self, id_turbo=None, model=None):
        record = self.env[model].browse(id_turbo)
        if not record.turbodega_creation:
            self.env["sync.api"].sync_api(id_product=record.id, model=model)
        else:
            self.env["sync.api"].sync_update(id_product=record.id, model=model)

    def sync_stockpicking(self, id_turbo=None):
        record = self.env["stock.picking"].browse(id_turbo)
        _logger.error(record.name)
        for data in record.move_ids_without_package:
            if not data.product_id.product_tmpl_id.company_id:
                msg = (
                    "producto:"
                    + data.product_id.product_tmpl_id.name
                    + "\nSin compañía"
                )
                raise UserError(_(msg))
            if data.product_id.product_tmpl_id.company_id.id != record.company_id.id:
                msg = (
                    "producto:"
                    + data.product_id.product_tmpl_id.name
                    + "\nCompañía:"
                    + data.product_id.product_tmpl_id.company_id.name
                )
                raise UserError(_(msg))

        for data in record.move_ids_without_package:
            _logger.warning("***" + data.name)
            self.sync_turbodega(data.product_id.product_tmpl_id.id, "product.template")
