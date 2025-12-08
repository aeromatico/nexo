# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

"""
Validadores de Impuestos Bolivia

Valida NITs, montos de impuestos, fechas fiscales, etc.
"""

import frappe
from frappe import _
import re


def validate_nit(nit):
    """
    Valida un NIT boliviano

    Formato: XXXXXXXXXX-X (10 dígitos + verificador)

    Args:
        nit (str): NIT a validar

    Returns:
        bool: True si es válido

    Raises:
        frappe.ValidationError: Si el NIT es inválido
    """
    if not nit:
        return False

    # Limpiar NIT
    nit_clean = re.sub(r'[^\d]', '', str(nit))

    # Validar longitud (al menos 7 dígitos)
    if len(nit_clean) < 7:
        frappe.throw(_('NIT debe tener al menos 7 dígitos'))

    # TODO: Implementar algoritmo de validación de dígito verificador del SIN
    # Por ahora solo validamos formato y longitud

    return True


def validate_tax_amounts(doc):
    """
    Valida que los montos de impuestos sean correctos

    Args:
        doc: Documento de factura (Sales/Purchase Invoice)

    Returns:
        bool: True si los montos son válidos
    """
    if not doc.taxes:
        return True

    for tax in doc.taxes:
        # Validar que rate esté en rango válido
        if tax.rate and (tax.rate < 0 or tax.rate > 100):
            frappe.throw(_('La tasa de impuesto {0} no es válida').format(tax.rate))

        # Validar que tax_amount sea positivo
        if tax.tax_amount and tax.tax_amount < 0:
            frappe.throw(_('El monto de impuesto no puede ser negativo'))

    return True


def validate_fiscal_year(posting_date, company):
    """
    Valida que la fecha de posting esté dentro de un año fiscal válido

    Args:
        posting_date: Fecha del documento
        company: Empresa

    Returns:
        str: Nombre del año fiscal

    Raises:
        frappe.ValidationError: Si no hay año fiscal válido
    """
    from erpnext.accounts.utils import get_fiscal_year

    try:
        fiscal_year = get_fiscal_year(posting_date, company=company)
        return fiscal_year[0]  # Retorna (fiscal_year, year_start_date, year_end_date)
    except Exception as e:
        frappe.throw(_('No se encontró un año fiscal válido para la fecha {0}').format(posting_date))


def validate_iva_rate(rate):
    """
    Valida que la tasa de IVA sea la correcta para Bolivia

    Args:
        rate (float): Tasa de IVA

    Returns:
        bool: True si la tasa es válida
    """
    valid_rates = [0, 13.0]  # 0% para exentos, 13% estándar

    if rate not in valid_rates:
        frappe.msgprint(_('La tasa de IVA {0}% no es estándar en Bolivia. La tasa normal es 13%').format(rate),
                       indicator='orange')

    return True


def validate_it_rate(rate):
    """
    Valida que la tasa de IT sea la correcta para Bolivia

    Args:
        rate (float): Tasa de IT

    Returns:
        bool: True si la tasa es válida
    """
    valid_rates = [0, 3.0]  # 0% para exentos, 3% estándar

    if rate not in valid_rates:
        frappe.msgprint(_('La tasa de IT {0}% no es estándar en Bolivia. La tasa normal es 3%').format(rate),
                       indicator='orange')

    return True


def validate_customer_tax_id(customer):
    """
    Valida que el cliente tenga NIT configurado

    Args:
        customer (str): Nombre del cliente

    Returns:
        bool: True si tiene NIT
    """
    tax_id = frappe.db.get_value('Customer', customer, 'tax_id')

    if not tax_id:
        frappe.msgprint(_('El cliente {0} no tiene NIT configurado').format(customer),
                       indicator='orange')
        return False

    # Validar formato NIT
    try:
        validate_nit(tax_id)
        return True
    except:
        return False


def validate_supplier_tax_id(supplier):
    """
    Valida que el proveedor tenga NIT configurado

    Args:
        supplier (str): Nombre del proveedor

    Returns:
        bool: True si tiene NIT
    """
    tax_id = frappe.db.get_value('Supplier', supplier, 'tax_id')

    if not tax_id:
        frappe.msgprint(_('El proveedor {0} no tiene NIT configurado').format(supplier),
                       indicator='orange')
        return False

    # Validar formato NIT
    try:
        validate_nit(tax_id)
        return True
    except:
        return False


def validate_invoice_for_bolivia(doc, method=None):
    """
    Validación completa de factura para Bolivia

    Args:
        doc: Sales Invoice o Purchase Invoice
        method: Método del hook
    """
    # Verificar que sea empresa de Bolivia
    country = frappe.db.get_value('Company', doc.company, 'country')
    if country != 'Bolivia':
        return

    # Validar año fiscal
    validate_fiscal_year(doc.posting_date, doc.company)

    # Validar cliente/proveedor tenga NIT
    if doc.doctype == 'Sales Invoice' and doc.customer:
        validate_customer_tax_id(doc.customer)
    elif doc.doctype == 'Purchase Invoice' and doc.supplier:
        validate_supplier_tax_id(doc.supplier)

    # Validar montos de impuestos
    validate_tax_amounts(doc)

    # Validar tasas de impuestos
    if doc.taxes:
        for tax in doc.taxes:
            if 'IVA' in (tax.description or ''):
                validate_iva_rate(tax.rate)
            elif 'IT' in (tax.description or '') and 'IVA' not in (tax.description or ''):
                validate_it_rate(tax.rate)


def get_tax_validation_warnings(doc):
    """
    Obtiene advertencias de validación de impuestos

    Args:
        doc: Documento de factura

    Returns:
        list: Lista de advertencias
    """
    warnings = []

    # Verificar si es empresa de Bolivia
    country = frappe.db.get_value('Company', doc.company, 'country')
    if country != 'Bolivia':
        return warnings

    # Verificar NIT
    if doc.doctype == 'Sales Invoice':
        tax_id = frappe.db.get_value('Customer', doc.customer, 'tax_id')
        if not tax_id:
            warnings.append(_('Cliente sin NIT configurado'))
    elif doc.doctype == 'Purchase Invoice':
        tax_id = frappe.db.get_value('Supplier', doc.supplier, 'tax_id')
        if not tax_id:
            warnings.append(_('Proveedor sin NIT configurado'))

    # Verificar si tiene IVA
    has_iva = False
    if doc.taxes:
        for tax in doc.taxes:
            if 'IVA' in (tax.description or ''):
                has_iva = True
                break

    if not has_iva and doc.net_total > 0:
        warnings.append(_('Factura sin IVA aplicado'))

    return warnings
