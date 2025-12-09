# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

"""
Cálculo de Prima Anual Bolivia

Prima:
- 1 mes de sueldo por año trabajado
- Calculado sobre último sueldo
- Pago proporcional si < 1 año

Pago: Cuando se termina el vínculo laboral
"""

import frappe
from frappe import _
from datetime import datetime, timedelta


def calculate_prima_anual(
    employee: str,
    base_salary: float = None,
    months_worked: float = None
) -> float:
    """
    Calcula la prima anual de un empleado

    Prima = (Días trabajados / 365) × Salario

    Args:
        employee (str): ID del empleado
        base_salary (float): Salario base para el cálculo (si es None, se obtiene del empleado)
        months_worked (float): Meses trabajados (si es None, se calcula desde fecha de ingreso)

    Returns:
        float: Monto de la prima anual

    Raises:
        frappe.ValidationError: Si empleado no existe

    Examples:
        >>> calculate_prima_anual('EMP001', 2362, 12)  # 1 año completo
        2362.0
        >>> calculate_prima_anual('EMP001', 2362, 6)  # 6 meses
        1181.0
        >>> calculate_prima_anual('EMP001', 2362, 1)  # 1 mes
        196.83
    """
    if not frappe.db.exists('Employee', employee):
        frappe.throw(_('Empleado {} no existe'.format(employee)))

    emp_doc = frappe.get_doc('Employee', employee)

    # Obtener salario base
    if base_salary is None:
        base_salary = emp_doc.ctc or 0

    if base_salary <= 0:
        frappe.throw(_('Empleado {} no tiene salario configurado'.format(employee)))

    # Calcular meses trabajados si no se proporciona
    if months_worked is None:
        months_worked = get_months_worked(emp_doc)

    if months_worked < 0:
        frappe.throw(_('Meses trabajados no puede ser negativo'))

    # Prima = (Meses trabajados / 12) × Salario
    prima = (months_worked / 12) * base_salary

    return round(float(prima), 2)


def get_months_worked(emp_doc) -> float:
    """
    Calcula los meses trabajados desde la fecha de ingreso

    Args:
        emp_doc: Documento Employee

    Returns:
        float: Número de meses trabajados
    """
    hire_date = emp_doc.date_of_joining
    if not hire_date:
        return 0

    # Si hay fecha de salida, usar hasta esa fecha
    if emp_doc.relieving_date:
        end_date = emp_doc.relieving_date
    else:
        end_date = datetime.now().date()

    # Convertir a datetime si es necesario
    if isinstance(hire_date, datetime):
        hire_date = hire_date.date()
    if isinstance(end_date, datetime):
        end_date = end_date.date()

    # Calcular diferencia
    delta = end_date - hire_date
    months = delta.days / 30.44  # Promedio días por mes

    return max(0, months)


def calculate_prima_at_termination(employee: str) -> float:
    """
    Calcula la prima al momento de terminación del vínculo laboral

    Args:
        employee (str): ID del empleado

    Returns:
        float: Monto de prima a pagar

    Raises:
        frappe.ValidationError: Si empleado no tiene fecha de salida
    """
    emp_doc = frappe.get_doc('Employee', employee)

    if not emp_doc.relieving_date:
        frappe.throw(_('Empleado {} aún está activo'.format(employee)))

    # Usar salario del último período
    last_salary_slip = frappe.db.get_list(
        'Salary Slip',
        filters={
            'employee': employee,
            'docstatus': 1
        },
        order_by='start_date desc',
        limit=1,
        fields=['gross_pay']
    )

    base_salary = last_salary_slip[0]['gross_pay'] if last_salary_slip else emp_doc.ctc

    months_worked = get_months_worked(emp_doc)

    return calculate_prima_anual(employee, base_salary, months_worked)


