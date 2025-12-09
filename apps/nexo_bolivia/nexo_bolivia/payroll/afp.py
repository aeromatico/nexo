# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

"""
Sistema de Aportes AFP Bolivia

AFP (Administradoras de Fondos de Pensiones) - Decreto Supremo 21060

Tasa total: 12.71%
- Aporte laboral solidario: 0.5%
- Comisión: 0.5%
- Prima riesgo común: 1.71%
- Aporte solidario del asegurado: 10% (lo paga el empleado)
"""

import frappe
from frappe import _

# Tasa AFP Total
AFP_RATE = 12.71

# Desglose de AFP
AFP_COMPONENTS = {
    'labor_solidarity': 0.5,      # Aporte laboral solidario
    'commission': 0.5,             # Comisión
    'common_risk': 1.71,           # Prima riesgo común
    'employee_contribution': 10.0  # Aporte solidario del asegurado
}

# Límites AFP
AFP_MIN_SALARY = 0      # No hay mínimo
AFP_MAX_SALARY = 999999 # No hay máximo para 2024


def calculate_afp(gross_salary: float, rate: float = None) -> float:
    """
    Calcula el aporte AFP sobre un salario

    Fórmula: Salario * 12.71 / 100

    Args:
        gross_salary (float): Salario bruto (total ganado)
        rate (float): Tasa de AFP (default: 12.71%)

    Returns:
        float: Monto del aporte AFP

    Examples:
        >>> calculate_afp(10000)
        1271.0
        >>> calculate_afp(5000)
        635.5
    """
    if rate is None:
        rate = AFP_RATE

    if gross_salary < 0:
        frappe.throw(_('Salario no puede ser negativo'))

    if rate < 0 or rate > 100:
        frappe.throw(_('Tasa AFP debe estar entre 0 y 100'))

    afp_amount = gross_salary * (rate / 100)

    return round(float(afp_amount), 2)


def get_afp_breakdown(gross_salary: float) -> dict:
    """
    Obtiene el desglose completo del aporte AFP

    Args:
        gross_salary (float): Salario bruto

    Returns:
        dict: Desglose de componentes AFP
            {
                'gross_salary': float,
                'labor_solidarity': float,
                'commission': float,
                'common_risk': float,
                'employee_contribution': float,
                'total_afp': float,
                'afp_rate': float
            }

    Examples:
        >>> breakdown = get_afp_breakdown(10000)
        >>> breakdown['labor_solidarity']
        50.0
        >>> breakdown['employee_contribution']
        1000.0
    """
    if gross_salary < 0:
        frappe.throw(_('Salario no puede ser negativo'))

    labor_solidarity = gross_salary * (AFP_COMPONENTS['labor_solidarity'] / 100)
    commission = gross_salary * (AFP_COMPONENTS['commission'] / 100)
    common_risk = gross_salary * (AFP_COMPONENTS['common_risk'] / 100)
    employee_contribution = gross_salary * (AFP_COMPONENTS['employee_contribution'] / 100)

    total_afp = labor_solidarity + commission + common_risk + employee_contribution

    return {
        'gross_salary': round(float(gross_salary), 2),
        'labor_solidarity': round(float(labor_solidarity), 2),
        'commission': round(float(commission), 2),
        'common_risk': round(float(common_risk), 2),
        'employee_contribution': round(float(employee_contribution), 2),
        'total_afp': round(float(total_afp), 2),
        'afp_rate': AFP_RATE
    }


def validate_afp_amount(afp_amount: float, gross_salary: float) -> bool:
    """
    Valida que el aporte AFP sea correcto

    Args:
        afp_amount (float): Monto de AFP a validar
        gross_salary (float): Salario bruto

    Returns:
        bool: True si es válido
    """
    expected_afp = calculate_afp(gross_salary)

    # Tolerar diferencia de 0.01 por redondeo
    return abs(afp_amount - expected_afp) <= 0.01


def apply_afp_to_salary_slip(doc, method=None):
    """
    Hook para aplicar AFP automáticamente a Salary Slip

    Args:
        doc: Documento Salary Slip
        method: Nombre del hook (validate, before_save, etc.)
    """
    if not doc.doctype == 'Salary Slip':
        return

    # Obtener salario bruto
    gross_salary = doc.gross_pay

    # Calcular AFP
    afp_amount = calculate_afp(gross_salary)

    # Buscar o crear deducción de AFP
    afp_exists = False
    for deduction in doc.deductions:
        if 'AFP' in (deduction.salary_component or ''):
            deduction.amount = afp_amount
            afp_exists = True
            break

    if not afp_exists:
        # Crear nueva deducción
        doc.append('deductions', {
            'salary_component': 'AFP 12.71%',
            'amount': afp_amount
        })

    # Recalcular totales
    doc.calculate_net_pay()


@frappe.whitelist()
def get_afp_rates() -> dict:
    """
    Obtiene las tasas de AFP vigentes

    Returns:
        dict: Información de tasas AFP
    """
    return {
        'total_rate': AFP_RATE,
        'components': AFP_COMPONENTS,
        'min_salary': AFP_MIN_SALARY,
        'max_salary': AFP_MAX_SALARY,
        'year': 2024
    }


@frappe.whitelist()
def calculate_afp_report(company: str, from_date: str, to_date: str) -> dict:
    """
    API para generar reporte de aportes AFP

    Args:
        company (str): Empresa
        from_date (str): Fecha inicio (YYYY-MM-DD)
        to_date (str): Fecha fin (YYYY-MM-DD)

    Returns:
        dict: Reporte de AFP
    """
    try:
        # Obtener todos los Salary Slip del período
        salary_slips = frappe.db.get_list(
            'Salary Slip',
            filters={
                'company': company,
                'start_date': ['>=', from_date],
                'end_date': ['<=', to_date],
                'docstatus': 1
            },
            fields=['name', 'employee', 'gross_pay']
        )

        total_gross = 0.0
        total_afp = 0.0
        employee_contributions = 0.0

        for slip in salary_slips:
            afp_amount = calculate_afp(slip['gross_pay'])
            emp_contrib = slip['gross_pay'] * (AFP_COMPONENTS['employee_contribution'] / 100)

            total_gross += slip['gross_pay']
            total_afp += afp_amount
            employee_contributions += emp_contrib

        return {
            'company': company,
            'from_date': from_date,
            'to_date': to_date,
            'salary_slips_count': len(salary_slips),
            'total_gross_salary': round(total_gross, 2),
            'total_afp': round(total_afp, 2),
            'employee_contribution': round(employee_contributions, 2),
            'employer_contribution': round(total_afp - employee_contributions, 2),
            'afp_rate': AFP_RATE
        }

    except Exception as e:
        frappe.throw(_('Error generando reporte AFP: {}').format(str(e)))
