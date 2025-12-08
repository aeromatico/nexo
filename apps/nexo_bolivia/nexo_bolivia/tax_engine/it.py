# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

"""
Motor de Cálculo de IT Bolivia

IT (Impuesto a las Transacciones):
- Tasa: 3%
- Base: Total de la transacción
- Aplica en: Todas las transacciones económicas
- Compensable con IUE
"""

import frappe
from frappe import _


# Tasa de IT Bolivia
IT_RATE = 3.0


def calculate_it(amount, rate=None):
    """
    Calcula el IT sobre un monto

    Args:
        amount (float): Monto de la transacción
        rate (float): Tasa de IT (default: 3%)

    Returns:
        float: Monto del IT
    """
    if rate is None:
        rate = IT_RATE

    it = amount * (rate / 100)
    return round(it, 2)


def calculate_total_with_it(amount, rate=None):
    """
    Calcula el total incluyendo IT

    Args:
        amount (float): Monto base
        rate (float): Tasa de IT (default: 3%)

    Returns:
        dict: {'base': amount, 'it': it_amount, 'total': total}
    """
    if rate is None:
        rate = IT_RATE

    it_amount = calculate_it(amount, rate)
    total = amount + it_amount

    return {
        'base': round(amount, 2),
        'it': it_amount,
        'total': round(total, 2),
        'rate': rate
    }


def apply_it_to_invoice(doc, method=None):
    """
    Hook para aplicar IT automáticamente a facturas

    El IT se aplica sobre el total de la transacción (incluyendo IVA)

    Args:
        doc: Documento de factura (Sales Invoice o Purchase Invoice)
        method: Método del hook
    """
    # Verificar si la empresa es de Bolivia
    if not is_bolivia_company(doc.company):
        return

    # Verificar si ya tiene IT aplicado
    if has_it_tax(doc):
        return

    # El IT se aplica solo a ventas (generalmente)
    if doc.doctype == 'Sales Invoice':
        add_it_tax_row(doc)


def apply_it_to_payment(doc, method=None):
    """
    Hook para aplicar IT a pagos

    Args:
        doc: Payment Entry
        method: Método del hook
    """
    # Verificar si la empresa es de Bolivia
    if not is_bolivia_company(doc.company):
        return

    # Calcular IT sobre el monto pagado
    if doc.paid_amount and doc.paid_amount > 0:
        it_amount = calculate_it(doc.paid_amount)

        # Crear asiento contable para IT
        create_it_journal_entry(doc, it_amount)


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


def has_it_tax(doc):
    """
    Verifica si el documento ya tiene IT aplicado

    Args:
        doc: Documento de factura

    Returns:
        bool: True si ya tiene IT
    """
    if not doc.taxes:
        return False

    for tax in doc.taxes:
        if 'IT' in (tax.description or '') and 'IVA' not in (tax.description or ''):
            return True

    return False


def add_it_tax_row(doc):
    """
    Agrega una fila de IT a la tabla de impuestos

    Args:
        doc: Documento de factura
    """
    # Obtener cuenta de IT
    it_account = get_it_account(doc.company)

    if not it_account:
        frappe.msgprint(_('Cuenta de IT no configurada para esta empresa'))
        return

    # El IT se calcula sobre el gran total (incluyendo IVA)
    doc.append('taxes', {
        'charge_type': 'On Previous Row Total',
        'account_head': it_account,
        'description': f'IT {IT_RATE}%',
        'rate': IT_RATE,
        'row_id': len(doc.taxes) if doc.taxes else 1,
        'included_in_print_rate': 0
    })

    # Recalcular totales
    doc.calculate_taxes_and_totals()


def get_it_account(company):
    """
    Obtiene la cuenta de IT para una empresa

    Args:
        company (str): Nombre de la empresa

    Returns:
        str: Nombre completo de la cuenta o None
    """
    abbr = frappe.get_cached_value('Company', company, 'abbr')

    # Cuenta IT por Pagar (2122)
    account = frappe.db.get_value('Plan Cuentas Bolivia',
                                  {'account_number': '2122', 'company': company},
                                  'account_name')

    if account:
        return f"{account} - {abbr}"

    # Buscar directamente en Account
    account = frappe.db.get_value('Account',
                                  {'account_name': 'IT por Pagar', 'company': company},
                                  'name')

    return account


def create_it_journal_entry(payment_entry, it_amount):
    """
    Crea un asiento contable para el IT de un pago

    Args:
        payment_entry: Payment Entry document
        it_amount (float): Monto del IT
    """
    # TODO: Implementar creación de Journal Entry para IT
    # Se crea cuando el IT no está incluido en la factura
    pass


def calculate_it_for_period(company, from_date, to_date):
    """
    Calcula el IT total para un periodo

    Args:
        company (str): Empresa
        from_date (str): Fecha inicio
        to_date (str): Fecha fin

    Returns:
        dict: Total IT del periodo
    """
    # IT de ventas
    it_sales = frappe.db.sql("""
        SELECT SUM(ti.tax_amount)
        FROM `tabSales Invoice` si
        INNER JOIN `tabSales Taxes and Charges` ti ON ti.parent = si.name
        WHERE si.company = %s
        AND si.docstatus = 1
        AND si.posting_date BETWEEN %s AND %s
        AND ti.description LIKE %s
        AND ti.description NOT LIKE %s
    """, (company, from_date, to_date, '%IT%', '%IVA%'))[0][0] or 0

    # IT de compras (si aplica)
    it_purchases = frappe.db.sql("""
        SELECT SUM(ti.tax_amount)
        FROM `tabPurchase Invoice` pi
        INNER JOIN `tabPurchase Taxes and Charges` ti ON ti.parent = pi.name
        WHERE pi.company = %s
        AND pi.docstatus = 1
        AND pi.posting_date BETWEEN %s AND %s
        AND ti.description LIKE %s
        AND ti.description NOT LIKE %s
    """, (company, from_date, to_date, '%IT%', '%IVA%'))[0][0] or 0

    total_it = it_sales + it_purchases

    return {
        'it_sales': round(it_sales, 2),
        'it_purchases': round(it_purchases, 2),
        'total_it': round(total_it, 2),
        'rate': IT_RATE
    }


def is_it_compensable_with_iue(company, fiscal_year):
    """
    Verifica si el IT pagado es compensable con IUE

    Según normativa boliviana, el IT pagado durante el año
    puede compensarse con el IUE (Impuesto sobre Utilidades)

    Args:
        company (str): Empresa
        fiscal_year (str): Año fiscal

    Returns:
        dict: Información de compensación
    """
    # Obtener inicio y fin del año fiscal
    from_date, to_date = frappe.db.get_value('Fiscal Year', fiscal_year, ['year_start_date', 'year_end_date'])

    # Total IT pagado
    it_data = calculate_it_for_period(company, from_date, to_date)
    total_it = it_data['total_it']

    # TODO: Calcular IUE del periodo
    # total_iue = calculate_iue_for_period(company, from_date, to_date)

    return {
        'total_it_paid': total_it,
        'is_compensable': True,
        'compensation_rate': 1.0  # 100% compensable
    }


@frappe.whitelist()
def get_it_report(company, from_date, to_date):
    """
    API para obtener reporte de IT

    Args:
        company (str): Empresa
        from_date (str): Fecha inicio
        to_date (str): Fecha fin

    Returns:
        dict: Reporte de IT
    """
    return calculate_it_for_period(company, from_date, to_date)
