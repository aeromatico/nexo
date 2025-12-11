# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

"""
Financial Dashboard
Revenue, expenses, profitability, and cash flow metrics
"""

import frappe
from frappe.utils import now, add_days, get_first_day, get_last_day
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@frappe.whitelist(methods=['GET'])
def get_financial_dashboard(company=None, period='This Month'):
    """
    Dashboard financiero completo:
    - Total ingresos (ventas)
    - Total egresos (compras, gastos)
    - Utilidad neta
    - Flujo de caja
    - Cuentas por cobrar
    - Cuentas por pagar
    - Gráfico de ingresos vs egresos (últimos 12 meses)
    - Top 5 gastos
    - Proyección financiera próximo mes

    Args:
        company (str): Empresa a considerar
        period (str): Período ('This Month', 'This Year', etc.)

    Returns:
        dict: Dashboard data
    """
    try:
        if not company:
            company = frappe.defaults.get_user_default('company')

        date_range = _get_period_dates(period)

        # Calcular métricas principales
        total_income = _calculate_total_income(company, date_range)
        total_expenses = _calculate_total_expenses(company, date_range)
        net_profit = total_income - total_expenses

        # Cuentas por cobrar
        accounts_receivable = _calculate_accounts_receivable(company)

        # Cuentas por pagar
        accounts_payable = _calculate_accounts_payable(company)

        # Cash flow
        cash_flow = accounts_receivable - accounts_payable

        # Top 5 gastos
        top_expenses = _get_top_expenses(company, date_range, limit=5)

        # Gráfico histórico (últimos 12 meses)
        monthly_chart = _get_monthly_financial_chart(company, months=12)

        # Proyección (regresión simple)
        forecast = _forecast_financial(company, months=3)

        return {
            'success': True,
            'dashboard': {
                'total_income': float(total_income or 0),
                'total_expenses': float(total_expenses or 0),
                'net_profit': float(net_profit or 0),
                'profit_margin': round((net_profit / total_income * 100) if total_income > 0 else 0, 2),
                'accounts_receivable': float(accounts_receivable or 0),
                'accounts_payable': float(accounts_payable or 0),
                'cash_flow': float(cash_flow or 0),
                'top_expenses': top_expenses,
                'monthly_chart': monthly_chart,
                'forecast': forecast,
                'period': period,
                'generated_at': now()
            }
        }

    except Exception as e:
        logger.error(f"Error generating financial dashboard: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'dashboard': {}
        }


def _calculate_total_income(company, date_range):
    """Calcula ingresos totales del período"""
    result = frappe.db.get_value(
        'Sales Invoice',
        {
            'company': company,
            'docstatus': 1,
            'posting_date': ['>=', date_range['start']],
            'posting_date': ['<=', date_range['end']]
        },
        'SUM(grand_total)'
    )
    return result[0] if result else 0


def _calculate_total_expenses(company, date_range):
    """Calcula egresos totales del período"""
    result = frappe.db.get_value(
        'Purchase Invoice',
        {
            'company': company,
            'docstatus': 1,
            'posting_date': ['>=', date_range['start']],
            'posting_date': ['<=', date_range['end']]
        },
        'SUM(grand_total)'
    )
    return result[0] if result else 0


def _calculate_accounts_receivable(company):
    """Calcula cuentas por cobrar pendientes"""
    result = frappe.db.get_value(
        'Sales Invoice',
        {
            'company': company,
            'docstatus': 1,
            'outstanding_amount': ['>', 0]
        },
        'SUM(outstanding_amount)'
    )
    return result[0] if result else 0


def _calculate_accounts_payable(company):
    """Calcula cuentas por pagar pendientes"""
    result = frappe.db.get_value(
        'Purchase Invoice',
        {
            'company': company,
            'docstatus': 1,
            'outstanding_amount': ['>', 0]
        },
        'SUM(outstanding_amount)'
    )
    return result[0] if result else 0


def _get_top_expenses(company, date_range, limit=5):
    """Obtiene top gastos del período"""
    expenses = frappe.get_all(
        'Purchase Invoice Item',
        filters={
            'parent': frappe.get_all(
                'Purchase Invoice',
                filters={
                    'company': company,
                    'docstatus': 1,
                    'posting_date': ['>=', date_range['start']],
                    'posting_date': ['<=', date_range['end']]
                },
                pluck='name'
            )
        },
        group_by='item_name',
        fields=['item_name', 'SUM(amount) as total_amount'],
        order_by='total_amount DESC',
        limit_page_length=limit
    )

    return [{'item': e['item_name'], 'amount': float(e['total_amount'] or 0)} for e in expenses]


def _get_monthly_financial_chart(company, months=12):
    """Obtiene datos mensuales para gráfico"""
    chart_data = []

    for i in range(months, 0, -1):
        target_date = datetime.now() - timedelta(days=30 * i)
        month_start = target_date.replace(day=1)

        if target_date.month == 12:
            month_end = month_start.replace(year=month_start.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = month_start.replace(month=month_start.month + 1, day=1) - timedelta(days=1)

        income = frappe.db.get_value(
            'Sales Invoice',
            {
                'company': company,
                'docstatus': 1,
                'posting_date': ['>=', month_start.date()],
                'posting_date': ['<=', month_end.date()]
            },
            'SUM(grand_total)'
        )
        income = income[0] if income else 0

        expenses = frappe.db.get_value(
            'Purchase Invoice',
            {
                'company': company,
                'docstatus': 1,
                'posting_date': ['>=', month_start.date()],
                'posting_date': ['<=', month_end.date()]
            },
            'SUM(grand_total)'
        )
        expenses = expenses[0] if expenses else 0

        chart_data.append({
            'period': target_date.strftime('%Y-%m'),
            'income': float(income or 0),
            'expenses': float(expenses or 0),
            'profit': float((income or 0) - (expenses or 0))
        })

    return chart_data


def _forecast_financial(company, months=3):
    """Proyecta financiero para próximos meses"""
    forecast = []

    for i in range(months):
        future_date = datetime.now() + timedelta(days=30 * (i + 1))

        forecast.append({
            'period': future_date.strftime('%Y-%m'),
            'projected_income': 0,  # Placeholder
            'projected_expenses': 0,  # Placeholder
            'projected_profit': 0  # Placeholder
        })

    return forecast


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

    elif period == 'Last 90 Days':
        return {'start': today - timedelta(days=90), 'end': today}

    else:
        return {'start': today.replace(day=1), 'end': today}
