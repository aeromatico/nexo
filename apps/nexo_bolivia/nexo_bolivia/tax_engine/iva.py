# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

"""
Motor de Cálculo de IVA Bolivia

IVA (Impuesto al Valor Agregado):
- Tasa: 13%
- Base: Precio de venta/compra
- Aplica en: Ventas de bienes y servicios
"""

import frappe
from frappe import _


# Tasa de IVA Bolivia
IVA_RATE = 13.0


def calculate_iva(amount, rate=None):
    """
    Calcula el IVA sobre un monto

    Args:
        amount (float): Monto base
        rate (float): Tasa de IVA (default: 13%)

    Returns:
        float: Monto del IVA
    """
    if rate is None:
        rate = IVA_RATE

    iva = amount * (rate / 100)
    return round(iva, 2)


def calculate_total_with_iva(amount, rate=None):
    """
    Calcula el total incluyendo IVA

    Args:
        amount (float): Monto base
        rate (float): Tasa de IVA (default: 13%)

    Returns:
        dict: {'base': amount, 'iva': iva_amount, 'total': total}
    """
    if rate is None:
        rate = IVA_RATE

    iva_amount = calculate_iva(amount, rate)
    total = amount + iva_amount

    return {
        'base': round(amount, 2),
        'iva': iva_amount,
        'total': round(total, 2),
        'rate': rate
    }


def extract_iva_from_total(total_with_iva, rate=None):
    """
    Extrae el IVA de un monto total que ya incluye IVA

    Args:
        total_with_iva (float): Monto total con IVA incluido
        rate (float): Tasa de IVA (default: 13%)

    Returns:
        dict: {'base': base_amount, 'iva': iva_amount, 'total': total}
    """
    if rate is None:
        rate = IVA_RATE

    # Total = Base + (Base * rate/100)
    # Total = Base * (1 + rate/100)
    # Base = Total / (1 + rate/100)

    divisor = 1 + (rate / 100)
    base_amount = total_with_iva / divisor
    iva_amount = total_with_iva - base_amount

    return {
        'base': round(base_amount, 2),
        'iva': round(iva_amount, 2),
        'total': round(total_with_iva, 2),
        'rate': rate
    }


def apply_iva_to_invoice(doc, method=None):
    """
    Hook para aplicar IVA automáticamente a facturas

    Este método se ejecuta antes de guardar una factura (Sales/Purchase Invoice)
    y aplica automáticamente el IVA del 13% si corresponde.

    Args:
        doc: Documento de factura (Sales Invoice o Purchase Invoice)
        method: Método del hook (before_save, validate, etc.)
    """
    # Verificar si la empresa es de Bolivia
    if not is_bolivia_company(doc.company):
        return

    # Verificar si ya tiene IVA aplicado
    if has_iva_tax(doc):
        return

    # Aplicar IVA del 13%
    add_iva_tax_row(doc)


def is_bolivia_company(company):
    """
    Verifica si una empresa es de Bolivia

    Args:
        company (str): Nombre de la empresa

    Returns:
        bool: True si la empresa es de Bolivia
    """
    if not company:
        return False

    country = frappe.db.get_value('Company', company, 'country')
    return country == 'Bolivia'


def has_iva_tax(doc):
    """
    Verifica si el documento ya tiene IVA aplicado

    Args:
        doc: Documento de factura

    Returns:
        bool: True si ya tiene IVA
    """
    if not doc.taxes:
        return False

    for tax in doc.taxes:
        # Buscar por descripción o nombre de cuenta
        if 'IVA' in (tax.description or '') or 'IVA' in (tax.account_head or ''):
            return True

    return False


def add_iva_tax_row(doc):
    """
    Agrega una fila de IVA a la tabla de impuestos

    Args:
        doc: Documento de factura
    """
    # Obtener cuenta de IVA según tipo de documento
    if doc.doctype == 'Sales Invoice':
        # IVA por Pagar (ventas)
        iva_account = get_iva_account(doc.company, 'IVA por Pagar')
    else:
        # IVA Crédito Fiscal (compras)
        iva_account = get_iva_account(doc.company, 'IVA Crédito Fiscal')

    if not iva_account:
        frappe.msgprint(_('Cuenta de IVA no configurada para esta empresa'))
        return

    # Agregar fila de impuesto
    doc.append('taxes', {
        'charge_type': 'On Net Total',
        'account_head': iva_account,
        'description': f'IVA {IVA_RATE}%',
        'rate': IVA_RATE,
        'included_in_print_rate': 0
    })

    # Recalcular totales
    doc.calculate_taxes_and_totals()


