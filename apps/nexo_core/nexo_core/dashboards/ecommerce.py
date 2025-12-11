# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

"""E-Commerce Dashboard"""

import frappe
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@frappe.whitelist(methods=['GET'])
def get_ecommerce_dashboard(company=None, period='This Month'):
    """Dashboard e-commerce completo"""
    try:
        if not company:
            company = frappe.defaults.get_user_default('company')

        date_range = _get_period_dates(period)

        # Ventas online (desde Online Order)
        online_orders = frappe.db.count(
            'Online Order',
            {
                'company': company,
                'status': 'Delivered',
                'creation': ['>=', date_range['start']],
                'creation': ['<=', date_range['end']]
            }
        )

        online_sales = frappe.db.get_value(
            'Online Order',
            {
                'company': company,
                'status': 'Delivered',
                'creation': ['>=', date_range['start']],
                'creation': ['<=', date_range['end']]
            },
            'SUM(grand_total)'
        )
        online_sales = online_sales[0] if online_sales else 0

        # Órdenes pendientes
        pending_orders = frappe.db.count(
            'Online Order',
            {
                'company': company,
                'status': 'Pending'
            }
        )

        # Carrito promedio
        avg_cart = online_sales / online_orders if online_orders > 0 else 0

        # Tasa de abandono de carrito (placeholder)
        cart_abandonment_rate = 0  # Requeriría tabla de carritos abandonados

        # Top productos online
        top_products = frappe.get_all(
            'Online Order Item',
            filters={
                'parent': frappe.get_all(
                    'Online Order',
                    filters={
                        'company': company,
                        'creation': ['>=', date_range['start']],
                        'creation': ['<=', date_range['end']]
                    },
                    pluck='name'
                )
            },
            group_by='item_code',
            fields=['item_code', 'SUM(qty) as total_qty', 'SUM(amount) as total_amount'],
            order_by='total_amount DESC',
            limit_page_length=5
        )

        # Métodos de pago más usados
        payment_methods = frappe.get_all(
            'Online Order',
            filters={
                'company': company,
                'creation': ['>=', date_range['start']],
                'creation': ['<=', date_range['end']]
            },
            group_by='payment_method',
            fields=['payment_method', 'COUNT(name) as count'],
            order_by='count DESC'
        )

        return {
            'success': True,
            'dashboard': {
                'total_online_orders': online_orders,
                'total_online_sales': float(online_sales or 0),
                'pending_orders': pending_orders,
                'average_cart': float(avg_cart or 0),
                'cart_abandonment_rate': cart_abandonment_rate,
                'top_products': [
                    {
                        'item_code': p['item_code'],
                        'qty': float(p['total_qty'] or 0),
                        'amount': float(p['total_amount'] or 0)
                    } for p in top_products
                ],
                'payment_methods': [
                    {
                        'method': m['payment_method'],
                        'count': m['count']
                    } for m in payment_methods
                ],
                'period': period,
                'generated_at': frappe.utils.now()
            }
        }

    except Exception as e:
        logger.error(f"Error generating e-commerce dashboard: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'dashboard': {}
        }


def _get_period_dates(period):
    """Obtiene rango de fechas para un período"""
    today = datetime.now().date()

    if period == 'This Month':
        start = today.replace(day=1)
        if today.month == 12:
            end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        return {'start': start, 'end': end}

    else:
        return {'start': today.replace(day=1), 'end': today}
