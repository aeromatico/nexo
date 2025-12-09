# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

import frappe
import json
from frappe import _


@frappe.whitelist(methods=['POST'])
def create_tenant(data):
    """
    Create a new tenant with automatic provisioning

    POST /api/method/nexo_core.api.tenant_api.create_tenant

    Args:
        data (str): JSON string with tenant data
            {
                "tenant_name": "empresa1",
                "subdomain": "empresa1",
                "company_name": "Empresa Ltda",
                "nit": "1234567890123",
                "admin_email": "admin@empresa.com",
                "admin_password": "secure_password",
                "subscription_plan": "Basic"
            }

    Returns:
        dict: Created tenant information
    """
    try:
        if isinstance(data, str):
            data = json.loads(data)

        # Validations
        required_fields = ['tenant_name', 'subdomain', 'company_name', 'nit', 'admin_email', 'admin_password', 'subscription_plan']
        for field in required_fields:
            if not data.get(field):
                return {
                    "success": False,
                    "message": f"El campo '{field}' es obligatorio"
                }

        # Create tenant document
        tenant = frappe.new_doc("Tenant")
        tenant.tenant_name = data.get("tenant_name")
        tenant.subdomain = data.get("subdomain")
        tenant.company_name = data.get("company_name")
        tenant.nit = data.get("nit")
        tenant.admin_email = data.get("admin_email")
        tenant.admin_password = data.get("admin_password")
        tenant.subscription_plan = data.get("subscription_plan")
        tenant.status = "Trial"

        tenant.insert(ignore_permissions=True)

        return {
            "success": True,
            "message": f"Tenant {tenant.name} creado exitosamente",
            "tenant": {
                "name": tenant.name,
                "subdomain": tenant.subdomain,
                "site_name": tenant.site_name,
                "status": tenant.status
            }
        }

    except frappe.ValidationError as e:
        return {
            "success": False,
            "message": str(e)
        }
    except Exception as e:
        frappe.log_error(f"Error creating tenant: {str(e)}", "Tenant API")
        return {
            "success": False,
            "message": f"Error al crear tenant: {str(e)}"
        }


@frappe.whitelist(methods=['GET'])
def get_tenant_info(tenant_name):
    """
    Get information about a specific tenant

    GET /api/method/nexo_core.api.tenant_api.get_tenant_info?tenant_name=empresa1

    Args:
        tenant_name: Name of the tenant

    Returns:
        dict: Tenant information
    """
    try:
        if not frappe.db.exists("Tenant", tenant_name):
            return {
                "success": False,
                "message": f"El tenant '{tenant_name}' no existe"
            }

        tenant = frappe.get_doc("Tenant", tenant_name)

        # Get plan limits
        plan_limits = tenant.get_plan_limits()

        # Get usage metrics
        usage_metrics = tenant.get_usage_metrics()

        return {
            "success": True,
            "tenant": {
                "name": tenant.name,
                "tenant_name": tenant.tenant_name,
                "subdomain": tenant.subdomain,
                "site_name": tenant.site_name,
                "company_name": tenant.company_name,
                "status": tenant.status,
                "subscription_plan": tenant.subscription_plan,
                "created_at": str(tenant.created_at),
                "activated_at": str(tenant.activated_at) if tenant.activated_at else None,
                "trial_end_date": str(tenant.trial_end_date) if tenant.trial_end_date else None,
                "plan_limits": plan_limits,
                "usage_metrics": usage_metrics
            }
        }

    except Exception as e:
        frappe.log_error(f"Error getting tenant info: {str(e)}", "Tenant API")
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }


@frappe.whitelist(methods=['GET'])
def get_all_tenants(filters=None, limit_page_length=20):
    """
    Get list of all tenants with optional filters

    GET /api/method/nexo_core.api.tenant_api.get_all_tenants?filters={"status":"Active"}

    Args:
        filters (str): JSON string with filters (optional)
        limit_page_length: Number of results to return

    Returns:
        dict: List of tenants
    """
    try:
        filter_dict = {}
        if filters:
            if isinstance(filters, str):
                filter_dict = json.loads(filters)
            else:
                filter_dict = filters

        tenants = frappe.get_all(
            "Tenant",
            filters=filter_dict,
            fields=["name", "tenant_name", "status", "subscription_plan", "created_at", "company_name"],
            limit_page_length=limit_page_length,
            order_by="created_at desc"
        )

        return {
            "success": True,
            "count": len(tenants),
            "tenants": tenants
        }

    except Exception as e:
        frappe.log_error(f"Error getting tenants: {str(e)}", "Tenant API")
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }


@frappe.whitelist(methods=['POST'])
def suspend_tenant(tenant_name, reason=None):
    """
    Suspend a tenant (disable access)

    POST /api/method/nexo_core.api.tenant_api.suspend_tenant

    Args:
        tenant_name: Name of the tenant
        reason: Reason for suspension (optional)

    Returns:
        dict: Operation result
    """
    try:
        if not frappe.db.exists("Tenant", tenant_name):
            return {
                "success": False,
                "message": f"El tenant '{tenant_name}' no existe"
            }

        tenant = frappe.get_doc("Tenant", tenant_name)
        tenant.suspend()

        return {
            "success": True,
            "message": f"Tenant {tenant_name} ha sido suspendido"
        }

    except Exception as e:
        frappe.log_error(f"Error suspending tenant: {str(e)}", "Tenant API")
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }


@frappe.whitelist(methods=['POST'])
def activate_tenant(tenant_name):
    """
    Activate a suspended tenant

    POST /api/method/nexo_core.api.tenant_api.activate_tenant

    Args:
        tenant_name: Name of the tenant

    Returns:
        dict: Operation result
    """
    try:
        if not frappe.db.exists("Tenant", tenant_name):
            return {
                "success": False,
                "message": f"El tenant '{tenant_name}' no existe"
            }

        tenant = frappe.get_doc("Tenant", tenant_name)
        tenant.activate()

        return {
            "success": True,
            "message": f"Tenant {tenant_name} ha sido activado"
        }

    except Exception as e:
        frappe.log_error(f"Error activating tenant: {str(e)}", "Tenant API")
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }


@frappe.whitelist(methods=['POST'])
def delete_tenant(tenant_name):
    """
    Delete a tenant completely

    POST /api/method/nexo_core.api.tenant_api.delete_tenant

    Args:
        tenant_name: Name of the tenant

    Returns:
        dict: Operation result
    """
    try:
        if not frappe.db.exists("Tenant", tenant_name):
            return {
                "success": False,
                "message": f"El tenant '{tenant_name}' no existe"
            }

        tenant = frappe.get_doc("Tenant", tenant_name)
        tenant.cancel_tenant()

        return {
            "success": True,
            "message": f"Tenant {tenant_name} ha sido cancelado y será eliminado"
        }

    except Exception as e:
        frappe.log_error(f"Error deleting tenant: {str(e)}", "Tenant API")
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }


@frappe.whitelist(methods=['POST'])
def upgrade_plan(tenant_name, new_plan):
    """
    Upgrade a tenant's subscription plan

    POST /api/method/nexo_core.api.tenant_api.upgrade_plan

    Args:
        tenant_name: Name of the tenant
        new_plan: Name of the new subscription plan

    Returns:
        dict: Operation result
    """
    try:
        if not frappe.db.exists("Tenant", tenant_name):
            return {
                "success": False,
                "message": f"El tenant '{tenant_name}' no existe"
            }

        if not frappe.db.exists("Subscription Plan", new_plan):
            return {
                "success": False,
                "message": f"El plan '{new_plan}' no existe"
            }

        tenant = frappe.get_doc("Tenant", tenant_name)
        old_plan = tenant.subscription_plan
        tenant.subscription_plan = new_plan
        tenant.save()

        return {
            "success": True,
            "message": f"Plan actualizado de {old_plan} a {new_plan}",
            "tenant": {
                "name": tenant.name,
                "subscription_plan": tenant.subscription_plan
            }
        }

    except Exception as e:
        frappe.log_error(f"Error upgrading plan: {str(e)}", "Tenant API")
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }


@frappe.whitelist(methods=['GET'])
def get_tenant_metrics(tenant_name):
    """
    Get usage metrics for a tenant

    GET /api/method/nexo_core.api.tenant_api.get_tenant_metrics?tenant_name=empresa1

    Args:
        tenant_name: Name of the tenant

    Returns:
        dict: Metrics information
    """
    try:
        if not frappe.db.exists("Tenant", tenant_name):
            return {
                "success": False,
                "message": f"El tenant '{tenant_name}' no existe"
            }

        tenant = frappe.get_doc("Tenant", tenant_name)
        metrics = tenant.get_usage_metrics()
        quota_info = tenant.check_quota_exceeded()

        return {
            "success": True,
            "tenant": tenant_name,
            "metrics": metrics,
            "quota_status": quota_info
        }

    except Exception as e:
        frappe.log_error(f"Error getting metrics: {str(e)}", "Tenant API")
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }


@frappe.whitelist(methods=['GET'])
def check_subdomain_available(subdomain):
    """
    Check if a subdomain is available for registration

    GET /api/method/nexo_core.api.tenant_api.check_subdomain_available?subdomain=empresa1

    Args:
        subdomain: Subdomain to check

    Returns:
        dict: Availability status
    """
    try:
        exists = frappe.db.exists("Tenant", {"subdomain": subdomain})

        return {
            "success": True,
            "subdomain": subdomain,
            "available": not exists
        }

    except Exception as e:
        frappe.log_error(f"Error checking subdomain: {str(e)}", "Tenant API")
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }


@frappe.whitelist(methods=['GET'])
def get_available_plans():
    """
    Get list of available subscription plans

    GET /api/method/nexo_core.api.tenant_api.get_available_plans

    Returns:
        dict: List of available plans
    """
    try:
        plans = frappe.get_all(
            "Subscription Plan",
            filters={"is_active": 1},
            fields=["name", "plan_name", "max_users", "max_storage_gb", "max_sites", "price_monthly", "price_annual", "currency"],
            order_by="price_monthly asc"
        )

        return {
            "success": True,
            "count": len(plans),
            "plans": plans
        }

    except Exception as e:
        frappe.log_error(f"Error getting plans: {str(e)}", "Tenant API")
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }
