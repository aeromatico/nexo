# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

"""
Declaración Jurada IVA (Form 200)

Formulario oficial de declaración mensual de IVA ante el SIN.

Secciones:
I. VENTAS - Débito fiscal total
II. COMPRAS - Crédito fiscal total
III. DETERMINACIÓN - Cálculo de saldo a pagar o a favor
"""

import frappe
from frappe import _
from datetime import datetime
from typing import Dict, Any


def execute(filters=None):
    """
    Genera Form 200 - Declaración Jurada IVA

    Args:
        filters: {'company': str, 'month': int, 'year': int}

    Returns:
        tuple: (columns, data)
    """
    if not filters:
        filters = {}

    if not filters.get('company'):
        frappe.throw(_('Empresa es requerida'))

    month = filters.get('month') or datetime.now().month
    year = filters.get('year') or datetime.now().year

    data = generate_form_200(filters.get('company'), month, year)

    columns = get_columns()
    return columns, [[data]]


def get_columns():
    """Retorna estructura de columnas"""
    return [
        {
            'fieldname': 'form_200',
            'label': _('Form 200'),
            'fieldtype': 'Data'
        }
    ]


def generate_form_200(company: str, month: int, year: int) -> Dict[str, Any]:
    """
    Genera Form 200 completo

    Args:
        company: Empresa
        month: Mes (1-12)
        year: Año

    Returns:
        Dict: Datos del formulario
    """
    from datetime import date
    import calendar

    # Obtener rango de fechas del mes
    first_day = date(year, month, 1)
    last_day = date(year, month, calendar.monthrange(year, month)[1])

    # I. VENTAS - Débito Fiscal
    sales_data = get_sales_summary(company, first_day, last_day)

    # II. COMPRAS - Crédito Fiscal
    purchases_data = get_purchases_summary(company, first_day, last_day)

    # III. DETERMINACIÓN
    balance = sales_data['total_iva'] - purchases_data['total_iva']

    # Saldo anterior (obtener del período anterior)
    previous_balance = get_previous_balance(company, month, year)

    # Total a pagar o saldo siguiente
    if balance > 0:
        total_to_pay = balance + previous_balance
        balance_next_period = 0
    else:
        total_to_pay = 0
        balance_next_period = abs(balance) + previous_balance

    return {
        'company': company,
        'period': f'{month:02d}/{year}',
        'month': month,
        'year': year,
        'form_type': 'Form 200',
        'i_sales': {
            'total_sales': sales_data['total_sales'],
            'cancelled_invoices': sales_data['cancelled'],
            'total_debit_fiscal': sales_data['total_iva'],
            'adjustments': 0
        },
        'ii_purchases': {
            'total_purchases': purchases_data['total_purchases'],
            'with_credit': purchases_data['with_credit'],
            'without_credit': purchases_data['without_credit'],
            'total_credit_fiscal': purchases_data['total_iva']
        },
        'iii_determination': {
            'debit_fiscal': sales_data['total_iva'],
            'minus_credit_fiscal': purchases_data['total_iva'],
            'balance': balance,
            'previous_balance': previous_balance,
            'total_to_pay': total_to_pay,
            'balance_next_period': balance_next_period
        }
    }


def get_sales_summary(company: str, from_date, to_date) -> Dict[str, float]:
    """Resumen de ventas y débito fiscal"""
    result = frappe.db.sql("""
        SELECT
            COUNT(DISTINCT si.name) as count,
            COALESCE(SUM(si.grand_total), 0) as total_sales,
            COALESCE(SUM(CASE WHEN si.is_cancelled = 1 THEN si.grand_total ELSE 0 END), 0) as cancelled,
            COALESCE(SUM(CASE WHEN stc.description LIKE '%IVA%' THEN stc.tax_amount ELSE 0 END), 0) as total_iva
        FROM `tabSales Invoice` si
        LEFT JOIN `tabSales Taxes and Charges` stc ON stc.parent = si.name
        WHERE si.company = %s
        AND si.docstatus = 1
        AND si.posting_date BETWEEN %s AND %s
    """, (company, from_date, to_date))[0]

    return {
        'count': result[0] or 0,
        'total_sales': round(result[1] or 0, 2),
        'cancelled': round(result[2] or 0, 2),
        'total_iva': round(result[3] or 0, 2)
    }


