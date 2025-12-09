# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

import frappe
import json
from frappe import _
from datetime import datetime, timedelta


@frappe.whitelist(methods=['GET'])
def get_platform_metrics():
    """
    Get global platform metrics

    GET /api/method/nexo_core.api.metrics_api.get_platform_metrics

    Returns:
        dict: Platform metrics
    """
    try:
        # Total tenants statistics
        total_tenants = frappe.db.count("Tenant")
        active_tenants = frappe.db.count("Tenant", {"status": "Active"})
        trial_tenants = frappe.db.count("Tenant", {"status": "Trial"})
        suspended_tenants = frappe.db.count("Tenant", {"status": "Suspended"})

        # Tenants created this month
        first_day_month = frappe.utils.today().replace(day=1)
        tenants_this_month = frappe.db.count("Tenant", {
            "created_at": [">=", first_day_month]
        })

        # Revenue statistics
        revenue_data = calculate_revenue()

        # Storage statistics
        storage_data = calculate_storage_usage()

        # Most used features
        plan_distribution = get_plan_distribution()

        return {
            "success": True,
            "metrics": {
                "tenants": {
                    "total": total_tenants,
                    "active": active_tenants,
                    "trial": trial_tenants,
                    "suspended": suspended_tenants,
                    "this_month": tenants_this_month
                },
                "revenue": revenue_data,
                "storage": storage_data,
                "plans": plan_distribution,
                "timestamp": frappe.utils.now()
            }
        }

    except Exception as e:
        frappe.log_error(f"Error getting platform metrics: {str(e)}", "Metrics API")
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }


@frappe.whitelist(methods=['GET'])
def get_tenant_usage_report(tenant_name, from_date=None, to_date=None):
    """
    Get usage report for a specific tenant

    GET /api/method/nexo_core.api.metrics_api.get_tenant_usage_report?tenant_name=empresa1&from_date=2024-01-01&to_date=2024-12-31

    Args:
        tenant_name: Name of the tenant
        from_date: Start date (default: 30 days ago)
        to_date: End date (default: today)

    Returns:
        dict: Usage report
    """
    try:
        if not frappe.db.exists("Tenant", tenant_name):
            return {
                "success": False,
                "message": f"El tenant '{tenant_name}' no existe"
            }

        # Set default dates if not provided
        if not to_date:
            to_date = frappe.utils.today()
        if not from_date:
            to_date_obj = datetime.strptime(to_date, "%Y-%m-%d")
            from_date = str(to_date_obj - timedelta(days=30))

        # Get usage report from TenantUsage
        from nexo_core.doctype.tenant_usage.tenant_usage import TenantUsage
        report = TenantUsage.get_tenant_usage_report(tenant_name, from_date, to_date)

        return {
            "success": True,
            "report": report
        }

    except Exception as e:
        frappe.log_error(f"Error getting usage report: {str(e)}", "Metrics API")
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }


@frappe.whitelist(methods=['GET'])
def get_tenant_quota_status(tenant_name):
    """
    Get quota status for a tenant

    GET /api/method/nexo_core.api.metrics_api.get_tenant_quota_status?tenant_name=empresa1

    Args:
        tenant_name: Name of the tenant

    Returns:
        dict: Quota status
    """
    try:
        if not frappe.db.exists("Tenant", tenant_name):
            return {
                "success": False,
                "message": f"El tenant '{tenant_name}' no existe"
            }

        tenant = frappe.get_doc("Tenant", tenant_name)
        quota_status = tenant.check_quota_exceeded()

        return {
            "success": True,
            "tenant": tenant_name,
            "quota_status": quota_status
        }

    except Exception as e:
        frappe.log_error(f"Error getting quota status: {str(e)}", "Metrics API")
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }


@frappe.whitelist(methods=['GET'])
def get_top_tenants(metric="storage", limit=10):
    """
    Get top tenants by specified metric

    GET /api/method/nexo_core.api.metrics_api.get_top_tenants?metric=storage&limit=10

    Args:
        metric: Metric to sort by (storage, users, api_calls, etc.)
        limit: Number of results to return

    Returns:
        dict: Top tenants
    """
    try:
        # Get latest usage for each tenant
        usages = frappe.db.sql("""
            SELECT DISTINCT tenant, storage_used_mb, active_users, api_calls
            FROM `tabTenant Usage`
            WHERE date = (SELECT MAX(date) FROM `tabTenant Usage`)
            ORDER BY {metric} DESC
            LIMIT {limit}
        """.format(metric=metric, limit=limit), as_dict=True)

        # Get tenant information
        results = []
        for usage in usages:
            tenant_doc = frappe.get_doc("Tenant", usage.get('tenant'))
            results.append({
                "tenant_name": tenant_doc.tenant_name,
                "status": tenant_doc.status,
                "subscription_plan": tenant_doc.subscription_plan,
                "storage_used_mb": usage.get('storage_used_mb'),
                "active_users": usage.get('active_users'),
                "api_calls": usage.get('api_calls')
            })

        return {
            "success": True,
            "metric": metric,
            "count": len(results),
            "top_tenants": results
        }

    except Exception as e:
        frappe.log_error(f"Error getting top tenants: {str(e)}", "Metrics API")
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }


def calculate_revenue():
    """
    Calculate revenue metrics

    Returns:
        dict: Revenue data
    """
    try:
        active_tenants = frappe.get_all(
            "Tenant",
            filters={"status": "Active"},
            fields=["subscription_plan"]
        )

        total_revenue = 0
        for tenant in active_tenants:
            plan = frappe.get_doc("Subscription Plan", tenant.subscription_plan)
            total_revenue += plan.price_monthly

        return {
            "monthly_revenue": total_revenue,
            "active_subscriptions": len(active_tenants)
        }

    except Exception:
        return {
            "monthly_revenue": 0,
            "active_subscriptions": 0
        }


def calculate_storage_usage():
    """
    Calculate total storage usage

    Returns:
        dict: Storage data
    """
    try:
        result = frappe.db.sql("""
            SELECT SUM(storage_used_mb) as total_storage
            FROM `tabTenant Usage`
            WHERE date = (SELECT MAX(date) FROM `tabTenant Usage`)
        """, as_dict=True)

        total_storage_mb = result[0].get('total_storage') or 0

        return {
            "total_storage_mb": total_storage_mb,
            "total_storage_gb": total_storage_mb / 1024
        }

    except Exception:
        return {
            "total_storage_mb": 0,
            "total_storage_gb": 0
        }


def get_plan_distribution():
    """
    Get distribution of tenants by plan

    Returns:
        dict: Plan distribution
    """
    try:
        plans = frappe.db.sql("""
            SELECT subscription_plan, COUNT(*) as count
            FROM `tabTenant`
            WHERE status = 'Active'
            GROUP BY subscription_plan
        """, as_dict=True)

        return {
            "plan_distribution": plans
        }

    except Exception:
        return {
            "plan_distribution": []
        }


@frappe.whitelist(methods=['POST'])
def collect_daily_metrics():
    """
    Manually trigger daily metrics collection

    POST /api/method/nexo_core.api.metrics_api.collect_daily_metrics

    Returns:
        dict: Operation result
    """
    try:
        from nexo_core.doctype.tenant_usage.tenant_usage import TenantUsage

        TenantUsage.collect_metrics()

        return {
            "success": True,
            "message": "Métricas diarias recolectadas exitosamente"
        }

    except Exception as e:
        frappe.log_error(f"Error collecting metrics: {str(e)}", "Metrics API")
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }
