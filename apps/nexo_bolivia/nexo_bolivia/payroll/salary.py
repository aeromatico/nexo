# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

"""
Módulo de Cálculo de Salarios Bolivia

Componentes salariales según Ley General del Trabajo:
- Haber básico
- Bono de antigüedad (5% por año, máximo 100%)
- Horas extras (50% nocturno, 100% feriados)
- Subsidios y bonos
- Salario total ganado
"""

import frappe
from frappe import _
from decimal import Decimal, ROUND_HALF_UP

# Constantes Bolivia 2024
SMN = 2362  # Salario Mínimo Nacional


def calculate_base_salary(employee: str, month: int, year: int) -> float:
    """
    Calcula el salario base de un empleado para un período específico

    Args:
        employee (str): ID del empleado
        month (int): Mes (1-12)
        year (int): Año

    Returns:
        float: Salario base

    Raises:
        frappe.ValidationError: Si el empleado no existe o datos incompletos
    """
    if not frappe.db.exists('Employee', employee):
        frappe.throw(_('Empleado {} no existe'.format(employee)))

    emp_doc = frappe.get_doc('Employee', employee)

    # Obtener salario configurado
    if not emp_doc.ctc:
        frappe.throw(_('Empleado {} no tiene CTC configurado'.format(employee)))

    salary = emp_doc.ctc

    # Validar mínimo nacional
    if salary < SMN:
        frappe.msgprint(
            _('Salario {} es menor que SMN {}. Considerando SMN como mínimo.'.format(salary, SMN)),
            indicator='yellow'
        )
        salary = SMN

    return round(float(salary), 2)


def calculate_seniority_bonus(years_service: float, base_salary: float) -> float:
    """
    Calcula el bono de antigüedad según Ley General del Trabajo

    Bonificación por antigüedad: 5% por año trabajado, máximo 100%

    Args:
        years_service (float): Años de servicio
        base_salary (float): Salario base

    Returns:
        float: Monto del bono de antigüedad

    Examples:
        >>> calculate_seniority_bonus(2, 2362)  # 2 años
        236.2
        >>> calculate_seniority_bonus(20, 2362)  # 20 años (máximo 100%)
        2362
    """
    if years_service < 0:
        return 0.0

    # Máximo 100% del salario base (20 años)
    bonus_percentage = min(years_service * 5, 100)

    bonus_amount = base_salary * (bonus_percentage / 100)

    return round(float(bonus_amount), 2)


def calculate_overtime(hours: float, hourly_rate: float, overtime_type: str = 'normal') -> float:
    """
    Calcula el pago de horas extras según Ley General del Trabajo

    Tasas según tipo:
    - 'normal': 50% adicional (horas diurnas)
    - 'nocturno': 50% adicional (horas nocturnas)
    - 'festivo': 100% adicional (días festivos)

    Args:
        hours (float): Número de horas extras
        hourly_rate (float): Tarifa horaria base
        overtime_type (str): Tipo de hora extra ('normal', 'nocturno', 'festivo')

    Returns:
        float: Monto a pagar por horas extras

    Raises:
        frappe.ValidationError: Si tipo no es válido

    Examples:
        >>> calculate_overtime(2, 100, 'normal')  # 2 horas a 150 Bs/hora
        300.0
        >>> calculate_overtime(2, 100, 'festivo')  # 2 horas a 200 Bs/hora
        400.0
    """
    if hours < 0:
        frappe.throw(_('Horas extras no pueden ser negativas'))

    if hourly_rate < 0:
        frappe.throw(_('Tarifa horaria no puede ser negativa'))

    # Multiplicadores según tipo
    multipliers = {
        'normal': 1.5,      # 50% adicional
        'nocturno': 1.5,    # 50% adicional
        'festivo': 2.0      # 100% adicional
    }

    if overtime_type not in multipliers:
        frappe.throw(
            _('Tipo de hora extra inválido. Debe ser: normal, nocturno o festivo')
        )

    multiplier = multipliers[overtime_type]
    overtime_pay = hours * hourly_rate * multiplier

    return round(float(overtime_pay), 2)


