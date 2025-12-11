# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

"""
Predefined metrics for common business indicators
Revenue, customer, and operational metrics
"""

import frappe
import json
from frappe.utils import now, add_days, get_first_day, get_last_day
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@frappe.whitelist(methods=['GET'])
def get_revenue_metrics(company=None, period='This Month'):
    """
    Métricas de ingresos

    Args:
        company (str): Empresa a considerar
        period (str): Período de análisis

    Returns:
        dict: Métricas de ingresos
    """
    try:
        if not company:
            company = frappe.defaults.get_user_default('company')

        # Obtener rango de fechas
        date_range = _get_period_dates(period)

        # Total revenue (Sum of grand_total in Sales Invoice)
        total_revenue = frappe.db.get_value(
            'Sales Invoice',
            {
                'company': company,
                'docstatus': 1,
                'posting_date': ['>=', date_range['start']],
                'posting_date': ['<=', date_range['end']]
            },
            'SUM(grand_total)'
        )
        total_revenue = total_revenue[0] if total_revenue else 0

        # Count of invoices
        invoice_count = frappe.db.count(
            'Sales Invoice',
            {
                'company': company,
                'docstatus': 1,
                'posting_date': ['>=', date_range['start']],
                'posting_date': ['<=', date_range['end']]
            }
        )

        # Average invoice value
        avg_invoice = total_revenue / invoice_count if invoice_count > 0 else 0

        # Revenue growth (vs previous period)
        prev_period = _get_previous_period_dates(period)
        prev_revenue = frappe.db.get_value(
            'Sales Invoice',
            {
                'company': company,
                'docstatus': 1,
                'posting_date': ['>=', prev_period['start']],
                'posting_date': ['<=', prev_period['end']]
            },
            'SUM(grand_total)'
        )
        prev_revenue = prev_revenue[0] if prev_revenue else 0

        growth_percentage = 0
        if prev_revenue and prev_revenue > 0:
            growth_percentage = ((total_revenue - prev_revenue) / prev_revenue) * 100

        return {
            'success': True,
            'metrics': {
                'total_revenue': float(total_revenue or 0),
                'invoice_count': invoice_count,
                'average_invoice': float(avg_invoice or 0),
                'growth_percentage': round(growth_percentage, 2),
                'period': period
            }
        }

    except Exception as e:
        logger.error(f"Error calculating revenue metrics: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'metrics': {}
        }


@frappe.whitelist(methods=['GET'])
def get_customer_metrics(company=None, period='This Month'):
    """
    Métricas de clientes

    Args:
        company (str): Empresa a considerar
        period (str): Período de análisis

    Returns:
        dict: Métricas de clientes
    """
    try:
        if not company:
            company = frappe.defaults.get_user_default('company')

        date_range = _get_period_dates(period)

        # Total customers
        total_customers = frappe.db.count(
            'Customer',
            {'company': company, 'disabled': 0}
        )

        # New customers (in period)
        new_customers = frappe.db.count(
            'Customer',
            {
                'company': company,
                'disabled': 0,
                'creation': ['>=', date_range['start']],
                'creation': ['<=', date_range['end']]
            }
        )

        # Customers with purchases (in period)
        active_customers = frappe.db.get_value(
            'Sales Invoice',
            {
                'company': company,
                'docstatus': 1,
                'posting_date': ['>=', date_range['start']],
                'posting_date': ['<=', date_range['end']]
            },
            'COUNT(DISTINCT customer)'
        )
        active_customers = active_customers[0] if active_customers else 0

        # Average customer value (in period)
        total_by_customer = frappe.db.get_value(
            'Sales Invoice',
            {
                'company': company,
                'docstatus': 1,
                'posting_date': ['>=', date_range['start']],
                'posting_date': ['<=', date_range['end']]
            },
            'SUM(grand_total)'
        )
        total_by_customer = total_by_customer[0] if total_by_customer else 0

        avg_customer_value = total_by_customer / active_customers if active_customers > 0 else 0

        return {
            'success': True,
            'metrics': {
                'total_customers': total_customers,
                'new_customers': new_customers,
                'active_customers': active_customers,
                'average_customer_value': float(avg_customer_value or 0),
                'period': period
            }
        }

    except Exception as e:
        logger.error(f"Error calculating customer metrics: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'metrics': {}
        }


