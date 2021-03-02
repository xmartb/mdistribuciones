# import logging

# from odoo import models

# _logger = logging.getLogger(__name__)


# class Picking(models.Model):
#     _inherit = "stock.picking"

#     def write(self, vals):
#         result = super(Picking, self).write(vals)
#         print("------------->", vals)
#         # for record in self:
#         #     for data in record.move_ids_without_package:
#         #         data.product_id.turbodega_sync = False
#         # print("------------->", vals)
#         # if self.to_json_validation(vals, ["date_done"]):
#         #     self.env["sync.api"].scheduler_1minute(model="product.template")
#         return result


# #     # def to_json_validation(self, vals, list_values):
# #     #     for data in list_values:
# #     #         if vals.get(data, False):
# #     #             return True
# #     #     return False
