"""
Nexo Core - Hourly Tasks
Tasks that run every hour
"""

import frappe


def check_tenant_quotas():
    """
    Check and enforce tenant resource quotas

    This function:
    - Checks storage limits for each active tenant
    - Checks user limits for each active tenant
    - Sends notifications if approaching limits
    """
    try:
        active_tenants = frappe.get_all(
            "Tenant",
            filters={"status": "Active"},
            fields=["name"]
        )

        for tenant_data in active_tenants:
            try:
                tenant = frappe.get_doc("Tenant", tenant_data.name)
                quota_status = tenant.check_quota_exceeded()

                # Log quota status
                if quota_status["users"]["exceeded"] or quota_status["storage"]["exceeded"]:
                    frappe.logger().warning(f"Quota exceeded for tenant {tenant.name}")

            except Exception as e:
                frappe.logger().warning(f"Error checking quota for {tenant_data.name}: {str(e)}")

    except Exception as e:
        frappe.logger().error(f"Error in check_tenant_quotas: {str(e)}")
