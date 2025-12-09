# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

"""
Reporte IT Mensual - Impuesto a las Transacciones

Reporte del Impuesto a las Transacciones (3%) para el período.
Incluye ingresos, base imponible y cálculo de IT.
"""

import frappe
from frappe import _
from datetime import datetime
from typing import Dict, List, Any


IT_RATE = 3.0


def execute(filters=None):
    """
    Genera reporte IT mensual

    Args:
        filters: {'company': str, 'from_date': str, 'to_date': str}

    Returns:
        tuple: (columns, data)
    """
    if not filters:
        filters = {}

    if not filters.get('company'):
        frappe.throw(_('Empresa es requerida'))

    columns = get_columns()
    data = get_it_data(filters)

    return columns, data


def get_columns() -> List[Dict[str, Any]]:
    """Retorna las columnas del reporte"""
    return [
        {'fieldname': 'description', 'label': _('Descripción'), 'fieldtype': 'Data', 'width': 250},
        {'fieldname': 'amount', 'label': _('Monto'), 'fieldtype': 'Currency', 'width': 150}
    ]


def get_it_data(filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Obtiene datos de IT"""
    result = calculate_it_for_period(
        filters.get('company'),
        filters.get('from_date'),
        filters.get('to_date')
    )

    data = [
        {'description': 'Ingresos Totales', 'amount': result['ingresos_totales']},
        {'description': 'Base Imponible IT (3%)', 'amount': result['base_imponible']},
        {'description': 'IT Generado (3%)', 'amount': result['it_generado']},
        {'description': 'Pagos a Cuenta', 'amount': result['pagos_cuenta']},
        {'description': 'Saldo a Pagar', 'amount': result['saldo_pagar']}
    ]

    return data


def calculate_it_for_period(company: str, from_date=None, to_date=None) -> Dict[str, float]:
    """
    Calcula IT del período

    Args:
        company: Empresa
        from_date: Fecha inicio
        to_date: Fecha fin

    Returns:
        Dict: Datos de IT
    """
    # Obtener ingresos por facturas de venta
    ingresos = frappe.db.sql("""
        SELECT COALESCE(SUM(grand_total), 0)
        FROM `tabSales Invoice`
        WHERE company = %s
        AND docstatus = 1
    """, (company,))[0][0] or 0

    # Obtener pagos a cuenta registrados
    pagos_cuenta = frappe.db.sql("""
        SELECT COALESCE(SUM(paid_amount), 0)
        FROM `tabPayment Entry`
        WHERE company = %s
        AND docstatus = 1
        AND payment_type = 'Receive'
    """, (company,))[0][0] or 0

    # Calcular IT
    base_imponible = ingresos
    it_generado = round(base_imponible * (IT_RATE / 100), 2)

    # Calcular saldo
    saldo_pagar = it_generado - pagos_cuenta

    return {
        'ingresos_totales': round(ingresos, 2),
        'base_imponible': round(base_imponible, 2),
        'it_generado': it_generado,
        'pagos_cuenta': round(pagos_cuenta, 2),
        'saldo_pagar': round(saldo_pagar, 2)
    }


@frappe.whitelist()
def get_it_report(company: str, month: int, year: int) -> Dict[str, Any]:
    """
    API para obtener reporte IT

    Args:
        company: Empresa
        month: Mes
        year: Año

    Returns:
        Dict: Reporte IT
    """
    from datetime import date
    import calendar

    first_day = date(year, month, 1)
    last_day = date(year, month, calendar.monthrange(year, month)[1])

    return calculate_it_for_period(company, first_day, last_day)


@frappe.whitelist()
def get_it_summary(company: str, month: int, year: int) -> Dict[str, Any]:
    """Obtiene resumen ejecutivo de IT"""
    result = get_it_report(company, month, year)
    return {
        'period': f'{month:02d}/{year}',
        'it_generado': result['it_generado'],
        'pagos_cuenta': result['pagos_cuenta'],
        'saldo_pagar': result['saldo_pagar'],
        'tasa': IT_RATE
    }
