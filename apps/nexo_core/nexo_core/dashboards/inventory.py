# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

"""Inventory Dashboard"""

import frappe
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@frappe.whitelist(methods=['GET'])
def get_inventory_dashboard(company=None):
    """Dashboard de inventario completo"""
    try:
        if not company:
            company = frappe.defaults.get_user_default('company')

        # Valor total del inventario
        total_inventory_value = frappe.db.get_value(
            'Bin',
            {'company': company},
            'SUM(stock_value)'
        )
        total_inventory_value = total_inventory_value[0] if total_inventory_value else 0

        # Items en stock bajo
        low_stock_items = frappe.get_all(
            'Item',
            filters={'disabled': 0},
            fields=['item_code', 'item_name', 'reorder_level'],
            limit_page_length=10
        )

        # Items sin movimiento (>90 días)
        cutoff_date = (datetime.now() - timedelta(days=90)).date()
        inactive_items = frappe.db.count(
            'Stock Entry',
            {
                'posting_date': ['<', cutoff_date]
            }
        )

        # Top 10 items más rotados
        top_rotated = frappe.get_all(
            'Stock Entry Item',
            group_by='item_code',
            fields=['item_code', 'SUM(qty) as total_qty'],
            order_by='total_qty DESC',
            limit_page_length=10
        )

        return {
            'success': True,
            'dashboard': {
                'total_inventory_value': float(total_inventory_value or 0),
                'low_stock_items': len(low_stock_items),
                'inactive_items': inactive_items,
                'top_rotated_items': [
                    {'item_code': item['item_code'], 'qty': float(item['total_qty'] or 0)}
                    for item in top_rotated
                ],
                'generated_at': frappe.utils.now()
            }
        }

    except Exception as e:
        logger.error(f"Error generating inventory dashboard: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'dashboard': {}
        }
