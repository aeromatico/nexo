# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

"""
Executive Dashboards for Nexo ERP
Financial, Sales, Inventory, HR, and E-commerce dashboards
"""

from .financial import get_financial_dashboard
from .sales import get_sales_dashboard
from .inventory import get_inventory_dashboard
from .hr import get_hr_dashboard
from .ecommerce import get_ecommerce_dashboard

__all__ = [
    'get_financial_dashboard',
    'get_sales_dashboard',
    'get_inventory_dashboard',
    'get_hr_dashboard',
    'get_ecommerce_dashboard',
]
