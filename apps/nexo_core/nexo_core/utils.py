"""
Nexo Core - Utility Functions
Helper functions for multi-tenant operations
"""

import frappe


def get_tenant_info(tenant_name=None):
    """
    Get information about a tenant

    Args:
        tenant_name: Name of the tenant site (optional, defaults to current site)

    Returns:
        dict: Tenant information
    """
    if not tenant_name:
        tenant_name = frappe.local.site

    return {
        "name": tenant_name,
        "site": tenant_name,
        # Add more tenant info as needed
    }


def get_currency_symbol(currency_code="BOB"):
    """
    Get currency symbol for Bolivia or specified currency

    Args:
        currency_code: ISO currency code (default: BOB)

    Returns:
        str: Currency symbol
    """
    symbols = {
        "BOB": "Bs",
        "USD": "$",
        "EUR": "€",
    }
    return symbols.get(currency_code, currency_code)


def create_tenant(tenant_name, admin_email, admin_password):
    """
    Create a new tenant site

    Args:
        tenant_name: Name for the new tenant site
        admin_email: Email for the admin user
        admin_password: Password for the admin user

    Returns:
        dict: Created tenant information
    """
    # TODO: Implement tenant creation logic
    # This will use Frappe's bench API to create new site
    pass


def get_tenant_usage(tenant_name=None):
    """
    Get resource usage statistics for a tenant

    Args:
        tenant_name: Name of the tenant (optional)

    Returns:
        dict: Usage statistics (storage, users, etc.)
    """
    # TODO: Implement usage tracking
    pass
