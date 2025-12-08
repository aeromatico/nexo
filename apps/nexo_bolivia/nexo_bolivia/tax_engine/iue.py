# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

"""
Motor de Cálculo de IUE Bolivia

IUE (Impuesto sobre las Utilidades de las Empresas):
- Tasa: 25%
- Base: Utilidad neta del ejercicio fiscal
- Periodo: Anual
- Compensable con IT pagado
"""

import frappe
from frappe import _


# Tasa de IUE Bolivia
IUE_RATE = 25.0


def calculate_iue(net_profit, rate=None):
    """
    Calcula el IUE sobre la utilidad neta

    Args:
        net_profit (float): Utilidad neta del ejercicio
        rate (float): Tasa de IUE (default: 25%)

    Returns:
        float: Monto del IUE
    """
    if rate is None:
        rate = IUE_RATE

    if net_profit <= 0:
        return 0.0

    iue = net_profit * (rate / 100)
    return round(iue, 2)


def calculate_iue_with_it_compensation(net_profit, it_paid, rate=None):
    """
    Calcula el IUE compensando el IT pagado durante el año

    IUE a pagar = IUE calculado - IT pagado (100% compensable)

    Args:
        net_profit (float): Utilidad neta del ejercicio
        it_paid (float): IT pagado durante el año
        rate (float): Tasa de IUE (default: 25%)

    Returns:
        dict: Detalle del cálculo IUE
    """
    if rate is None:
        rate = IUE_RATE

    # Calcular IUE base
    iue_base = calculate_iue(net_profit, rate)

    # Compensar con IT (100% compensable según normativa)
    it_compensation = min(it_paid, iue_base)  # No puede ser más que el IUE
    iue_to_pay = iue_base - it_compensation

    return {
        'net_profit': round(net_profit, 2),
        'iue_base': iue_base,
        'it_paid': round(it_paid, 2),
        'it_compensation': round(it_compensation, 2),
        'iue_to_pay': round(max(iue_to_pay, 0), 2),  # No puede ser negativo
        'rate': rate
    }


def calculate_net_profit_for_fiscal_year(company, fiscal_year):
    """
    Calcula la utilidad neta para un año fiscal

    Args:
        company (str): Empresa
        fiscal_year (str): Año fiscal

    Returns:
        float: Utilidad neta
    """
    from_date, to_date = frappe.db.get_value('Fiscal Year', fiscal_year,
                                             ['year_start_date', 'year_end_date'])

    # Obtener Profit and Loss
    from erpnext.accounts.utils import get_fiscal_year

    # Ingresos totales
    income = frappe.db.sql("""
        SELECT SUM(gl.debit - gl.credit)
        FROM `tabGL Entry` gl
        INNER JOIN `tabAccount` acc ON acc.name = gl.account
        WHERE gl.company = %s
        AND gl.posting_date BETWEEN %s AND %s
        AND gl.is_cancelled = 0
        AND acc.root_type = 'Income'
    """, (company, from_date, to_date))[0][0] or 0

    # Egresos totales
    expense = frappe.db.sql("""
        SELECT SUM(gl.debit - gl.credit)
        FROM `tabGL Entry` gl
        INNER JOIN `tabAccount` acc ON acc.name = gl.account
        WHERE gl.company = %s
        AND gl.posting_date BETWEEN %s AND %s
        AND gl.is_cancelled = 0
        AND acc.root_type = 'Expense'
    """, (company, from_date, to_date))[0][0] or 0

    # Utilidad neta = Ingresos - Egresos
    net_profit = abs(income) - abs(expense)

    return round(net_profit, 2)