def get_purchases_summary(company: str, from_date, to_date) -> Dict[str, float]:
    """Resumen de compras y crédito fiscal"""
    result = frappe.db.sql("""
        SELECT
            COUNT(DISTINCT pi.name) as count,
            COALESCE(SUM(pi.grand_total), 0) as total_purchases,
            COALESCE(SUM(CASE WHEN pi.is_cancelled = 1 THEN pi.grand_total ELSE 0 END), 0) as cancelled,
            COALESCE(SUM(CASE WHEN ptc.description LIKE '%IVA%' THEN ptc.tax_amount ELSE 0 END), 0) as total_iva
        FROM `tabPurchase Invoice` pi
        LEFT JOIN `tabPurchase Taxes and Charges` ptc ON ptc.parent = pi.name
        WHERE pi.company = %s
        AND pi.docstatus = 1
        AND pi.posting_date BETWEEN %s AND %s
    """, (company, from_date, to_date))[0]

    return {
        'count': result[0] or 0,
        'total_purchases': round(result[1] or 0, 2),
        'with_credit': round(result[1] or 0, 2),
        'without_credit': 0,
        'cancelled': round(result[2] or 0, 2),
        'total_iva': round(result[3] or 0, 2)
    }


def get_previous_balance(company: str, current_month: int, current_year: int) -> float:
    """Obtiene el saldo del período anterior"""
    prev_month = current_month - 1 if current_month > 1 else 12
    prev_year = current_year if current_month > 1 else current_year - 1

    # Buscar Form 200 del mes anterior
    form_200 = frappe.db.get_value(
        'Form 200 IVA',
        {
            'company': company,
            'month': prev_month,
            'year': prev_year,
            'docstatus': 1
        },
        'balance_next_period'
    )

    return form_200 or 0


@frappe.whitelist()
def calculate_iva_declaration(company: str, month: int, year: int) -> Dict[str, Any]:
    """
    API para calcular declaración IVA

    Args:
        company: Empresa
        month: Mes
        year: Año

    Returns:
        Dict: Form 200 completado
    """
    return generate_form_200(company, month, year)


@frappe.whitelist()
def export_form_200_pdf(company: str, month: int, year: int) -> str:
    """Exporta Form 200 a PDF"""
    form_200 = generate_form_200(company, month, year)

    # Crear HTML para PDF
    html = f"""
    <h1>DECLARACIÓN JURADA IVA - FORM 200</h1>
    <p>Empresa: {form_200['company']}</p>
    <p>Período: {form_200['period']}</p>

    <h2>I. VENTAS</h2>
    <p>Total Débito Fiscal: {form_200['i_sales']['total_debit_fiscal']}</p>

    <h2>II. COMPRAS</h2>
    <p>Total Crédito Fiscal: {form_200['ii_purchases']['total_credit_fiscal']}</p>

    <h2>III. DETERMINACIÓN</h2>
    <p>Balance a Pagar: {form_200['iii_determination']['total_to_pay']}</p>
    """

    return frappe.render_template(html, form_200)


@frappe.whitelist()
def get_form_200_summary(company: str, month: int, year: int) -> Dict[str, Any]:
    """Obtiene resumen ejecutivo de Form 200"""
    form_200 = generate_form_200(company, month, year)
    return {
        'period': form_200['period'],
        'debit_fiscal': form_200['iii_determination']['debit_fiscal'],
        'credit_fiscal': form_200['iii_determination']['credit_fiscal'],
        'balance': form_200['iii_determination']['balance'],
        'total_to_pay': form_200['iii_determination']['total_to_pay']
    }
