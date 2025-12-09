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
}

# Scheduled Tasks
# ---------------
scheduler_events = {
    "daily": [
        "nexo_core.tasks.daily.cleanup_expired_sessions",
        "nexo_core.tasks.daily.update_tenant_metrics",
        "nexo_core.doctype.tenant_usage.tenant_usage.collect_metrics",
    ],
    "hourly": [
        "nexo_core.tasks.hourly.check_tenant_quotas",
    ],
    "weekly": [
        "nexo_core.provisioning.site_creator.cleanup_old_backups",
    ],
}

# Website
# -------
website_route_rules = [
    {"from_route": "/tenant/<path:tenant_name>", "to_route": "tenant"},
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
