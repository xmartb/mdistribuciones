# import tb_conexion
import json
import logging
import time
from datetime import datetime

from odoo import _, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SyncApi(models.Model):
    _name = "sync.api"

    def sync_api(self, id_product=None, model=None):
        error_data = ""
        model_1 = self.env[model].browse(id_product)
        res_company_1 = self.env["res.company"].browse(1)
        model_1.company_id = res_company_1
        if not model_1.company_id:
            raise UserError(_("Company no selected."))
        if model_1.turbodega_type_entity == "turbodega":
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
            transaccion_status = "error"
            try:
                json_message = json.loads(json_message)
                _logger.error(tb_data)
                if return_value:
                    model_1.turbodega_sync = True
                    model_1.turbodega_creation = True
                    model_1.turbodega_sync_date = datetime.now()
                    _logger.error(tb_data)
                    model_1.last_json = tb_data
                    transaccion_status = "done"
                    if model == "res.partner":
                        model_1.ref = json_message.get("id", False)
                else:
                    transaccion_status = "error"
                    error_data = json_message.get("message", False)
            except Exception as e:
                _logger.error(e)
                error_data = e
                json_message = {"error": "error en el json de respuesta"}
            event_obj.update(
                {
                    "json_out": json.dumps(json_message, indent=4, sort_keys=True),
                    "error_details": error_data,
                    "stages_id": transaccion_status,
                    "endpoint": url_endpoint,
                    "fechaActualizacion": datetime.now(),
                }
            )

    def sync_update(self, id_product=None, model=None):
        error_data = ""
        model_1 = self.env[model].browse(id_product)
        if model_1.turbodega_type_entity == "turbodega" and model_1.turbodega_creation:
            tb_data = model_1.to_json_turbodega()
            last_json = json.dumps(tb_data)
            _logger.error(model_1.last_json == last_json)
            if model_1.last_json != last_json:
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
                time.sleep(0.02)
                json_message = json.loads(json_message)
                error_data = ""
                if return_value:
                    model_1.turbodega_sync = True
                    model_1.turbodega_sync_date = datetime.now()
                    model_1.last_json = last_json
                    transaccion_status = "done"
                else:
                    transaccion_status = "error"
                    error_data = json_message.get("message", False)
                event_obj.update(
                    {
                        "json_out": json.dumps(json_message, indent=4, sort_keys=True),
                        "error_details": error_data,
                        "stages_id": transaccion_status,
                        "endpoint": url_endpoint,
                        "fechaActualizacion": datetime.now(),
                    }
                )

    def sync_update_related(self, id_product=None, model=None):
        model_1 = self.env[model].browse(id_product)
        if model_1.turbodega_type_entity == "turbodega" and model_1.turbodega_creation:
            model_1.update_related()

    def scheduler_1minute(self, model=None):
        list_productos = self.env[model].search(
            [
                ("turbodega_creation", "=", False),
                ("turbodega_type_entity", "=", "turbodega"),
            ]
        )
        for data in list_productos:
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
        _logger.error(record.state)
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
            self.sync_turbodega(data.product_id.product_tmpl_id.id, "product.template")
        for data in record.move_ids_without_package:
            self.sync_update_related(
                id_product=data.product_id.product_tmpl_id.id, model="product.template"
            )

    def sync_mrp_bom(self, id_turbo=None):
        record = self.env["mrp.bom"].browse(id_turbo)
        if not record.product_tmpl_id.company_id:
            msg = "producto:" + record.product_tmpl_id.name + "\nSin compañía"
            raise UserError(_(msg))
        self.sync_turbodega(record.product_tmpl_id.id, "product.template")
