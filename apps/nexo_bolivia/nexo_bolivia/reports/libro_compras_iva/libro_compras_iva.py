# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

"""
Libro de Compras IVA - Reporte Oficial SIN

Registro detallado de todas las compras con IVA del período según
Resolución Normativa 10-0001-07 del SIN.

Columnas:
1. Nro - Número correlativo
2. Fecha de Factura
3. Nro de Factura
4. Nro de DUI (si aplica)
5. NIT del Proveedor
6. Nombre/Razón Social del Proveedor
7. Monto Total Compra
8. Importe ICE (si aplica)
9. Importe No Sujeto a Crédito Fiscal
10. Importes con Derecho a Crédito Fiscal
11. Crédito Fiscal (IVA 13%)
12. Código de Control
"""

import frappe
from frappe import _
from typing import Dict, List, Any


def execute(filters=None):
    """
    Genera reporte de compras IVA

    Args:
        filters: {
            'company': str,
            'from_date': str,
            'to_date': str,
            'supplier': str (opcional)
        }

    Returns:
        tuple: (columns, data)
    """
    if not filters:
        filters = {}

    if not filters.get('company'):
        frappe.throw(_('Empresa es requerida'))

    if not filters.get('from_date') or not filters.get('to_date'):
        frappe.throw(_('Fechas son requeridas'))

    columns = get_columns()
    data = get_purchase_invoices(filters)
    data = calculate_totals(data)

    return columns, data


def get_columns() -> List[Dict[str, Any]]:
    """Retorna las columnas del reporte"""
    return [
        {
            'fieldname': 'nro',
            'label': _('Nro'),
            'fieldtype': 'Int',
            'width': 60
        },
        {
            'fieldname': 'posting_date',
            'label': _('Fecha'),
            'fieldtype': 'Date',
            'width': 90
        },
        {
            'fieldname': 'name',
            'label': _('Nro Factura'),
            'fieldtype': 'Link',
            'options': 'Purchase Invoice',
            'width': 120
        },
        {
            'fieldname': 'dui',
            'label': _('DUI'),
            'fieldtype': 'Data',
            'width': 120
        },
        {
            'fieldname': 'supplier_nit',
            'label': _('NIT Proveedor'),
            'fieldtype': 'Data',
            'width': 120
        },
        {
            'fieldname': 'supplier_name',
            'label': _('Proveedor'),
            'fieldtype': 'Data',
            'width': 200
        },
        {
            'fieldname': 'total_amount',
            'label': _('Total Compra'),
            'fieldtype': 'Currency',
            'width': 120
        },
        {
            'fieldname': 'ice_amount',
            'label': _('ICE'),
            'fieldtype': 'Currency',
            'width': 100
        },
        {
            'fieldname': 'non_credit_amount',
            'label': _('Sin Crédito Fiscal'),
            'fieldtype': 'Currency',
            'width': 120
        },
        {
            'fieldname': 'credit_amount',
            'label': _('Con Crédito Fiscal'),
            'fieldtype': 'Currency',
            'width': 120
        },
        {
            'fieldname': 'credit_fiscal',
            'label': _('Crédito Fiscal'),
            'fieldtype': 'Currency',
            'width': 120
        },
        {
            'fieldname': 'control_code',
            'label': _('Código Control'),
            'fieldtype': 'Data',
            'width': 120
        }
    ]


def get_purchase_invoices(filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Obtiene facturas de compra del período"""
    conditions = [
        'docstatus IN (0, 1)',
        'company = %s',
        'posting_date BETWEEN %s AND %s'
    ]

    params = [
        filters.get('company'),
        filters.get('from_date'),
        filters.get('to_date')
    ]

    if filters.get('supplier'):
        conditions.append('supplier = %s')
        params.append(filters.get('supplier'))

    where_clause = ' AND '.join(conditions)

    invoices = frappe.db.sql(f"""
        SELECT
            name,
            posting_date,
            supplier_name,
            supplier,
            grand_total,
            docstatus,
            status
        FROM `tabPurchase Invoice`
        WHERE {where_clause}
        ORDER BY posting_date, name
    """, params, as_dict=True)

    data = []
    nro = 1

    for invoice_doc in invoices:
        invoice = frappe.get_doc('Purchase Invoice', invoice_doc.name)

        supplier_nit = frappe.db.get_value('Supplier', invoice.supplier, 'nit_ci') or ''
        dui = invoice.get('dui') or ''
        control_code = invoice.get('control_code') or ''

        credit_fiscal = 0
        credit_amount = 0
        non_credit_amount = 0
        ice_amount = 0

        # Procesar items
        for item in invoice.items:
            credit_amount += item.net_amount

        # Procesar impuestos
        for tax in invoice.taxes:
            if 'IVA' in (tax.description or ''):
                credit_fiscal += tax.tax_amount
            elif 'ICE' in (tax.description or ''):
                ice_amount += tax.tax_amount

        status = 'Anulada' if invoice.get('is_cancelled') else ('Válida' if invoice_doc.docstatus == 1 else 'Borrador')

        data.append({
            'nro': nro,
            'posting_date': invoice_doc.posting_date,
            'name': invoice_doc.name,
            'dui': dui,
            'supplier_nit': supplier_nit,
            'supplier_name': invoice_doc.supplier_name,
            'total_amount': invoice.grand_total,
            'ice_amount': ice_amount,
            'non_credit_amount': non_credit_amount,
            'credit_amount': credit_amount,
            'credit_fiscal': credit_fiscal,
            'control_code': control_code
        })

        nro += 1

    return data


def calculate_totals(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Calcula totales del reporte"""
    if not data:
        return data

    totals = {
        'nro': '',
        'posting_date': '',
        'name': 'TOTAL',
        'dui': '',
        'supplier_nit': '',
        'supplier_name': 'TOTAL DEL PERÍODO',
        'total_amount': sum(row.get('total_amount', 0) for row in data),
        'ice_amount': sum(row.get('ice_amount', 0) for row in data),
        'non_credit_amount': sum(row.get('non_credit_amount', 0) for row in data),
        'credit_amount': sum(row.get('credit_amount', 0) for row in data),
        'credit_fiscal': sum(row.get('credit_fiscal', 0) for row in data),
        'control_code': ''
    }

    data.append(totals)
    return data


@frappe.whitelist()
def export_to_excel(filters):
    """Exporta libro de compras a Excel"""
    from nexo_bolivia.reports.exporters.excel_exporter import export_libro_compras_to_excel

    if isinstance(filters, str):
        import json
        filters = json.loads(filters)

    columns, data = execute(filters)
    return export_libro_compras_to_excel(data, columns, filters)


@frappe.whitelist()
def export_to_txt(filters):
    """Exporta libro de compras a TXT"""
    from nexo_bolivia.reports.exporters.txt_exporter import export_to_davinci_txt

    if isinstance(filters, str):
        import json
        filters = json.loads(filters)

    columns, data = execute(filters)
    return export_to_davinci_txt(data, columns, 'libro_compras')


def validate_data(data: List[Dict[str, Any]]) -> bool:
    """Valida integridad del reporte"""
    if not data:
        return True

    for row in data:
        if row.get('status') == 'Válida' and not row.get('supplier_nit'):
            frappe.msgprint(
                _('Factura {} no tiene NIT del proveedor').format(row.get('name')),
                title=_('Validación - Falta NIT'),
                indicator='red'
            )

    return True
