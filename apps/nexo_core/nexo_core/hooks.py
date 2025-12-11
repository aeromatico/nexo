"""
Nexo Core - Frappe Hooks
Configuration for app hooks and overrides
"""

from . import __version__ as app_version

app_name = "nexo_core"
app_title = "Nexo Core"
app_publisher = "Aero"
app_description = "Core multi-tenant and SaaS functionality for Nexo ERP"
app_email = "admin@aero.bo"
app_license = "GNU General Public License (v3)"
app_version = app_version

# Apps
# -----
required_apps = ["frappe", "erpnext"]

# DocTypes
# --------
# Document Events
# ---------------
doc_events = {
    "Tenant": {
        "after_insert": "nexo_core.provisioning.site_creator.provision_tenant_site",
        "on_trash": "nexo_core.provisioning.site_creator.cleanup_tenant_site",
    },
    "Online Order": {
        "on_submit": "nexo_core.ecommerce.orders.create_sales_invoice_from_order_hook",
    },
}

# Scheduled Tasks
# ---------------
scheduler_events = {
    "daily": [
        "nexo_core.tasks.daily.cleanup_expired_sessions",
        "nexo_core.tasks.daily.update_tenant_metrics",
        "nexo_core.doctype.tenant_usage.tenant_usage.collect_metrics",
        "nexo_core.ecommerce.orders.check_pending_orders",
        # Fase 6 - Analytics & BI
        "nexo_core.analytics.kpi_engine.KPIEngine.check_kpi_alerts",
        "nexo_core.reports.scheduler.execute_scheduled_reports",
        "nexo_core.data_warehouse.aggregator.aggregate_sales_data",
    ],
    "hourly": [
        "nexo_core.tasks.hourly.check_tenant_quotas",
        "nexo_core.ecommerce.payment_gateways.qr_simple.verify_pending_payments",
        # Fase 6 - Analytics & BI
        "nexo_core.analytics.alerts.check_all_alerts",
    ],
    "weekly": [
        "nexo_core.provisioning.site_creator.cleanup_old_backups",
    ],
    "monthly": [
        # Fase 6 - Analytics & BI
        "nexo_core.data_warehouse.aggregator.aggregate_financial_data",
    ],
}

# Website
# -------
website_route_rules = [
    {"from_route": "/tenant/<path:tenant_name>", "to_route": "tenant"},
    {"from_route": "/shop/<path:item_code>", "to_route": "product_detail"},
    {"from_route": "/cart", "to_route": "shopping_cart"},
    {"from_route": "/checkout", "to_route": "checkout"},
    {"from_route": "/my-account", "to_route": "customer_portal"},
    {"from_route": "/my-orders", "to_route": "customer_orders"},
    {"from_route": "/my-invoices", "to_route": "customer_invoices"},
    {"from_route": "/my-support", "to_route": "customer_support"},
]

# Fixtures
# --------
fixtures = [
    {
        "dt": "Custom Field",
        "filters": [["name", "in", []]],
    }
]

# Jinja
# -----
jinja = {
    "methods": [
        "nexo_core.utils.get_tenant_info",
        "nexo_core.utils.get_currency_symbol",
    ],
}

# API Whitelist
# -------------
# Functions available via REST API
# Add custom API endpoints here

# Permissions
# -----------
# permission_query_conditions = {
#     "Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }

# Document Class Override
# -----------------------
# override_doctype_class = {
#     "ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Class Dashboards
# --------------------------
# override_doctype_dashboards = {
#     "Task": "nexo_core.task.get_dashboard_data"
# }

# Exempt from CSRF
# ----------------
# Routes that don't need CSRF token
# exempt_from_csrf = ["nexo_core.api.hook"]