def calculate_iue_for_fiscal_year(company, fiscal_year):
    """
    Calcula el IUE completo para un año fiscal

    Args:
        company (str): Empresa
        fiscal_year (str): Año fiscal

    Returns:
        dict: Detalle completo del IUE
    """
    # Calcular utilidad neta
    net_profit = calculate_net_profit_for_fiscal_year(company, fiscal_year)

    # Obtener IT pagado durante el año
    from_date, to_date = frappe.db.get_value('Fiscal Year', fiscal_year,
                                             ['year_start_date', 'year_end_date'])

    from nexo_bolivia.tax_engine.it import calculate_it_for_period
    it_data = calculate_it_for_period(company, from_date, to_date)
    it_paid = it_data['total_it']

    # Calcular IUE con compensación IT
    iue_data = calculate_iue_with_it_compensation(net_profit, it_paid)

    # Agregar información adicional
    iue_data['company'] = company
    iue_data['fiscal_year'] = fiscal_year
    iue_data['from_date'] = from_date
    iue_data['to_date'] = to_date

    return iue_data


def create_iue_journal_entry(company, fiscal_year):
    """
    Crea el asiento contable para el IUE

    Args:
        company (str): Empresa
        fiscal_year (str): Año fiscal

    Returns:
        str: Nombre del Journal Entry creado
    """
    # Calcular IUE
    iue_data = calculate_iue_for_fiscal_year(company, fiscal_year)

    if iue_data['iue_to_pay'] <= 0:
        frappe.msgprint(_('No hay IUE a pagar para este periodo'))
        return None

    # Obtener cuentas
    abbr = frappe.get_cached_value('Company', company, 'abbr')

    # Cuenta IUE por Pagar (2123)
    iue_payable = frappe.db.get_value('Plan Cuentas Bolivia',
                                      {'account_number': '2123', 'company': company},
                                      'account_name')
    if iue_payable:
        iue_payable = f"{iue_payable} - {abbr}"

    # Cuenta IUE Gasto (5412)
    iue_expense = frappe.db.get_value('Plan Cuentas Bolivia',
                                     {'account_number': '5412', 'company': company},
                                     'account_name')
    if iue_expense:
        iue_expense = f"{iue_expense} - {abbr}"

    if not iue_payable or not iue_expense:
        frappe.throw(_('Cuentas de IUE no configuradas'))

    # Crear Journal Entry
    je = frappe.get_doc({
        'doctype': 'Journal Entry',
        'company': company,
        'posting_date': iue_data['to_date'],
        'voucher_type': 'Journal Entry',
        'user_remark': f'IUE {fiscal_year} - Utilidad: {iue_data["net_profit"]}, IT Compensado: {iue_data["it_compensation"]}',
        'accounts': [
            {
                'account': iue_expense,
                'debit_in_account_currency': iue_data['iue_base'],
                'credit_in_account_currency': 0
            },
            {
                'account': iue_payable,
                'debit_in_account_currency': 0,
                'credit_in_account_currency': iue_data['iue_to_pay']
            }
        ]
    })

    # Si hay compensación IT, agregar la cuenta
    if iue_data['it_compensation'] > 0:
        # Cuenta IT Pagado por Anticipado (1142)
        it_prepaid = frappe.db.get_value('Plan Cuentas Bolivia',
                                        {'account_number': '1142', 'company': company},
                                        'account_name')
        if it_prepaid:
            it_prepaid = f"{it_prepaid} - {abbr}"
            je.append('accounts', {
                'account': it_prepaid,
                'debit_in_account_currency': 0,
                'credit_in_account_currency': iue_data['it_compensation']
            })

    je.insert()
    je.submit()

    return je.name


@frappe.whitelist()
def get_iue_report(company, fiscal_year):
    """
    API para obtener reporte de IUE

    Args:
        company (str): Empresa
        fiscal_year (str): Año fiscal

    Returns:
        dict: Reporte de IUE
    """
    return calculate_iue_for_fiscal_year(company, fiscal_year)


@frappe.whitelist()
def create_iue_provision(company, fiscal_year):
    """
    API para crear el asiento de provisión de IUE

    Args:
        company (str): Empresa
        fiscal_year (str): Año fiscal

    Returns:
        str: Nombre del Journal Entry
    """
    return create_iue_journal_entry(company, fiscal_year)