def calculate_hourly_rate(monthly_salary: float, working_days: int = 22) -> float:
    """
    Calcula la tarifa horaria a partir del salario mensual

    Asume 8 horas de trabajo por día

    Args:
        monthly_salary (float): Salario mensual
        working_days (int): Días hábiles en el mes (default: 22)

    Returns:
        float: Tarifa horaria

    Examples:
        >>> calculate_hourly_rate(2362, 22)  # SMN / 22 días / 8 horas
        13.42
    """
    if working_days <= 0:
        frappe.throw(_('Días hábiles debe ser mayor a 0'))

    hourly_rate = monthly_salary / (working_days * 8)

    return round(float(hourly_rate), 2)


def calculate_daily_rate(monthly_salary: float, working_days: int = 22) -> float:
    """
    Calcula la tarifa diaria a partir del salario mensual

    Args:
        monthly_salary (float): Salario mensual
        working_days (int): Días hábiles en el mes (default: 22)

    Returns:
        float: Tarifa diaria

    Examples:
        >>> calculate_daily_rate(2362, 22)
        107.36
    """
    if working_days <= 0:
        frappe.throw(_('Días hábiles debe ser mayor a 0'))

    daily_rate = monthly_salary / working_days

    return round(float(daily_rate), 2)


def calculate_total_salary(
    base_salary: float,
    seniority_bonus: float = 0.0,
    overtime_pay: float = 0.0,
    subsidies: float = 0.0,
    bonuses: float = 0.0,
    other_allowances: float = 0.0
) -> dict:
    """
    Calcula el salario total ganado en un período

    Args:
        base_salary (float): Salario base
        seniority_bonus (float): Bono de antigüedad
        overtime_pay (float): Pago de horas extras
        subsidies (float): Subsidios
        bonuses (float): Bonos
        other_allowances (float): Otros allowances

    Returns:
        dict: Desglose del salario total
            {
                'base_salary': float,
                'seniority_bonus': float,
                'overtime_pay': float,
                'subsidies': float,
                'bonuses': float,
                'other_allowances': float,
                'gross_salary': float
            }
    """
    gross_salary = (
        base_salary +
        seniority_bonus +
        overtime_pay +
        subsidies +
        bonuses +
        other_allowances
    )

    return {
        'base_salary': round(float(base_salary), 2),
        'seniority_bonus': round(float(seniority_bonus), 2),
        'overtime_pay': round(float(overtime_pay), 2),
        'subsidies': round(float(subsidies), 2),
        'bonuses': round(float(bonuses), 2),
        'other_allowances': round(float(other_allowances), 2),
        'gross_salary': round(float(gross_salary), 2)
    }


def validate_minimum_salary(salary: float) -> bool:
    """
    Valida que el salario sea al menos el SMN

    Args:
        salary (float): Salario a validar

    Returns:
        bool: True si cumple, False si no

    Note:
        Esta es una validación informativa. El sistema debe permitir salarios
        menores en casos de reducción de jornada o períodos incompletos.
    """
    return salary >= SMN


@frappe.whitelist()
def calculate_salary_breakdown(employee: str, month: int, year: int) -> dict:
    """
    API para calcular desglose completo de salario

    Args:
        employee (str): ID del empleado
        month (int): Mes (1-12)
        year (int): Año

    Returns:
        dict: Desglose completo del salario
    """
    try:
        emp_doc = frappe.get_doc('Employee', employee)

        base_salary = calculate_base_salary(employee, month, year)

        # Calcular antigüedad
        from datetime import date
        hire_date = emp_doc.date_of_joining
        today = date(year, month, 1)
        days_worked = (today - hire_date).days
        years_service = days_worked / 365.25

        seniority_bonus = calculate_seniority_bonus(years_service, base_salary)

        # Retornar desglose
        return calculate_total_salary(base_salary, seniority_bonus)

    except Exception as e:
        frappe.throw(_('Error calculando desglose de salario: {}').format(str(e)))


@frappe.whitelist()
def get_smn() -> float:
    """
    Obtiene el salario mínimo nacional actual

    Returns:
        float: SMN en BOB
    """
    return float(SMN)