def get_iva_account(company, account_name):
    """
    Obtiene la cuenta de IVA para una empresa

    Args:
        company (str): Nombre de la empresa
        account_name (str): Nombre de la cuenta (ej: 'IVA por Pagar')

    Returns:
        str: Nombre completo de la cuenta o None
    """
    # Buscar en Plan Cuentas Bolivia primero
    abbr = frappe.get_cached_value('Company', company, 'abbr')

    # Buscar por número de cuenta
    account_numbers = {
        'IVA por Pagar': '2121',
        'IVA Crédito Fiscal': '1141'
    }

    account_number = account_numbers.get(account_name)
    if account_number:
        account = frappe.db.get_value('Plan Cuentas Bolivia',
                                      {'account_number': account_number, 'company': company},
                                      'account_name')
        if account:
            return f"{account} - {abbr}"

    # Buscar directamente en Account
    account = frappe.db.get_value('Account',
                                  {'account_name': account_name, 'company': company},
                                  'name')

    return account


def get_iva_credit_fiscal(invoice):
    """
    Calcula el IVA Crédito Fiscal de una factura de compra

    Args:
        invoice: Purchase Invoice

    Returns:
        float: Monto de IVA CF
    """
    if not invoice.taxes:
        return 0.0

    total_iva = 0.0
    for tax in invoice.taxes:
        if 'IVA' in (tax.description or ''):
            total_iva += tax.tax_amount

    return round(total_iva, 2)


def get_iva_debit_fiscal(invoice):
    """
    Calcula el IVA Débito Fiscal de una factura de venta

    Args:
        invoice: Sales Invoice

    Returns:
        float: Monto de IVA DF
    """
    if not invoice.taxes:
        return 0.0

    total_iva = 0.0
    for tax in invoice.taxes:
        if 'IVA' in (tax.description or ''):
            total_iva += tax.tax_amount

    return round(total_iva, 2)


def calculate_iva_balance(company, from_date, to_date):
    """
    Calcula el balance de IVA (DF - CF) para un periodo

    Balance positivo = IVA a pagar
    Balance negativo = IVA a favor del contribuyente

    Args:
        company (str): Empresa
        from_date (str): Fecha inicio
        to_date (str): Fecha fin

    Returns:
        dict: Balance de IVA
    """
    # IVA Débito Fiscal (ventas)
    iva_df = frappe.db.sql("""
        SELECT SUM(ti.tax_amount)
        FROM `tabSales Invoice` si
        INNER JOIN `tabSales Taxes and Charges` ti ON ti.parent = si.name
        WHERE si.company = %s
        AND si.docstatus = 1
        AND si.posting_date BETWEEN %s AND %s
        AND ti.description LIKE %s
    """, (company, from_date, to_date, '%IVA%'))[0][0] or 0

    # IVA Crédito Fiscal (compras)
    iva_cf = frappe.db.sql("""
        SELECT SUM(ti.tax_amount)
        FROM `tabPurchase Invoice` pi
        INNER JOIN `tabPurchase Taxes and Charges` ti ON ti.parent = pi.name
        WHERE pi.company = %s
        AND pi.docstatus = 1
        AND pi.posting_date BETWEEN %s AND %s
        AND ti.description LIKE %s
    """, (company, from_date, to_date, '%IVA%'))[0][0] or 0

    balance = iva_df - iva_cf

    return {
        'iva_debit_fiscal': round(iva_df, 2),
        'iva_credit_fiscal': round(iva_cf, 2),
        'balance': round(balance, 2),
        'status': 'Por Pagar' if balance > 0 else ('A Favor' if balance < 0 else 'Sin Balance')
    }


@frappe.whitelist()
def get_iva_report(company, from_date, to_date):
    """
    API para obtener reporte de IVA

    Args:
        company (str): Empresa
        from_date (str): Fecha inicio
        to_date (str): Fecha fin

    Returns:
        dict: Reporte de IVA
    """
    return calculate_iva_balance(company, from_date, to_date)
