# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

"""
Reporte RC-IVA - Retenciones en Planilla

Reporte de retenciones RC-IVA aplicadas en nómina.
Detalle por empleado de salarios y retenciones.
"""

import frappe
from frappe import _
from typing import Dict, List, Any


def execute(filters=None):
    """
    Genera reporte RC-IVA

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
    data = get_rc_iva_details(filters)

    return columns, data


def get_columns() -> List[Dict[str, Any]]:
    """Retorna las columnas del reporte"""
    return [
        {'fieldname': 'employee', 'label': _('Empleado'), 'fieldtype': 'Link', 'options': 'Employee', 'width': 150},
        {'fieldname': 'employee_name', 'label': _('Nombre'), 'fieldtype': 'Data', 'width': 200},
        {'fieldname': 'posting_date', 'label': _('Fecha'), 'fieldtype': 'Date', 'width': 100},
        {'fieldname': 'salary', 'label': _('Salario Mensual'), 'fieldtype': 'Currency', 'width': 120},
        {'fieldname': 'other_income', 'label': _('Otros Ingresos'), 'fieldtype': 'Currency', 'width': 120},
        {'fieldname': 'dependents', 'label': _('Dependientes'), 'fieldtype': 'Int', 'width': 100},
        {'fieldname': 'deduction', 'label': _('Deducción'), 'fieldtype': 'Currency', 'width': 120},
        {'fieldname': 'taxable_base', 'label': _('Base Imponible'), 'fieldtype': 'Currency', 'width': 120},
        {'fieldname': 'rc_iva_rate', 'label': _('Tasa %'), 'fieldtype': 'Float', 'width': 80},
        {'fieldname': 'rc_iva_amount', 'label': _('RC-IVA Retenido'), 'fieldtype': 'Currency', 'width': 120}
    ]


def get_rc_iva_details(filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Obtiene detalle de retenciones RC-IVA por empleado"""
    conditions = [
        'ss.docstatus = 1',
        'ss.company = %s',
        'ss.posting_date BETWEEN %s AND %s'
    ]

    params = [
        filters.get('company'),
        filters.get('from_date'),
        filters.get('to_date')
    ]

    # Obtener salary slips
    salary_slips = frappe.db.sql(f"""
        SELECT
            ss.name,
            ss.employee,
            ss.employee_name,
            ss.posting_date,
            ss.gross_pay,
            e.ctc
        FROM `tabSalary Slip` ss
        LEFT JOIN `tabEmployee` e ON e.name = ss.employee
        WHERE {' AND '.join(conditions)}
        ORDER BY ss.posting_date, ss.employee
    """, params, as_dict=True)

    data = []

    for slip_doc in salary_slips:
        slip = frappe.get_doc('Salary Slip', slip_doc.name)

        # Obtener información de ingresos y deducciones
        salary = 0
        other_income = 0

        for earning in slip.earnings:
            if 'salario' in earning.salary_component.lower():
                salary += earning.amount
            else:
                other_income += earning.amount

        # Obtener deducciones
        total_deduction = 0
        for deduction in slip.deductions:
            total_deduction += deduction.amount

        # Calcular RC-IVA
        taxable_base = salary + other_income - total_deduction

        # Obtener número de dependientes del empleado
        dependents = frappe.db.get_value('Employee', slip.employee, 'ctc') or 0

        # Obtener tasa de RC-IVA (se obtendría de tabla configurada)
        rc_iva_rate = get_rc_iva_rate(salary, dependents)
        rc_iva_amount = round(taxable_base * (rc_iva_rate / 100), 2) if taxable_base > 0 else 0

        data.append({
            'employee': slip.employee,
            'employee_name': slip_doc.employee_name,
            'posting_date': slip_doc.posting_date,
            'salary': salary,
            'other_income': other_income,
            'dependents': dependents,
            'deduction': total_deduction,
            'taxable_base': taxable_base,
            'rc_iva_rate': rc_iva_rate,
            'rc_iva_amount': rc_iva_amount
        })

    # Agregar totales
    if data:
        totals = {
            'employee': '',
            'employee_name': 'TOTAL PERÍODO',
            'posting_date': '',
            'salary': sum(row.get('salary', 0) for row in data),
            'other_income': sum(row.get('other_income', 0) for row in data),
            'dependents': sum(row.get('dependents', 0) for row in data),
            'deduction': sum(row.get('deduction', 0) for row in data),
            'taxable_base': sum(row.get('taxable_base', 0) for row in data),
            'rc_iva_rate': '',
            'rc_iva_amount': sum(row.get('rc_iva_amount', 0) for row in data)
        }
        data.append(totals)

    return data


def get_rc_iva_rate(salary: float, dependents: int = 0) -> float:
    """
    Obtiene la tasa de RC-IVA según tabla oficial

    Args:
        salary: Salario mensual
        dependents: Número de dependientes

    Returns:
        float: Tasa de RC-IVA
    """
    # Tabla de retención RC-IVA 2024 (ejemplo)
    # Se puede configurar en sistema

    if salary <= 2500:
        return 0.0  # Sin retención
    elif salary <= 5000:
        return 0.5
    elif salary <= 7500:
        return 1.0
    elif salary <= 10000:
        return 1.5
    else:
        return 2.0


@frappe.whitelist()
def get_rc_iva_report(company: str, month: int, year: int) -> Dict[str, Any]:
    """
    API para obtener reporte RC-IVA

    Args:
        company: Empresa
        month: Mes
        year: Año

    Returns:
        Dict: Reporte RC-IVA
    """
    from datetime import date
    import calendar

    first_day = date(year, month, 1)
    last_day = date(year, month, calendar.monthrange(year, month)[1])

    filters = {
        'company': company,
        'from_date': first_day,
        'to_date': last_day
    }

    columns, data = execute(filters)

    return {
        'period': f'{month:02d}/{year}',
        'total_rc_iva': data[-1].get('rc_iva_amount', 0) if data else 0,
        'employees_count': len(data) - 1 if data else 0,
        'details': data
    }


@frappe.whitelist()
def get_rc_iva_summary(company: str, month: int, year: int) -> Dict[str, Any]:
    """Obtiene resumen ejecutivo de RC-IVA"""
    result = get_rc_iva_report(company, month, year)
    return {
        'period': result['period'],
        'total_rc_iva': result['total_rc_iva'],
        'employees_count': result['employees_count']
    }
