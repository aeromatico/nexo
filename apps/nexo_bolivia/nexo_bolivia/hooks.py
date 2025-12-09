"""
Nexo Bolivia - Frappe Hooks
Configuración de hooks y personalizaciones para Bolivia
"""

from . import __version__ as app_version

app_name = "nexo_bolivia"
app_title = "Nexo Bolivia"
app_publisher = "Aero"
app_description = "Localización completa para Bolivia - Facturación SIN, Impuestos, Nómina"
app_email = "admin@aero.bo"
app_license = "GNU General Public License (v3)"
app_version = app_version

# Apps
required_apps = ["frappe", "erpnext", "nexo_core"]

# Regional Settings
# -----------------
# Configuración regional por defecto para Bolivia
default_regional_settings = {
    "country": "Bolivia",
    "currency": "BOB",
    "time_zone": "America/La_Paz",
    "date_format": "dd/mm/yyyy",
    "number_format": "#.###,##",
    "first_day_of_week": "Monday",
}

# Document Events
# ---------------
doc_events = {
    "Sales Invoice": {
        "validate": [
            "nexo_bolivia.tax_engine.validators.validate_invoice_for_bolivia",
            "nexo_bolivia.tax_engine.iva.apply_iva_to_invoice",
            "nexo_bolivia.tax_engine.it.apply_it_to_invoice",
        ],
        # SIN Integration - Facturación Electrónica
        "on_submit": [
            "nexo_bolivia.sin_integration.hooks.on_submit_sales_invoice",
            "nexo_bolivia.reports.audit.audit_trail.log_sales_invoice_submit",  # Auditoría
        ],
        "on_cancel": "nexo_bolivia.sin_integration.hooks.on_cancel_sales_invoice",
    },
    "Purchase Invoice": {
        "validate": [
            "nexo_bolivia.tax_engine.validators.validate_invoice_for_bolivia",
            "nexo_bolivia.tax_engine.iva.apply_iva_to_invoice",
        ],
        "on_submit": [
            "nexo_bolivia.reports.audit.audit_trail.log_purchase_invoice_submit",  # Auditoría
        ],
    },
    "Payment Entry": {
        "on_submit": "nexo_bolivia.tax_engine.it.apply_it_to_payment",
    },
    # Payroll - Nómina Bolivia
    "Salary Slip": {
        "validate": [
            "nexo_bolivia.payroll.validators.validate_salary_slip_bolivia",
            "nexo_bolivia.payroll.validators.validate_salary_slip_dates",
            "nexo_bolivia.payroll.afp.apply_afp_to_salary_slip",
            "nexo_bolivia.payroll.validators.validate_afp_in_salary_slip",
        ],
    },
    "Employee": {
        "validate": [
            "nexo_bolivia.payroll.validators.validate_employee_nit",
            "nexo_bolivia.payroll.validators.validate_salary_increase",
        ],
    },
}

# Scheduled Tasks
# ---------------
scheduler_events = {
    "daily": [
        "nexo_bolivia.sin_integration.hooks.daily_cufd_renewal",  # Renovar CUFD diariamente
        "nexo_bolivia.sin_integration.hooks.sync_pending_invoices",  # Sincronizar facturas pendientes
        "nexo_bolivia.reports.audit.compliance_checker.run_daily_compliance_check",  # Verificar compliance diariamente
    ],
    "hourly": [
        "nexo_bolivia.sin_integration.hooks.check_siat_connection",  # Verificar conexión SIAT cada hora
    ],
    "monthly": [
        "nexo_bolivia.payroll.aguinaldo.check_aguinaldo_payment",  # Verificar pago de aguinaldo (21 Jun, 21 Dic)
    ],
}

# Fixtures
# --------
# Datos iniciales para Bolivia
fixtures = [
    {
        "dt": "Country",
        "filters": [["name", "=", "Bolivia"]],
    },
    {
        "dt": "Currency",
        "filters": [["name", "=", "BOB"]],
    },
    # Plan contable boliviano
    {
        "dt": "Account",
        "filters": [["account_number", "like", "BO-%"]],
    },
    # Impuestos Bolivia
    {
        "dt": "Tax Category",
        "filters": [["name", "in", ["IVA 13%", "IT 3%", "IUE 25%"]]],
    },
    # Departamentos de Bolivia
    {
        "dt": "Territory",
        "filters": [["parent_territory", "=", "Bolivia"]],
    },
]

# Jinja Methods
# -------------
jinja = {
    "methods": [
        "nexo_bolivia.utils.format_nit",
        "nexo_bolivia.utils.format_bolivian_currency",
        "nexo_bolivia.sin_integration.qr.generate_qr_code",
    ],
}

# Override Print Formats
# ----------------------
# Formatos de impresión personalizados para Bolivia
override_doctype_dashboards = {
    "Sales Invoice": "nexo_bolivia.dashboards.sales_invoice_dashboard",
}

# Website
# -------
website_route_rules = [
    {"from_route": "/factura/<invoice_id>", "to_route": "factura_electronica"},
]

# Regional Reports
# ----------------
# Reportes específicos para Bolivia
regional_overrides = {
    "Bolivia": {
        "erpnext.regional.report.gstr_1.gstr_1.execute":
            "nexo_bolivia.reports.libro_ventas_iva.libro_ventas_iva.execute",
        "erpnext.regional.report.gstr_2.gstr_2.execute":
            "nexo_bolivia.reports.libro_compras_iva.libro_compras_iva.execute",
    }
}

# API Whitelist
# -------------
# Endpoints para integración SIN y Compliance
