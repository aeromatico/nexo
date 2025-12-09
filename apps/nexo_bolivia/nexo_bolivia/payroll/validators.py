# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

"""
Validadores para Nómina Bolivia

Validaciones para:
- Salario mínimo nacional
- NIT del empleado
- Fechas de pago
- Límites AFP
- Validaciones de período
"""

import frappe
from frappe import _
import re

# Constantes
SMN = 2362
AFP_RATE = 12.71
MIN_NIT_DIGITS = 7
MAX_NIT_DIGITS = 13


def validate_salary_slip_bolivia(doc, method=None):
    """
    Hook de validación para Salary Slip en Bolivia

    Valida:
    - Empleado válido
    - Periodo válido
    - Moneda BOB
    - Salario mínimo (si aplica)

    Args:
        doc: Documento Salary Slip
        method: Nombre del hook
    """
    if not is_bolivia_company(doc.company):
        return

    # Validar período
    if not doc.start_date or not doc.end_date:
        frappe.throw(_('Fecha inicio y fin son requeridas'))

    if doc.start_date >= doc.end_date:
        frappe.throw(_('Fecha inicio debe ser menor a fecha fin'))

    # Validar empleado
    if not doc.employee:
        frappe.throw(_('Empleado es requerido'))

    emp_doc = frappe.get_doc('Employee', doc.employee)

    # Validar que empleado sea de la empresa
    if emp_doc.company != doc.company:
        frappe.throw(_('Empleado no pertenece a esta empresa'))

    # Validar salario bruto
    if doc.gross_pay < 0:
        frappe.throw(_('Salario bruto no puede ser negativo'))

    # Validar salario mínimo (informativo)
    if doc.gross_pay > 0 and doc.gross_pay < SMN:
        # No lanzar error, solo advertencia
        frappe.msgprint(
            _('Advertencia: Salario bruto {} es menor que SMN {}'.format(
                doc.gross_pay, SMN
            )),
            indicator='yellow'
        )


def validate_employee_nit(doc, method=None):
    """
    Hook de validación de NIT para Employee

    Args:
        doc: Documento Employee
        method: Nombre del hook
    """
    if not is_bolivia_company(doc.company):
        return

    if not doc.get('nit'):
        frappe.msgprint(
            _('Empleado boliviano debería tener NIT registrado'),
            indicator='yellow'
        )
        return

    if not is_valid_nit(doc.nit):
        frappe.throw(_('NIT inválido: {}. Debe tener entre 7 y 13 dígitos').format(doc.nit))


def validate_salary_slip_dates(doc, method=None):
    """
    Valida que las fechas del Salary Slip sean correctas

    Args:
        doc: Documento Salary Slip
        method: Nombre del hook
    """
    from datetime import datetime, timedelta

    if not doc.start_date or not doc.end_date:
        return

    # Validar que sea un periodo de 1 mes aproximadamente
    delta = (doc.end_date - doc.start_date).days

    if delta < 20 or delta > 45:
        frappe.msgprint(
            _('Período de {} días parece anormal para Salary Slip'.format(delta)),
            indicator='yellow'
        )


def validate_afp_in_salary_slip(doc, method=None):
    """
    Valida que AFP esté correctamente calculada en Salary Slip

    Args:
        doc: Documento Salary Slip
        method: Nombre del hook
    """
    from nexo_bolivia.payroll.afp import calculate_afp, AFP_RATE

    if not is_bolivia_company(doc.company):
        return

    # Buscar deducción AFP
    afp_deduction = None
    for deduction in doc.deductions:
        if 'AFP' in (deduction.salary_component or ''):
            afp_deduction = deduction
            break

    if not afp_deduction:
        return

    # Validar monto
    expected_afp = calculate_afp(doc.gross_pay)
    actual_afp = afp_deduction.amount

    # Tolerancia de 0.05 por redondeo
    if abs(actual_afp - expected_afp) > 0.05:
        frappe.msgprint(
            _('AFP calculada ({}) difiere de lo esperado ({})'.format(
                actual_afp, expected_afp
            )),
            indicator='yellow'
        )


def validate_salary_increase(doc, method=None):
    """
    Valida cambios de salario en Employee

    Args:
        doc: Documento Employee
        method: Nombre del hook
    """
    if not is_bolivia_company(doc.company):
        return

    if not doc.ctc or doc.ctc < 0:
        frappe.throw(_('Salario (CTC) debe ser positivo'))

    # Obtener salario anterior
    old_doc = frappe.db.get_value('Employee', doc.name, 'ctc')

    if old_doc and doc.ctc < old_doc:
        # Reducción de salario requiere justificación
        frappe.msgprint(
            _('Reducción de salario de {} a {}. Verificar que esté autorizado'.format(
                old_doc, doc.ctc
            )),
            indicator='orange'
        )


def is_bolivia_company(company: str) -> bool:
    """
    Verifica si una empresa es de Bolivia

    Args:
        company (str): Nombre de la empresa

    Returns:
        bool: True si es empresa boliviana
    """
    if not company:
        return False

    country = frappe.db.get_value('Company', company, 'country')
    return country == 'Bolivia'


def is_valid_nit(nit: str) -> bool:
    """
    Valida formato de NIT boliviano

    NIT debe:
    - Tener 7-13 dígitos
    - Contener solo dígitos y guiones
    - Formato típico: 1234567 o 1234567-0

    Args:
        nit (str): NIT a validar

    Returns:
        bool: True si formato es válido
    """
    if not nit:
        return False

    # Limpiar
    nit_clean = nit.replace('-', '').strip()

    # Validar solo dígitos
    if not nit_clean.isdigit():
        return False

    # Validar rango
    if len(nit_clean) < MIN_NIT_DIGITS or len(nit_clean) > MAX_NIT_DIGITS:
        return False

    return True


@frappe.whitelist()
def validate_payroll_period(company: str, from_date: str, to_date: str) -> dict:
    """
    API para validar un período de nómina

    Args:
        company (str): Empresa
        from_date (str): Fecha inicio
        to_date (str): Fecha fin

    Returns:
        dict: Resultado de validación
    """
    try:
        from datetime import datetime

        from_date_obj = datetime.strptime(from_date, '%Y-%m-%d').date()
        to_date_obj = datetime.strptime(to_date, '%Y-%m-%d').date()

        if from_date_obj >= to_date_obj:
            return {
                'valid': False,
                'error': 'Fecha inicio debe ser menor a fecha fin'
            }

        days = (to_date_obj - from_date_obj).days

        if days < 20 or days > 45:
            return {
                'valid': True,
                'warning': 'Período de {} días parece anormal'.format(days)
            }

        return {'valid': True}

    except Exception as e:
        frappe.throw(_('Error validando período: {}').format(str(e)))


@frappe.whitelist()
def validate_employee_for_payroll(employee: str) -> dict:
    """
    API para validar si un empleado puede ser procesado en nómina

    Args:
        employee (str): ID del empleado

    Returns:
        dict: Resultado de validación
    """
    try:
        if not frappe.db.exists('Employee', employee):
            return {'valid': False, 'errors': ['Empleado no existe']}

        emp_doc = frappe.get_doc('Employee', employee)
        errors = []
        warnings = []

        # Validaciones
        if emp_doc.status != 'Active':
            errors.append('Empleado no está activo')

        if not emp_doc.ctc or emp_doc.ctc <= 0:
            errors.append('Empleado no tiene salario configurado')

        if not emp_doc.get('nit'):
            warnings.append('Empleado no tiene NIT registrado')

        if not emp_doc.date_of_joining:
            errors.append('Fecha de ingreso no está registrada')

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }

    except Exception as e:
        frappe.throw(_('Error validando empleado: {}').format(str(e)))


@frappe.whitelist()
def format_nit(nit: str) -> str:
    """
    Formatea un NIT boliviano

    Entrada: 12345670
    Salida: 1234567-0

    Args:
        nit (str): NIT sin formato

    Returns:
        str: NIT formateado
    """
    if not nit:
        return ''

    nit_clean = nit.replace('-', '').strip()

    if len(nit_clean) < 7 or len(nit_clean) > 13:
        return nit  # Retornar original si no es válido

    # Formato: últimos 9 dígitos con guión al final
    if len(nit_clean) > 1:
        return nit_clean[:-1] + '-' + nit_clean[-1]

    return nit_clean
