# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

"""
Sales Dashboard
Revenue, products, customers, and conversion metrics
"""

import frappe
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@frappe.whitelist(methods=['GET'])
def get_sales_dashboard(company=None, period='This Month'):
    """
    Dashboard de ventas:
    - Total ventas (monto y cantidad)
    - Ventas por canal (POS, Online, Manual)
    - Top 10 productos más vendidos
    - Top 10 clientes
    - Tasa de conversión (cotizaciones → ventas)
    - Ticket promedio
    - Tendencia de ventas (gráfico últimos 6 meses)
    - Ventas por región (si aplica)
    """
    try:
        if not company:
            company = frappe.defaults.get_user_default('company')

        date_range = _get_period_dates(period)

        # Total ventas
        total_sales = frappe.db.get_value(
            'Sales Invoice',
            {
                'company': company,
                'docstatus': 1,
                'posting_date': ['>=', date_range['start']],
                'posting_date': ['<=', date_range['end']]
            },
            'SUM(grand_total)'
        )
        total_sales = total_sales[0] if total_sales else 0

        # Cantidad de facturas
        invoice_count = frappe.db.count(
            'Sales Invoice',
            {
                'company': company,
                'docstatus': 1,
                'posting_date': ['>=', date_range['start']],
                'posting_date': ['<=', date_range['end']]
            }
        )

        # Ticket promedio
        avg_ticket = total_sales / invoice_count if invoice_count > 0 else 0

        # Top 10 productos
        top_products = frappe.get_all(
            'Sales Invoice Item',
            filters={
                'parent': frappe.get_all(
                    'Sales Invoice',
                    filters={
                        'company': company,
                        'docstatus': 1,
                        'posting_date': ['>=', date_range['start']],
                        'posting_date': ['<=', date_range['end']]
                    },
                    pluck='name'
                )
            },
            group_by='item_code',
            fields=['item_code', 'item_name', 'SUM(qty) as total_qty', 'SUM(amount) as total_amount'],
            order_by='total_amount DESC',
            limit_page_length=10
        )

        # Top 10 clientes
        top_customers = frappe.get_all(
            'Sales Invoice',
            filters={
                'company': company,
                'docstatus': 1,
                'posting_date': ['>=', date_range['start']],
                'posting_date': ['<=', date_range['end']]
            },
            group_by='customer',
            fields=['customer', 'SUM(grand_total) as total_sales', 'COUNT(name) as order_count'],
            order_by='total_sales DESC',
            limit_page_length=10
        )

        # Tasa de conversión
        quotations = frappe.db.count(
            'Quotation',
            {
                'docstatus': 1,
                'posting_date': ['>=', date_range['start']],
                'posting_date': ['<=', date_range['end']]
            }
        )

        conversion_rate = (invoice_count / quotations * 100) if quotations > 0 else 0

        # Tendencia (últimos 6 meses)
        trend = _get_sales_trend(company, months=6)

        return {
            'success': True,
            'dashboard': {
                'total_sales': float(total_sales or 0),
                'invoice_count': invoice_count,
                'average_ticket': float(avg_ticket or 0),
                'conversion_rate': round(conversion_rate, 2),
                'quotations_count': quotations,
                'top_products': [
                    {
                        'item_code': p['item_code'],
                        'item_name': p['item_name'],
                        'qty': float(p['total_qty'] or 0),
                        'amount': float(p['total_amount'] or 0)
                    } for p in top_products
                ],
                'top_customers': [
                    {
                        'customer': c['customer'],
                        'sales': float(c['total_sales'] or 0),
                        'orders': c['order_count']
                    } for c in top_customers
                ],
                'trend': trend,
                'period': period
            }
        }

    except Exception as e:
        logger.error(f"Error generating sales dashboard: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'dashboard': {}
        }


def _get_sales_trend(company, months=6):
    """Obtiene tendencia de ventas últimos N meses"""
    trend = []

    for i in range(months, 0, -1):
        target_date = datetime.now() - timedelta(days=30 * i)
        month_start = target_date.replace(day=1)

        if target_date.month == 12:
            month_end = month_start.replace(year=month_start.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = month_start.replace(month=month_start.month + 1, day=1) - timedelta(days=1)

        sales = frappe.db.get_value(
            'Sales Invoice',
            {
                'company': company,
                'docstatus': 1,
                'posting_date': ['>=', month_start.date()],
                'posting_date': ['<=', month_end.date()]
            },
            'SUM(grand_total)'
        )

        trend.append({
            'period': target_date.strftime('%Y-%m'),
            'sales': float(sales[0] if sales else 0)
        })

    return trend


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

    elif period == 'This Year':
        return {'start': today.replace(month=1, day=1), 'end': today.replace(month=12, day=31)}

    else:
        return {'start': today.replace(day=1), 'end': today}
