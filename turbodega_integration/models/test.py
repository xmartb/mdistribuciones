# import datetime
import xmlrpc.client

url = "http://localhost:13069"
db = "devel"
username = "admin"
password = "admin"

# url = "http://192.168.42.66:8069"
# db = "erpnube"
# username = "edelgado@erpnube.com"
# password = "2846er.-"


# Conexion con Base de datos
common = xmlrpc.client.ServerProxy("{}/xmlrpc/2/common".format(url))
uid = common.authenticate(db, username, password, {})
# print (common.version())

models = xmlrpc.client.ServerProxy("{}/xmlrpc/2/object".format(url))
conex_result = models.execute_kw(
    db,
    uid,
    password,
    "res.partner",
    "check_access_rights",
    ["read"],
    {"raise_exception": False},
)

# user = models.execute_kw(
#     db, uid, password, "res.users", "search_read", [[["login", "=", "apiuser"]]]
# )

# Buscar la factura con saldo del cliente
# invoice_ids = models.execute_kw(db, uid, password,
#    'account.move', 'search',
#    [[['type', '=', 'in_invoice'],
#    	['currency_id', '=', 162]
#        ]])

# invoice_ids = [12996]

# print(invoice_ids)

result = models.execute_kw(
    db,
    uid,
    password,
    "sale.order",
    "create",
    [
        {
            "name": "NAME0002",
            "partner_id": 5,
            "order_line": [
                [
                    0,
                    "virtual_254",
                    {
                        "sequence": 10,
                        "display_type": False,
                        "product_uom_qty": 1,
                        "qty_delivered_manual": 0,
                        "customer_lead": 0,
                        "product_packaging": False,
                        "price_unit": 1,
                        "discount": 0,
                        "product_id": 54,
                        "product_template_id": 44,
                        "name": "[REF3] PRODUCTO_TEMPLATE3",
                        "route_id": False,
                        "product_uom": 1,
                        "tax_id": [[6, False, [5]]],
                    },
                ],
                [
                    0,
                    "virtual_255",
                    {
                        "sequence": 11,
                        "display_type": False,
                        "product_uom_qty": 1,
                        "qty_delivered_manual": 0,
                        "customer_lead": 0,
                        "product_packaging": False,
                        "price_unit": 1,
                        "discount": 0,
                        "product_id": 54,
                        "product_template_id": 44,
                        "name": "[REF3] PRODUCTO_TEMPLATE3",
                        "route_id": False,
                        "product_uom": 1,
                        "tax_id": [[6, False, [5]]],
                    },
                ],
            ],
        }
    ],
)

# partner_id = partner[0]['id']
# partner_name = partner[0]['name']


# print(result)
