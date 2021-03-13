import logging

from odoo import fields, models

from .TbConexion import api_send_partner, api_update_partner

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    turbodega_sync = fields.Boolean(string="Sync", default=False)
    turbodega_sync_date = fields.Datetime("datetime")
    turbodega_creation = fields.Boolean(string="Create", default=False)
    dniresponsable = fields.Char(string="Dni responsable")
    turbodega_type_entity = fields.Selection(
        [
            ("turbodega", "Tienda turbodega"),
            ("otro", "Otro"),
        ],
        "Tipo",
        required=True,
        default="",
        track_visibility="always",
    )
    last_json = fields.Char(string="json")

    def update_related(self):
        _logger.warning("related")

    def api_send(self, tb_data):
        return api_send_partner(
            tb_data, self.env.company.token, self.company_id.partner_url
        )

    def api_update_product(self, tb_data):
        return api_update_partner(
            tb_data, self.env.company.token, self.company_id.partner_url
        )

    def to_json_turbodega(self):
        partner_1 = self.env["res.partner"].browse(self.id)
        tb_geocoord = [partner_1.partner_latitude, partner_1.partner_longitude]

        tb_address = {
            "street1": partner_1.street,
            "town": partner_1.state_id.name or "",
            "postalCode": partner_1.zip or "",
            "adminDivision": partner_1.city_id.name or partner_1.city,
            "countryCode": partner_1.country_id.code,
            "geocoord": tb_geocoord,
        }
        doc_ruc = ""
        doc_dni = ""
        if partner_1.country_id.code == "PE":
            if self.l10n_latam_identification_type_id.name == "RUC":
                doc_ruc = self.vat
                doc_dni = ""
            if self.l10n_latam_identification_type_id.name == "DNI":
                doc_ruc = ""
                doc_dni = self.vat
        else:
            doc_ruc = self.vat
            doc_dni = ""

        tb_data = {
            "code": str(partner_1.id).zfill(5),
            "name": partner_1.name,
            "address": tb_address,
            "dni": doc_dni,
            "ruc": doc_ruc,
            "mobile": partner_1.mobile or "",
            "businessType": partner_1.industry_id.name or False,
            "notes": partner_1.comment or "",
        }
        return tb_data

    def to_json_validation(self, vals, list_values):
        for data in list_values:
            if vals.get(data, False):
                return True
        return False

    def scheduler_1minute(self):
        self.env["sync.api"].scheduler_1minute(model="res.partner")

    def sync_turbodega(self):
        for record in self:
            self.env["sync.api"].sync_turbodega(id_turbo=record.id, model="res.partner")
