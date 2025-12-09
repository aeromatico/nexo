# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

import frappe


@frappe.whitelist()
def get_tenant_dashboard_data(tenant_name=None):
    """
    Get dashboard data for a specific tenant

    Dashboard includes:
    - Current vs plan limits (users, storage)
    - Usage metrics (storage, database size)
    - Activity metrics (API calls, emails, invoices)
    - Recent invoices
    - Storage breakdown
    - Alerts and recommendations

    Args:
        tenant_name: Name of the tenant (optional, defaults to current site)

    Returns:
        dict: Dashboard data
    """
    try:
        if not tenant_name:
            tenant_name = frappe.local.site

        if not frappe.db.exists("Tenant", tenant_name):
            return {
                "success": False,
                "message": f"El tenant '{tenant_name}' no existe"
            }

        tenant = frappe.get_doc("Tenant", tenant_name)
        plan_limits = tenant.get_plan_limits()
        usage_metrics = tenant.get_usage_metrics()
        quota_status = tenant.check_quota_exceeded()

        # Get latest usage record
        latest_usage = None
        try:
            latest_usage = frappe.get_last_doc(
                "Tenant Usage",
                filters={"tenant": tenant_name},
                order_by="date desc"
            )
        except Exception:
            pass

        # Calculate percentages
        user_percentage = (usage_metrics["active_users"] / plan_limits["max_users"] * 100) if plan_limits["max_users"] > 0 else 0
        storage_percentage = (usage_metrics["storage_used_mb"] / (plan_limits["max_storage_gb"] * 1024) * 100) if plan_limits["max_storage_gb"] > 0 else 0

        # Get subscription info
        plan = frappe.get_doc("Subscription Plan", tenant.subscription_plan)

        # Get recent activity
        recent_invoices = get_recent_invoices(tenant_name)

        # Get alerts
        alerts = get_tenant_alerts(tenant)

        return {
            "success": True,
            "dashboard": {
                "tenant": {
                    "name": tenant.name,
                    "tenant_name": tenant.tenant_name,
                    "company_name": tenant.company_name,
                    "status": tenant.status,
                    "created_at": str(tenant.created_at),
                    "site_name": tenant.site_name
                },
                "subscription": {
                    "plan_name": plan.plan_name,
                    "price_monthly": plan.price_monthly,
                    "billing_cycle": plan.billing_cycle,
                    "currency": plan.currency
                },
                "quotas": {
                    "users": {
                        "used": usage_metrics["active_users"],
                        "limit": plan_limits["max_users"],
                        "percentage": user_percentage,
                        "status": "critical" if user_percentage >= 90 else "warning" if user_percentage >= 70 else "ok"
                    },
                    "storage": {
                        "used_mb": usage_metrics["storage_used_mb"],
                        "used_gb": usage_metrics["storage_used_mb"] / 1024,
                        "limit_gb": plan_limits["max_storage_gb"],
                        "percentage": storage_percentage,
                        "status": "critical" if storage_percentage >= 90 else "warning" if storage_percentage >= 70 else "ok"
                    },
                    "database_size_mb": usage_metrics["database_size_mb"]
                },
                "activity": {
                    "api_calls": usage_metrics["api_calls"],
                    "emails_sent": usage_metrics["email_sent"],
                    "invoices_generated": usage_metrics["invoices_generated"]
                },
                "recent_invoices": recent_invoices,
                "alerts": alerts,
                "recommendations": get_recommendations(quota_status, user_percentage, storage_percentage),
                "timestamp": frappe.utils.now()
            }
        }

    except Exception as e:
        frappe.log_error(f"Error getting tenant dashboard data: {str(e)}", "Tenant Dashboard")
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }


def get_recent_invoices(tenant_name, limit=5):
    """
    Get recent invoices for the tenant

    Args:
        tenant_name: Name of the tenant
        limit: Number of invoices to return

    Returns:
        list: Recent invoices
    """
    try:
        # TODO: Query Sales Invoice from the tenant's site
        # For now, return empty list
        return []

    except Exception:
        return []


def get_tenant_alerts(tenant):
    """
    Get alerts for the tenant

    Args:
        tenant: Tenant document

    Returns:
        list: Alerts
    """
    alerts = []

    try:
        # Check trial expiration
        if tenant.status == "Trial" and tenant.trial_end_date:
            today = frappe.utils.today()
            trial_days_left = (tenant.trial_end_date - today).days

            if trial_days_left <= 3 and trial_days_left > 0:
                alerts.append({
                    "type": "warning",
                    "title": "Trial por vencer",
                    "message": f"Su período de prueba vence en {trial_days_left} días. Considere actualizar a un plan pago.",
                    "action": "upgrade_plan"
                })
            elif trial_days_left <= 0:
                alerts.append({
                    "type": "critical",
                    "title": "Trial vencido",
                    "message": "Su período de prueba ha vencido. Contacte con soporte para continuar.",
                    "action": "contact_support"
                })

        # Check quota warnings
        quota_status = tenant.check_quota_exceeded()

        if quota_status["users"]["exceeded"]:
            alerts.append({
                "type": "critical",
                "title": "Límite de usuarios excedido",
                "message": f"Ha excedido el límite de usuarios ({quota_status['users']['used']}/{quota_status['users']['limit']})",
                "action": "upgrade_plan"
            })

        if quota_status["storage"]["exceeded"]:
            alerts.append({
                "type": "critical",
                "title": "Límite de almacenamiento excedido",
                "message": f"Ha excedido el límite de almacenamiento",
                "action": "upgrade_plan"
            })

    except Exception:
        pass

    return alerts


def get_recommendations(quota_status, user_percentage, storage_percentage):
    """
    Get recommendations based on usage

    Args:
        quota_status: Quota status information
        user_percentage: User usage percentage
        storage_percentage: Storage usage percentage

    Returns:
        list: Recommendations
    """
    recommendations = []

    if user_percentage >= 80:
        recommendations.append({
            "type": "upgrade",
            "title": "Actualizar plan",
            "message": "Está usando la mayoría de su cuota de usuarios. Considere actualizar a un plan con más usuarios."
        })

    if storage_percentage >= 80:
        recommendations.append({
            "type": "storage",
            "title": "Limpiar almacenamiento",
            "message": "Está usando la mayoría de su cuota de almacenamiento. Considere limpiar datos antiguos o actualizar el plan."
        })

    return recommendations


@frappe.whitelist()
def get_tenant_charts(tenant_name=None):
    """
    Get chart data for tenant dashboard

    Args:
        tenant_name: Name of the tenant

    Returns:
        dict: Chart data
    """
    try:
        if not tenant_name:
            tenant_name = frappe.local.site

        if not frappe.db.exists("Tenant", tenant_name):
            return {
                "success": False,
                "message": "Tenant not found"
            }

        # Get usage history (last 30 days)
        usage_history = frappe.get_all(
            "Tenant Usage",
            filters={"tenant": tenant_name},
            fields=["date", "active_users", "storage_used_mb", "api_calls"],
            order_by="date asc",
            limit_page_length=30
        )

        return {
            "success": True,
            "charts": {
                "usage_history": usage_history
            }
        }

    except Exception as e:
        frappe.log_error(f"Error getting charts: {str(e)}", "Tenant Dashboard")
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }
