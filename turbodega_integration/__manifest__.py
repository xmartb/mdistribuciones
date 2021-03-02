{
    "name": "TURBODEGA - REST API CLIENT -TEST",
    "version": "14.0.1.1.0",
    "author": "Tecnativa",
    "authors": ["Erick Delgado"],
    "category": "Tools",
    "support": "odoo.com",
    "summary": """
    Extends the REST API TURBODEGA
    agregar un botón que obtenga el resourceid

    """,
    "license": "LGPL-3",
    "demo": [],
    "depends": [
        "base",
        "base_automation",
        "sale_management",
        "contacts",
        "stock",
        "account",
        "purchase",
        "product_brand",
        "base_address_extended",
        "l10n_latam_base",
        "l10n_latam_invoice_document",
        "l10n_pe",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/product_view.xml",
        "views/res_company_view.xml",
        "views/partner_view.xml",
        "report/sale_report_templates.xml",
        "report/stock_picking_report_templates.xml",
        "views/base_automation.xml",
        "views/view_product_product.xml",
        "views/logs_request_view.xml",
    ],
    "installable": True,
}
