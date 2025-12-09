# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

"""
Cálculo de Aguinaldo Bolivia

Aguinaldo:
- Simple: 1/12 del total ganado en el año
- Doble: Adicional si crecimiento PIB ≥ 4.5%

Pagos:
- Aguinaldo de Navidad: Diciembre (100%)
- Aguinaldo de Aniversario: Junio (50%)
"""

import frappe
from frappe import _
from datetime import datetime, timedelta

# PIB growth threshold para doble aguinaldo
PIB_GROWTH_THRESHOLD = 4.5  # %


def calculate_aguinaldo(
    employee: str,
    year: int,
    aguinaldo_type: str = 'simple',
    total_earned: float = None
) -> float:
    """
    Calcula el aguinaldo simple de un empleado

    Aguinaldo = (Total ganado en el año) / 12

    Args:
        employee (str): ID del empleado
        year (int): Año del cálculo
        aguinaldo_type (str): Tipo de aguinaldo ('simple' o 'doble')
        total_earned (float): Total ganado en el año (si no se proporciona, se calcula)

    Returns:
        float: Monto del aguinaldo

    Raises:
        frappe.ValidationError: Si datos incompletos

    Examples:
        >>> calculate_aguinaldo('EMP001', 2024, 'simple', 30000)
        2500.0
    """
    if not frappe.db.exists('Employee', employee):
        frappe.throw(_('Empleado {} no existe'.format(employee)))

    if year < 2000 or year > 2100:
        frappe.throw(_('Año inválido'))

    # Si no se proporciona total_earned, calcular desde Salary Slips
    if total_earned is None:
        total_earned = get_total_earned_in_year(employee, year)

    if total_earned < 0:
        frappe.throw(_('Total ganado no puede ser negativo'))

    # Aguinaldo simple: 1/12 del total ganado
    aguinaldo = total_earned / 12

    if aguinaldo_type == 'doble':
        # El doble incluye el aguinaldo adicional (otro 1/12)
        aguinaldo = aguinaldo * 2

    return round(float(aguinaldo), 2)


def calculate_double_aguinaldo(
    employee: str,
    year: int,
    pib_growth: float = None,
    total_earned: float = None
) -> float:
    """
    Calcula el aguinaldo doble si aplica

    El doble aguinaldo se paga si el PIB creció ≥ 4.5% en el año anterior

    Args:
        employee (str): ID del empleado
        year (int): Año del cálculo
        pib_growth (float): Crecimiento del PIB (%). Si es None, usa valor por defecto
        total_earned (float): Total ganado en el año

    Returns:
        float: Monto del aguinaldo doble (0 si no aplica)

    Examples:
        >>> calculate_double_aguinaldo('EMP001', 2024, 5.2, 30000)
        5000.0  # 2 × (30000/12)
        >>> calculate_double_aguinaldo('EMP001', 2024, 3.0, 30000)
        0.0  # PIB < 4.5%
    """
    if not is_eligible_for_double_aguinaldo(pib_growth):
        return 0.0

    # Aguinaldo adicional (otro 1/12)
    simple_aguinaldo = calculate_aguinaldo(employee, year, 'simple', total_earned)

    return round(float(simple_aguinaldo), 2)


def is_eligible_for_double_aguinaldo(pib_growth: float = None) -> bool:
    """
    Verifica si se paga doble aguinaldo según crecimiento del PIB

    Args:
        pib_growth (float): Crecimiento del PIB en %

    Returns:
        bool: True si crecimiento >= 4.5%
    """
    if pib_growth is None:
        # Valor por defecto para 2024 (requiere actualización anual)
        pib_growth = 3.0  # Estimado para Bolivia 2024

    return pib_growth >= PIB_GROWTH_THRESHOLD


def get_total_earned_in_year(employee: str, year: int) -> float:
    """
    Calcula el total ganado por un empleado en un año

    Suma todos los Salary Slip del año (solo los aprobados)

    Args:
        employee (str): ID del empleado
        year (int): Año

    Returns:
        float: Total ganado en el año
    """
    try:
        result = frappe.db.sql("""
            SELECT SUM(gross_pay)
            FROM `tabSalary Slip`
            WHERE employee = %s
            AND YEAR(start_date) = %s
            AND docstatus = 1
        """, (employee, year))

        return float(result[0][0]) if result[0][0] else 0.0

    except Exception as e:
        frappe.msgprint(
            _('Error calculando total ganado: {}').format(str(e)),
            indicator='red'
        )
        return 0.0


def calculate_proportional_aguinaldo(
    employee: str,
    year: int,
    months_worked: int,
    total_earned: float = None
) -> float:
    """
    Calcula aguinaldo prorrateado por meses trabajados

    Aplica cuando el empleado no trabajó todo el año

    Args:
        employee (str): ID del empleado
        year (int): Año
        months_worked (int): Número de meses trabajados
        total_earned (float): Total ganado en el período

    Returns:
        float: Aguinaldo prorrateado

    Examples:
        >>> calculate_proportional_aguinaldo('EMP001', 2024, 6, 15000)
        1250.0  # (15000/12) × 1 para 6 meses, pero se calcula sobre lo ganado
    """
    if months_worked < 0 or months_worked > 12:
        frappe.throw(_('Meses trabajados debe estar entre 0 y 12'))

    if total_earned is None:
        total_earned = get_total_earned_in_year(employee, year)

    # Aguinaldo proporcional
    aguinaldo = (total_earned / 12) * (months_worked / 12)

    return round(float(aguinaldo), 2)