@frappe.whitelist(methods=['GET'])
def get_operational_metrics(company=None, period='This Month'):
    """
    Métricas operacionales

    Args:
        company (str): Empresa a considerar
        period (str): Período de análisis

    Returns:
        dict: Métricas operacionales
    """
    try:
        if not company:
            company = frappe.defaults.get_user_default('company')

        date_range = _get_period_dates(period)

        # Total inventory value
        total_stock_value = frappe.db.get_value(
            'Stock Entry',
            {
                'company': company,
                'docstatus': 1,
                'posting_date': ['>=', date_range['start']],
                'posting_date': ['<=', date_range['end']]
            },
            'SUM(total_incoming_value)'
        )
        total_stock_value = total_stock_value[0] if total_stock_value else 0

        # Items count
        items_count = frappe.db.count(
            'Item',
            {'disabled': 0}
        )

        # Low stock items
        low_stock_items = frappe.db.count(
            'Bin',
            {
                'warehouse': frappe.get_all(
                    'Warehouse',
                    filters={'company': company},
                    pluck='name'
                )[0] if frappe.get_all('Warehouse', filters={'company': company}) else None,
                'actual_qty': ['<', frappe.db.get_value('Item', {'item_code': 'default'}, 'reorder_level') or 10]
            }
        ) if frappe.get_all('Warehouse', filters={'company': company}) else 0

        # Purchase orders pending
        pending_orders = frappe.db.count(
            'Purchase Order',
            {
                'company': company,
                'docstatus': 0
            }
        )

        # Sales orders pending
        pending_sales = frappe.db.count(
            'Sales Order',
            {
                'company': company,
                'docstatus': 1,
                'status': 'To Deliver'
            }
        )

        return {
            'success': True,
            'metrics': {
                'total_stock_value': float(total_stock_value or 0),
                'items_count': items_count,
                'low_stock_items': low_stock_items,
                'pending_orders': pending_orders,
                'pending_sales': pending_sales,
                'period': period
            }
        }

    except Exception as e:
        logger.error(f"Error calculating operational metrics: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'metrics': {}
        }


@frappe.whitelist(methods=['GET'])
def get_financial_health(company=None, period='This Month'):
    """
    Métricas de salud financiera

    Args:
        company (str): Empresa a considerar
        period (str): Período de análisis

    Returns:
        dict: Métricas financieras
    """
    try:
        if not company:
            company = frappe.defaults.get_user_default('company')

        date_range = _get_period_dates(period)

        # Accounts receivable
        accounts_receivable = frappe.db.get_value(
            'Sales Invoice',
            {
                'company': company,
                'docstatus': 1,
                'posting_date': ['>=', date_range['start']],
                'posting_date': ['<=', date_range['end']],
                'outstanding_amount': ['>', 0]
            },
            'SUM(outstanding_amount)'
        )
        accounts_receivable = accounts_receivable[0] if accounts_receivable else 0

        # Accounts payable
        accounts_payable = frappe.db.get_value(
            'Purchase Invoice',
            {
                'company': company,
                'docstatus': 1,
                'posting_date': ['>=', date_range['start']],
                'posting_date': ['<=', date_range['end']],
                'outstanding_amount': ['>', 0]
            },
            'SUM(outstanding_amount)'
        )
        accounts_payable = accounts_payable[0] if accounts_payable else 0

        # Overdue invoices
        overdue_invoices = frappe.db.count(
            'Sales Invoice',
            {
                'company': company,
                'docstatus': 1,
                'due_date': ['<', now().split(' ')[0]],
                'outstanding_amount': ['>', 0]
            }
        )

        # Overdue amount
        overdue_amount = frappe.db.get_value(
            'Sales Invoice',
            {
                'company': company,
                'docstatus': 1,
                'due_date': ['<', now().split(' ')[0]],
                'outstanding_amount': ['>', 0]
            },
            'SUM(outstanding_amount)'
        )
        overdue_amount = overdue_amount[0] if overdue_amount else 0

        return {
            'success': True,
            'metrics': {
                'accounts_receivable': float(accounts_receivable or 0),
                'accounts_payable': float(accounts_payable or 0),
                'overdue_invoices': overdue_invoices,
                'overdue_amount': float(overdue_amount or 0),
                'cash_flow_indicator': float((accounts_receivable or 0) - (accounts_payable or 0)),
                'period': period
            }
        }

    except Exception as e:
        logger.error(f"Error calculating financial health metrics: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'metrics': {}
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

    elif period == 'Last 30 Days':
        return {'start': today - timedelta(days=30), 'end': today}

    elif period == 'This Year':
        start = today.replace(month=1, day=1)
        end = today.replace(month=12, day=31)
        return {'start': start, 'end': end}

    elif period == 'Last Year':
        start = (today - timedelta(days=365)).replace(month=1, day=1)
        end = (today - timedelta(days=365)).replace(month=12, day=31)
        return {'start': start, 'end': end}

    else:
        return {'start': today.replace(day=1), 'end': today}


def _get_previous_period_dates(period):
    """Obtiene rango de fechas del período anterior"""
    dates = _get_period_dates(period)
    delta = dates['end'] - dates['start']

    prev_end = dates['start'] - timedelta(days=1)
    prev_start = prev_end - delta

    return {'start': prev_start, 'end': prev_end}


@frappe.whitelist(methods=['GET'])
def get_all_metrics(company=None, period='This Month'):
    """
    Obtiene todas las métricas en una sola llamada

    Returns:
        dict: Todas las métricas consolidadas
    """
    try:
        revenue = get_revenue_metrics(company, period)
        customers = get_customer_metrics(company, period)
        operations = get_operational_metrics(company, period)
        financial = get_financial_health(company, period)

        return {
            'success': True,
            'revenue': revenue.get('metrics', {}),
            'customers': customers.get('metrics', {}),
            'operations': operations.get('metrics', {}),
            'financial': financial.get('metrics', {}),
            'period': period,
            'generated_at': now()
        }

    except Exception as e:
        logger.error(f"Error getting all metrics: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }
