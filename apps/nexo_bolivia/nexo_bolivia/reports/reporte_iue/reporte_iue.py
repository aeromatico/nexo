# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

"""
Reporte IUE Anual - Impuesto sobre Utilidades de Empresas

Reporte del Impuesto sobre Utilidades de Empresas (25%) para el año fiscal.
Incluye utilidad neta, ajustes fiscales, compensación de IT, etc.
"""

import frappe
from frappe import _
from datetime import datetime
from typing import Dict, List, Any


IUE_RATE = 25.0


def execute(filters=None):
    """
    Genera reporte IUE anual

    Args:
        filters: {'company': str, 'fiscal_year': str}

    Returns:
        tuple: (columns, data)
    """
    if not filters:
        filters = {}

    if not filters.get('company'):
        frappe.throw(_('Empresa es requerida'))

    columns = get_columns()
    data = get_iue_data(filters)

    return columns, data


def get_columns() -> List[Dict[str, Any]]:
    """Retorna las columnas del reporte"""
    return [
        {'fieldname': 'description', 'label': _('Descripción'), 'fieldtype': 'Data', 'width': 300},
        {'fieldname': 'amount', 'label': _('Monto'), 'fieldtype': 'Currency', 'width': 150}
    ]


def get_iue_data(filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Obtiene datos de IUE"""
    result = calculate_iue_annual(
        filters.get('company'),
        filters.get('fiscal_year')
    )

    data = [
        {'description': 'Utilidad Neta Contable', 'amount': result['utilidad_neta']},
        {'description': 'Ajustes Fiscales (+)', 'amount': result['adiciones']},
        {'description': 'Deducciones Fiscales (-)', 'amount': result['deducciones']},
        {'description': 'Base Imponible IUE', 'amount': result['base_imponible']},
        {'description': f'IUE Calculado ({IUE_RATE}%)', 'amount': result['iue_calculado']},
        {'description': 'IT Pagado en el Año (Compensable 100%)', 'amount': result['it_pagado']},
        {'description': 'IUE Neto a Pagar', 'amount': result['iue_neto']}
    ]

    return data


def calculate_iue_annual(company: str, fiscal_year: str = None) -> Dict[str, float]:
    """
    Calcula IUE del año fiscal

    Args:
        company: Empresa
        fiscal_year: Año fiscal

    Returns:
        Dict: Datos de IUE
    """
    if not fiscal_year:
        fiscal_year = str(datetime.now().year)

    # Obtener ganancias/pérdidas netas del año
    # Usar report del P&L o sumas de income/expense
    utilidad_neta = frappe.db.sql("""
        SELECT COALESCE(SUM(CASE
            WHEN account_type IN ('Income', 'Revenue') THEN credit - debit
            WHEN account_type IN ('Expense') THEN debit - credit
            ELSE 0
        END), 0)
        FROM `tabGL Entry`
        WHERE company = %s
        AND YEAR(posting_date) = %s
    """, (company, fiscal_year))[0][0] or 0

    # Ajustes fiscales (adiciones)
    adiciones = 0  # Se agregarían manualmente según normativa

    # Deducciones fiscales
    deducciones = 0

    # Calcular base imponible
    base_imponible = utilidad_neta + adiciones - deducciones

    # Calcular IUE
    iue_calculado = round(base_imponible * (IUE_RATE / 100), 2) if base_imponible > 0 else 0

    # IT pagado en el año (compensable 100%)
    it_pagado = frappe.db.sql("""
        SELECT COALESCE(SUM(paid_amount), 0)
        FROM `tabPayment Entry`
        WHERE company = %s
        AND YEAR(posting_date) = %s
        AND payment_type = 'Receive'
    """, (company, fiscal_year))[0][0] or 0

    # IUE neto
    iue_neto = max(iue_calculado - it_pagado, 0)

    return {
        'utilidad_neta': round(utilidad_neta, 2),
        'adiciones': round(adiciones, 2),
        'deducciones': round(deducciones, 2),
        'base_imponible': round(base_imponible, 2),
        'iue_calculado': iue_calculado,
        'it_pagado': round(it_pagado, 2),
        'iue_neto': round(iue_neto, 2)
    }


@frappe.whitelist()
def get_iue_report(company: str, fiscal_year: str = None) -> Dict[str, Any]:
    """
    API para obtener reporte IUE

    Args:
        company: Empresa
        fiscal_year: Año fiscal

    Returns:
        Dict: Reporte IUE
    """
    return calculate_iue_annual(company, fiscal_year)


@frappe.whitelist()
def generate_declaracion_iue(company: str, fiscal_year: str = None) -> Dict[str, Any]:
    """
    Genera declaración jurada IUE (Form 500)

    Args:
        company: Empresa
        fiscal_year: Año fiscal

    Returns:
        Dict: Form 500
    """
    result = calculate_iue_annual(company, fiscal_year)

    return {
        'form_type': 'Form 500',
        'company': company,
        'fiscal_year': fiscal_year or str(datetime.now().year),
        'declaration_date': datetime.now().date(),
        'data': result,
        'iue_neto': result['iue_neto']
    }


@frappe.whitelist()
def get_iue_summary(company: str, fiscal_year: str = None) -> Dict[str, Any]:
    """Obtiene resumen ejecutivo de IUE"""
    result = get_iue_report(company, fiscal_year)
    return {
        'fiscal_year': fiscal_year or str(datetime.now().year),
        'utilidad_neta': result['utilidad_neta'],
        'iue_calculado': result['iue_calculado'],
        'it_pagado': result['it_pagado'],
        'iue_neto': result['iue_neto'],
        'tasa': IUE_RATE
    }
