# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

import frappe
import json
from frappe import _


@frappe.whitelist(methods=['POST'])
def provision_new_tenant(data):
    """
    Complete provisioning API endpoint

    This is a comprehensive endpoint that handles:
    1. Validation of tenant data
    2. Verification of plan availability
    3. Creation of tenant document
    4. Automatic provisioning trigger
    5. Credential generation

    POST /api/method/nexo_core.api.provisioning_api.provision_new_tenant

    Args:
        data (str): JSON string with provisioning data
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
        dict: Provisioning result with credentials
    """
    try:
        if isinstance(data, str):
            data = json.loads(data)

        # Step 1: Validate required fields
        required_fields = ['tenant_name', 'subdomain', 'company_name', 'nit', 'admin_email', 'admin_password', 'subscription_plan']
        validation_errors = []

        for field in required_fields:
            if not data.get(field):
                validation_errors.append(f"El campo '{field}' es obligatorio")

        if validation_errors:
            return {
                "success": False,
                "message": "Errores de validación",
                "errors": validation_errors
            }

        # Step 2: Verify plan exists and is active
        plan_name = data.get('subscription_plan')
        if not frappe.db.exists("Subscription Plan", plan_name):
            return {
                "success": False,
                "message": f"El plan '{plan_name}' no existe"
            }

        plan = frappe.get_doc("Subscription Plan", plan_name)
        if not plan.is_active:
            return {
                "success": False,
                "message": f"El plan '{plan_name}' no está disponible"
            }

        # Step 3: Check subdomain availability
        if frappe.db.exists("Tenant", {"subdomain": data.get('subdomain')}):
            return {
                "success": False,
                "message": f"El subdominio '{data.get('subdomain')}' ya está en uso"
            }

        # Step 4: Create tenant document
        tenant = frappe.new_doc("Tenant")
        tenant.tenant_name = data.get("tenant_name")
        tenant.subdomain = data.get("subdomain")
        tenant.company_name = data.get("company_name")
        tenant.nit = data.get("nit")
        tenant.admin_email = data.get("admin_email")
        tenant.admin_password = data.get("admin_password")
        tenant.subscription_plan = data.get("subscription_plan")
        tenant.status = "Trial"

        # Save tenant (this will trigger provisioning automatically)
        tenant.insert(ignore_permissions=True)

        # Step 5: Generate access credentials
        credentials = {
            "site_url": f"https://{tenant.site_name}",
            "admin_email": tenant.admin_email,
            "site_name": tenant.site_name,
            "note": "Las credenciales se enviarán al email del administrador una vez completado el provisioning"
        }

        return {
            "success": True,
            "message": f"Tenant {tenant.name} ha sido creado. El provisioning está en progreso",
            "tenant": {
                "name": tenant.name,
                "subdomain": tenant.subdomain,
                "site_name": tenant.site_name,
                "status": tenant.status,
                "subscription_plan": plan_name
            },
            "credentials": credentials,
            "provisioning_status": "in_progress"
        }

    except frappe.ValidationError as e:
        return {
            "success": False,
            "message": f"Error de validación: {str(e)}"
        }
    except Exception as e:
        frappe.log_error(f"Error in tenant provisioning: {str(e)}", "Provisioning API")
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }


@frappe.whitelist(methods=['GET'])
def check_subdomain_available(subdomain):
    """
    Check if a subdomain is available for registration

    GET /api/method/nexo_core.api.provisioning_api.check_subdomain_available?subdomain=empresa1

    Args:
        subdomain: Subdomain to check

    Returns:
        dict: Availability status
    """
    try:
        # Validate subdomain format
        import re
        if not re.match(r'^[a-z0-9-]+$', subdomain.lower()):
            return {
                "success": False,
                "message": "El subdominio contiene caracteres inválidos",
                "available": False
            }

        if len(subdomain) < 3 or len(subdomain) > 63:
            return {
                "success": False,
                "message": "El subdominio debe tener entre 3 y 63 caracteres",
                "available": False
            }

        # Check reserved words
        reserved = ['admin', 'api', 'www', 'mail', 'ftp', 'smtp', 'nexo', 'erp']
        if subdomain.lower() in reserved:
            return {
                "success": False,
                "message": f"El subdominio '{subdomain}' está reservado",
                "available": False
            }

        # Check if already in use
        exists = frappe.db.exists("Tenant", {"subdomain": subdomain.lower()})

        return {
            "success": True,
            "subdomain": subdomain.lower(),
            "available": not exists,
            "message": "Subdominio disponible" if not exists else "Subdominio ya está en uso"
        }

    except Exception as e:
        frappe.log_error(f"Error checking subdomain: {str(e)}", "Provisioning API")
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }


@frappe.whitelist(methods=['GET'])
def get_provisioning_status(tenant_name):
    """
    Get the provisioning status of a tenant

    GET /api/method/nexo_core.api.provisioning_api.get_provisioning_status?tenant_name=empresa1

    Args:
        tenant_name: Name of the tenant

    Returns:
        dict: Provisioning status information
    """
    try:
        if not frappe.db.exists("Tenant", tenant_name):
            return {
                "success": False,
                "message": f"El tenant '{tenant_name}' no existe"
            }

        tenant = frappe.get_doc("Tenant", tenant_name)

        return {
            "success": True,
            "tenant": tenant_name,
            "status": tenant.status,
            "site_name": tenant.site_name,
            "created_at": str(tenant.created_at),
            "activated_at": str(tenant.activated_at) if tenant.activated_at else None,
            "provisioning_complete": tenant.status == "Active"
        }

    except Exception as e:
        frappe.log_error(f"Error getting status: {str(e)}", "Provisioning API")
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }


@frappe.whitelist(methods=['POST'])
def retry_provisioning(tenant_name):
    """
    Retry provisioning for a failed tenant

    POST /api/method/nexo_core.api.provisioning_api.retry_provisioning

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

        # Trigger provisioning again
        frappe.enqueue(
            "nexo_core.provisioning.site_creator.provision_tenant_site",
            tenant_name=tenant_name,
            queue="default",
            timeout=3600,
            is_async=True
        )

        return {
            "success": True,
            "message": f"Provisioning reenviado para tenant {tenant_name}"
        }

    except Exception as e:
        frappe.log_error(f"Error retrying provisioning: {str(e)}", "Provisioning API")
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }
