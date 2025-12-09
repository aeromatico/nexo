# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

import frappe
from datetime import datetime, timedelta


@frappe.whitelist()
def get_admin_dashboard_data():
    """
    Get dashboard data for super admin

    Dashboard includes:
    - Total tenants (active, trial, suspended, cancelled)
    - Tenants created this month
    - Monthly revenue projection
    - Storage usage statistics
    - Top 10 tenants by usage
    - Alerts and recent events

    Returns:
        dict: Dashboard data
    """
    try:
        # Get tenant statistics
        total_tenants = frappe.db.count("Tenant")
        active_tenants = frappe.db.count("Tenant", {"status": "Active"})
        trial_tenants = frappe.db.count("Tenant", {"status": "Trial"})
        suspended_tenants = frappe.db.count("Tenant", {"status": "Suspended"})
        cancelled_tenants = frappe.db.count("Tenant", {"status": "Cancelled"})

        # Tenants created this month
        first_day_month = frappe.utils.today().replace(day=1)
        tenants_this_month = frappe.db.count("Tenant", {
            "created_at": [">=", first_day_month]
        })

        # Revenue calculation
        active_plans = frappe.db.sql("""
            SELECT subscription_plan, COUNT(*) as count
            FROM `tabTenant`
            WHERE status = 'Active'
            GROUP BY subscription_plan
        """, as_dict=True)

        monthly_revenue = 0
        for plan_data in active_plans:
            plan = frappe.get_doc("Subscription Plan", plan_data.subscription_plan)
            monthly_revenue += plan.price_monthly * plan_data.get('count', 0)

        # Storage statistics
        storage_result = frappe.db.sql("""
            SELECT
                SUM(storage_used_mb) as total_storage,
                MAX(storage_used_mb) as max_storage
            FROM `tabTenant Usage`
            WHERE date = (SELECT MAX(date) FROM `tabTenant Usage`)
        """, as_dict=True)

        total_storage_mb = storage_result[0].get('total_storage') or 0
        max_storage_mb = storage_result[0].get('max_storage') or 0

        # Top 10 tenants by storage
        top_tenants = frappe.db.sql("""
            SELECT tu.tenant, tu.storage_used_mb, t.status, t.subscription_plan
            FROM `tabTenant Usage` tu
            JOIN `tabTenant` t ON tu.tenant = t.name
            WHERE tu.date = (SELECT MAX(date) FROM `tabTenant Usage`)
            ORDER BY tu.storage_used_mb DESC
            LIMIT 10
        """, as_dict=True)

        # Recent events (new tenants, suspensions, etc.)
        recent_tenants = frappe.get_all(
            "Tenant",
            fields=["name", "tenant_name", "status", "created_at"],
            order_by="created_at desc",
            limit_page_length=5
        )

        # Trial tenants expiring soon
        upcoming_trial_end = frappe.utils.add_days(frappe.utils.today(), 7)
        expiring_trials = frappe.get_all(
            "Tenant",
            filters={
                "status": "Trial",
                "trial_end_date": ["<=", upcoming_trial_end],
                "trial_end_date": [">=", frappe.utils.today()]
            },
            fields=["name", "tenant_name", "trial_end_date"],
            order_by="trial_end_date asc"
        )

        # Tenants exceeding quota
        quota_warnings = get_quota_warnings()

        return {
            "success": True,
            "dashboard": {
                "tenants": {
                    "total": total_tenants,
                    "active": active_tenants,
                    "trial": trial_tenants,
                    "suspended": suspended_tenants,
                    "cancelled": cancelled_tenants,
                    "created_this_month": tenants_this_month
                },
                "revenue": {
                    "monthly": monthly_revenue,
                    "currency": "BOB"
                },
                "storage": {
                    "total_mb": total_storage_mb,
                    "total_gb": total_storage_mb / 1024,
                    "max_single_tenant_mb": max_storage_mb
                },
                "top_tenants": top_tenants,
                "recent_activity": {
                    "new_tenants": recent_tenants,
                    "expiring_trials": expiring_trials,
                    "quota_warnings": quota_warnings
                },
                "timestamp": frappe.utils.now()
            }
        }

    except Exception as e:
        frappe.log_error(f"Error getting admin dashboard data: {str(e)}", "Admin Dashboard")
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }


def get_quota_warnings():
    """
    Get tenants that have exceeded quotas

    Returns:
        list: Tenants with quota issues
    """
    try:
        warnings = []
        active_tenants = frappe.get_all("Tenant", filters={"status": "Active"}, fields=["name"])

        for tenant_data in active_tenants:
            tenant = frappe.get_doc("Tenant", tenant_data.name)
            quota_status = tenant.check_quota_exceeded()

            if quota_status["users"]["exceeded"] or quota_status["storage"]["exceeded"]:
                warnings.append({
                    "tenant": tenant_data.name,
                    "user_quota_exceeded": quota_status["users"]["exceeded"],
                    "storage_quota_exceeded": quota_status["storage"]["exceeded"]
                })

        return warnings

    except Exception:
        return []


@frappe.whitelist()
def get_dashboard_charts():
    """
    Get chart data for dashboard visualization

    Returns:
        dict: Chart data
    """
    try:
        # Chart 1: Tenants by status
        status_chart = frappe.db.sql("""
            SELECT status, COUNT(*) as count
            FROM `tabTenant`
            GROUP BY status
        """, as_dict=True)

        # Chart 2: Revenue trend (last 30 days)
        revenue_trend = []
        for i in range(30, -1, -1):
            date = frappe.utils.add_days(frappe.utils.today(), -i)
            # TODO: Calculate revenue for each day
            revenue_trend.append({
                "date": str(date),
                "revenue": 0
            })

        # Chart 3: New tenants trend (last 30 days)
        tenants_trend = []
        for i in range(30, -1, -1):
            date = frappe.utils.add_days(frappe.utils.today(), -i)
            count = frappe.db.count("Tenant", {
                "created_at": [">=", f"{date} 00:00:00"],
                "created_at": ["<", f"{date} 23:59:59"]
            })
            tenants_trend.append({
                "date": str(date),
                "count": count
            })

        return {
            "success": True,
            "charts": {
                "status_distribution": status_chart,
                "revenue_trend": revenue_trend,
                "new_tenants_trend": tenants_trend
            }
        }

    except Exception as e:
        frappe.log_error(f"Error getting charts: {str(e)}", "Admin Dashboard")
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }
