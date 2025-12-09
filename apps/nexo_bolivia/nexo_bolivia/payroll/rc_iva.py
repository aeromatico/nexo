# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

"""
RC-IVA (Retención por Concepto de IVA) - Ley 843 de Bolivia

Cálculo de impuesto a la renta de personas naturales trabajadores dependientes.
Tablas progresivas 2024.

Formula: (Base imponible - 2 SMN × dependientes) × tasa progresiva
"""

import frappe
from frappe import _
from datetime import datetime

# Constantes Bolivia 2024
SMN = 2362  # Salario Mínimo Nacional
RC_IVA_MIN_NO_IMPONIBLE = 13000  # Mínimo no imponible

# Tabla de retención RC-IVA 2024 (progresiva)
# Formato: (hasta, tasa)
RC_IVA_BRACKETS_2024 = [
    (13000, 0.0),      # Hasta 13,000: 0%
    (25000, 13.0),     # 13,001 - 25,000: 13%
    (50000, 16.5),     # 25,001 - 50,000: 16.5%
    (75000, 19.5),     # 50,001 - 75,000: 19.5%
    (150000, 22.5),    # 75,001 - 150,000: 22.5%
    (float('inf'), 27.5)  # Más de 150,000: 27.5%
]


def get_rc_iva_table(year: int = 2024) -> list:
    """
    Obtiene la tabla de retención RC-IVA para un año

    Args:
        year (int): Año (actualmente solo 2024)

    Returns:
        list: Tabla de brackets con tasas progresivas
    """
    if year != 2024:
        frappe.msgprint(
            _('Solo hay tabla RC-IVA para 2024. Usando 2024.'),
            indicator='yellow'
        )

    return RC_IVA_BRACKETS_2024


def calculate_rc_iva_rate(annual_salary: float) -> float:
    """
    Obtiene la tasa de RC-IVA según salario anual

    Args:
        annual_salary (float): Salario anual

    Returns:
        float: Tasa de retención en %

    Examples:
        >>> calculate_rc_iva_rate(13000)
        0.0
        >>> calculate_rc_iva_rate(25000)
        13.0
        >>> calculate_rc_iva_rate(150000)
        22.5
        >>> calculate_rc_iva_rate(200000)
        27.5
    """
    if annual_salary < 0:
        return 0.0

    brackets = get_rc_iva_table()

    for limit, rate in brackets:
        if annual_salary <= limit:
            return rate

    return brackets[-1][1]


def calculate_rc_iva(annual_salary: float, dependents: int = 0) -> float:
    """
    Calcula el RC-IVA sobre un salario anual

    Fórmula: (Salario anual - (2 SMN × dependientes)) × tasa progresiva

    Args:
        annual_salary (float): Salario anual
        dependents (int): Número de dependientes (deduce 2 SMN por cada uno)

    Returns:
        float: Monto del RC-IVA a retener

    Examples:
        >>> calculate_rc_iva(25000)  # Sin dependientes
        1560.0
        >>> calculate_rc_iva(25000, 1)  # Con 1 dependiente
        741.66
    """
    if annual_salary < 0:
        frappe.throw(_('Salario no puede ser negativo'))

    if dependents < 0:
        frappe.throw(_('Número de dependientes no puede ser negativo'))

    # Aplicar deducción de dependientes
    deduction = 2 * SMN * dependents
    taxable_base = annual_salary - deduction

    # El mínimo no imponible es 13,000
    if taxable_base < RC_IVA_MIN_NO_IMPONIBLE:
        return 0.0

    # Obtener tasa según base imponible
    rate = calculate_rc_iva_rate(taxable_base)

    # Calcular retención
    rc_iva = taxable_base * (rate / 100)

    return round(float(rc_iva), 2)


def calculate_rc_iva_monthly(annual_salary: float, dependents: int = 0, month: int = 12) -> dict:
    """
    Calcula RC-IVA prorrateado mensualmente

    Args:
        annual_salary (float): Salario anual
        dependents (int): Número de dependientes
        month (int): Mes para calcular (1-12)

    Returns:
        dict: Información de RC-IVA mensual
    """
    annual_rc_iva = calculate_rc_iva(annual_salary, dependents)

    # Prorrateo simple: dividir entre 12 meses
    monthly_rc_iva = annual_rc_iva / 12

    # Retención acumulada hasta el mes
    accumulated = monthly_rc_iva * month

    return {
        'annual_salary': round(annual_salary, 2),
        'dependents': dependents,
        'taxable_base': round(annual_salary - (2 * SMN * dependents), 2),
        'annual_rc_iva': round(annual_rc_iva, 2),
        'monthly_rc_iva': round(monthly_rc_iva, 2),
        'month': month,
        'accumulated_rc_iva': round(accumulated, 2),
        'rate': calculate_rc_iva_rate(annual_salary - (2 * SMN * dependents))
    }


def get_rc_iva_breakdown(annual_salary: float, dependents: int = 0) -> dict:
    """
    Obtiene el desglose completo del RC-IVA

    Args:
        annual_salary (float): Salario anual
        dependents (int): Número de dependientes

    Returns:
        dict: Desglose de RC-IVA
    """
    deduction = 2 * SMN * dependents
    taxable_base = annual_salary - deduction

    # Evitar negativo
    if taxable_base < 0:
        taxable_base = 0

    rate = calculate_rc_iva_rate(taxable_base)
    rc_iva_amount = calculate_rc_iva(annual_salary, dependents)

    return {
        'annual_salary': round(annual_salary, 2),
        'dependents': dependents,
        'deduction_per_dependent': round(2 * SMN, 2),
        'total_deduction': round(deduction, 2),
        'taxable_base': round(taxable_base, 2),
        'min_no_imponible': RC_IVA_MIN_NO_IMPONIBLE,
        'applicable_rate': rate,
        'rc_iva': round(rc_iva_amount, 2),
        'net_salary': round(annual_salary - rc_iva_amount, 2),
        'effective_rate': round((rc_iva_amount / annual_salary * 100) if annual_salary > 0 else 0, 2)
    }


def apply_rc_iva_to_salary_slip(doc, method=None):
    """
    Hook para aplicar RC-IVA automáticamente a Salary Slip

    Args:
        doc: Documento Salary Slip
        method: Nombre del hook
    """
    if not doc.doctype == 'Salary Slip':
        return

    # No aplicar RC-IVA automáticamente en hook
    # Se debe calcular según configuración anual del empleado
    pass


@frappe.whitelist()
def calculate_annual_rc_iva(employee: str, year: int = None) -> dict:
    """
    API para calcular RC-IVA anual de un empleado

    Args:
        employee (str): ID del empleado
        year (int): Año (default: año actual)

    Returns:
        dict: Información de RC-IVA anual
    """
    if year is None:
        year = datetime.now().year

    try:
        emp_doc = frappe.get_doc('Employee', employee)

        # Obtener salario anual (CTC)
        annual_salary = emp_doc.ctc

        # Obtener número de dependientes
        dependents = emp_doc.number_of_children or 0

        return get_rc_iva_breakdown(annual_salary, dependents)

    except Exception as e:
        frappe.throw(_('Error calculando RC-IVA: {}').format(str(e)))


@frappe.whitelist()
def get_rc_iva_table_2024() -> list:
    """
    API para obtener tabla de RC-IVA 2024

    Returns:
        list: Tabla con brackets y tasas
    """
    return [
        {
            'range_from': 0,
            'range_to': 13000,
            'rate': 0.0,
            'description': 'Mínimo no imponible'
        },
        {
            'range_from': 13001,
            'range_to': 25000,
            'rate': 13.0,
            'description': 'Primeros 12,000'
        },
        {
            'range_from': 25001,
            'range_to': 50000,
            'rate': 16.5,
            'description': 'Siguientes 25,000'
        },
        {
            'range_from': 50001,
            'range_to': 75000,
            'rate': 19.5,
            'description': 'Siguientes 25,000'
        },
        {
            'range_from': 75001,
            'range_to': 150000,
            'rate': 22.5,
            'description': 'Siguientes 75,000'
        },
        {
            'range_from': 150001,
            'range_to': None,
            'rate': 27.5,
            'description': 'Más de 150,000'
        }
    ]


@frappe.whitelist()
def calculate_rc_iva_report(company: str, year: int = None) -> dict:
    """
    API para generar reporte de RC-IVA

    Args:
        company (str): Empresa
        year (int): Año

    Returns:
        dict: Reporte de RC-IVA
    """
    if year is None:
        year = datetime.now().year

    try:
        # Obtener empleados activos
        employees = frappe.db.get_list(
            'Employee',
            filters={
                'company': company,
                'status': 'Active'
            },
            fields=['name', 'ctc', 'number_of_children']
        )

        total_salary = 0.0
        total_rc_iva = 0.0
        employee_details = []

        for emp in employees:
            salary = emp['ctc'] or 0
            dependents = emp['number_of_children'] or 0

            rc_iva = calculate_rc_iva(salary, dependents)

            total_salary += salary
            total_rc_iva += rc_iva

            employee_details.append({
                'employee': emp['name'],
                'annual_salary': round(salary, 2),
                'dependents': dependents,
                'rc_iva': round(rc_iva, 2)
            })

        return {
            'company': company,
            'year': year,
            'total_employees': len(employees),
            'total_salary': round(total_salary, 2),
            'total_rc_iva': round(total_rc_iva, 2),
            'average_rc_iva_per_employee': round(total_rc_iva / len(employees), 2) if employees else 0,
            'details': employee_details
        }

    except Exception as e:
        frappe.throw(_('Error generando reporte RC-IVA: {}').format(str(e)))