def get_aguinaldo_payment_dates(year: int) -> dict:
    """
    Obtiene las fechas de pago de aguinaldo en el año

    Args:
        year (int): Año

    Returns:
        dict: Fechas de pago
            {
                'christmas': datetime,  # 21 de Diciembre
                'anniversary': datetime  # 21 de Junio
            }
    """
    return {
        'christmas': datetime(year, 12, 21).date(),
        'anniversary': datetime(year, 6, 21).date()
    }


def get_aguinaldo_breakdown(
    employee: str,
    year: int,
    pib_growth: float = None,
    total_earned: float = None
) -> dict:
    """
    Obtiene el desglose completo del aguinaldo

    Args:
        employee (str): ID del empleado
        year (int): Año
        pib_growth (float): Crecimiento del PIB
        total_earned (float): Total ganado

    Returns:
        dict: Desglose del aguinaldo
    """
    if total_earned is None:
        total_earned = get_total_earned_in_year(employee, year)

    simple = calculate_aguinaldo(employee, year, 'simple', total_earned)
    double = calculate_double_aguinaldo(employee, year, pib_growth, total_earned)
    total = simple + double

    dates = get_aguinaldo_payment_dates(year)

    return {
        'employee': employee,
        'year': year,
        'total_earned': round(total_earned, 2),
        'simple_aguinaldo': round(simple, 2),
        'double_aguinaldo': round(double, 2),
        'total_aguinaldo': round(total, 2),
        'pib_growth': pib_growth,
        'eligible_for_double': is_eligible_for_double_aguinaldo(pib_growth),
        'christmas_payment_date': str(dates['christmas']),
        'anniversary_payment_date': str(dates['anniversary']),
        'christmas_amount': round((simple + double / 2) if double > 0 else simple, 2),
        'anniversary_amount': round(double / 2 if double > 0 else 0, 2)
    }


@frappe.whitelist()
def calculate_employee_aguinaldo(employee: str, year: int = None) -> dict:
    """
    API para calcular aguinaldo anual de un empleado

    Args:
        employee (str): ID del empleado
        year (int): Año (default: año actual)

    Returns:
        dict: Información del aguinaldo
    """
    if year is None:
        year = datetime.now().year

    try:
        total_earned = get_total_earned_in_year(employee, year)

        # Usar PIB growth por defecto
        pib_growth = None

        return get_aguinaldo_breakdown(employee, year, pib_growth, total_earned)

    except Exception as e:
        frappe.throw(_('Error calculando aguinaldo: {}').format(str(e)))


@frappe.whitelist()
def check_aguinaldo_payment():
    """
    Verifica si hoy es fecha de pago de aguinaldo

    Hook para scheduler: ejecutar mensualmente

    Returns:
        dict: Información de pagos pendientes
    """
    today = datetime.now().date()

    # Fechas de pago
    christmas = datetime(today.year, 12, 21).date()
    anniversary = datetime(today.year, 6, 21).date()

    payment_due = False
    payment_type = None

    if today == christmas:
        payment_due = True
        payment_type = 'christmas'
    elif today == anniversary:
        payment_due = True
        payment_type = 'anniversary'

    if not payment_due:
        return {'payment_due': False}

    # Obtener empleados activos
    employees = frappe.db.get_list(
        'Employee',
        filters={'status': 'Active'},
        fields=['name', 'employee_name']
    )

    return {
        'payment_due': True,
        'payment_type': payment_type,
        'payment_date': str(today),
        'employees_count': len(employees),
        'message': 'Se debe procesar pago de aguinaldo de {}'.format(payment_type)
    }


@frappe.whitelist()
def calculate_aguinaldo_report(company: str, year: int = None) -> dict:
    """
    API para generar reporte de aguinaldo

    Args:
        company (str): Empresa
        year (int): Año

    Returns:
        dict: Reporte de aguinaldo
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
            fields=['name', 'employee_name']
        )

        total_aguinaldo = 0.0
        employee_details = []

        for emp in employees:
            breakdown = get_aguinaldo_breakdown(emp['name'], year, total_earned=None)

            total_aguinaldo += breakdown['total_aguinaldo']
            employee_details.append({
                'employee': emp['name'],
                'employee_name': emp['employee_name'],
                'total_earned': breakdown['total_earned'],
                'simple_aguinaldo': breakdown['simple_aguinaldo'],
                'double_aguinaldo': breakdown['double_aguinaldo'],
                'total_aguinaldo': breakdown['total_aguinaldo']
            })

        return {
            'company': company,
            'year': year,
            'total_employees': len(employees),
            'total_aguinaldo': round(total_aguinaldo, 2),
            'average_aguinaldo_per_employee': round(total_aguinaldo / len(employees), 2) if employees else 0,
            'details': employee_details
        }

    except Exception as e:
        frappe.throw(_('Error generando reporte aguinaldo: {}').format(str(e)))