def get_prima_breakdown(
    employee: str,
    base_salary: float = None,
    months_worked: float = None
) -> dict:
    """
    Obtiene el desglose completo de la prima anual

    Args:
        employee (str): ID del empleado
        base_salary (float): Salario base
        months_worked (float): Meses trabajados

    Returns:
        dict: Desglose de prima
    """
    if base_salary is None or months_worked is None:
        emp_doc = frappe.get_doc('Employee', employee)

        if base_salary is None:
            base_salary = emp_doc.ctc or 0

        if months_worked is None:
            months_worked = get_months_worked(emp_doc)

    prima = calculate_prima_anual(employee, base_salary, months_worked)

    # Prima por cada año completo
    complete_years = int(months_worked // 12)
    remaining_months = months_worked % 12

    prima_per_year = base_salary
    prima_for_complete_years = prima_per_year * complete_years
    prima_for_remaining_months = (remaining_months / 12) * base_salary

    return {
        'employee': employee,
        'base_salary': round(base_salary, 2),
        'months_worked': round(months_worked, 2),
        'complete_years': complete_years,
        'remaining_months': round(remaining_months, 2),
        'prima_per_year': round(prima_per_year, 2),
        'prima_for_complete_years': round(prima_for_complete_years, 2),
        'prima_for_remaining_months': round(prima_for_remaining_months, 2),
        'total_prima': round(prima, 2)
    }


def is_eligible_for_prima(employee: str) -> bool:
    """
    Verifica si un empleado tiene derecho a prima anual

    Requisitos:
    - Haber trabajado al menos 30 días

    Args:
        employee (str): ID del empleado

    Returns:
        bool: True si es elegible
    """
    emp_doc = frappe.get_doc('Employee', employee)

    months_worked = get_months_worked(emp_doc)

    # Mínimo 1 mes (30 días)
    return months_worked >= 1


@frappe.whitelist()
def calculate_employee_prima(employee: str) -> dict:
    """
    API para calcular prima anual de un empleado

    Args:
        employee (str): ID del empleado

    Returns:
        dict: Información de prima
    """
    try:
        if not is_eligible_for_prima(employee):
            return {
                'employee': employee,
                'eligible': False,
                'message': 'Empleado no cumple requisitos mínimos para prima'
            }

        return {
            'eligible': True,
            **get_prima_breakdown(employee)
        }

    except Exception as e:
        frappe.throw(_('Error calculando prima: {}').format(str(e)))


@frappe.whitelist()
def calculate_prima_report(company: str) -> dict:
    """
    API para generar reporte de prima anual

    Args:
        company (str): Empresa

    Returns:
        dict: Reporte de prima
    """
    try:
        # Obtener empleados activos
        employees = frappe.db.get_list(
            'Employee',
            filters={
                'company': company,
                'status': 'Active'
            },
            fields=['name', 'employee_name', 'ctc', 'date_of_joining', 'relieving_date']
        )

        total_prima = 0.0
        eligible_count = 0
        employee_details = []

        for emp in employees:
            if is_eligible_for_prima(emp['name']):
                breakdown = get_prima_breakdown(emp['name'])

                total_prima += breakdown['total_prima']
                eligible_count += 1

                employee_details.append({
                    'employee': emp['name'],
                    'employee_name': emp['employee_name'],
                    'months_worked': breakdown['months_worked'],
                    'prima': breakdown['total_prima']
                })

        return {
            'company': company,
            'total_employees': len(employees),
            'eligible_employees': eligible_count,
            'total_prima': round(total_prima, 2),
            'average_prima_per_employee': round(total_prima / eligible_count, 2) if eligible_count > 0 else 0,
            'details': employee_details
        }

    except Exception as e:
        frappe.throw(_('Error generando reporte prima: {}').format(str(e)))


@frappe.whitelist()
def calculate_prima_at_termination_api(employee: str) -> dict:
    """
    API para calcular prima al momento de terminación

    Args:
        employee (str): ID del empleado

    Returns:
        dict: Prima a pagar
    """
    try:
        prima = calculate_prima_at_termination(employee)
        breakdown = get_prima_breakdown(employee)

        return {
            'employee': employee,
            'status': 'Termination',
            'prima_to_pay': round(prima, 2),
            'breakdown': breakdown
        }

    except Exception as e:
        frappe.throw(_('Error calculando prima de terminación: {}').format(str(e)))
