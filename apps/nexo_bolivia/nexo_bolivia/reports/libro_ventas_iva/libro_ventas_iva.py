# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

"""
Libro de Ventas IVA - Reporte Oficial SIN

Registro detallado de todas las ventas con IVA del período según
Resolución Normativa 10-0001-07 del SIN.

Columnas:
1. Nro - Número correlativo
2. Fecha de Factura
3. Nro de Factura
4. Nro de Autorización (CUF para electrónicas)
5. Estado - Válida, Anulada
6. NIT/CI del Cliente
7. Nombre/Razón Social del Cliente
8. Monto Total Venta
9. Importe ICE (si aplica)
10. Importe Exentas
11. Importe Gravadas (Base imponible)
12. Débito Fiscal (IVA 13%)
13. Código de Control
"""

import frappe
from frappe import _
from datetime import datetime
from typing import Dict, List, Any


def execute(filters=None):
    """
    Genera reporte de ventas IVA

    Args:
        filters: {
            'company': str,
            'from_date': str,
            'to_date': str,
            'customer': str (opcional)
        }

    Returns:
        tuple: (columns, data)
    """
    if not filters:
        filters = {}

    # Validar filtros requeridos
    if not filters.get('company'):
        frappe.throw(_('Empresa es requerida'))

    if not filters.get('from_date') or not filters.get('to_date'):
        frappe.throw(_('Fechas son requeridas'))

    # Obtener columnas
    columns = get_columns()

    # Obtener datos
    data = get_sales_invoices(filters)

    # Validar y calcular datos
    data = calculate_totals(data)

    return columns, data


def get_columns() -> List[Dict[str, Any]]:
    """
    Retorna las columnas del reporte

    Returns:
        List[Dict]: Columnas del reporte
    """
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
            'options': 'Sales Invoice',
            'width': 120
        },
        {
            'fieldname': 'cuf',
            'label': _('CUF/Autorización'),
            'fieldtype': 'Data',
            'width': 150
        },
        {
            'fieldname': 'status',
            'label': _('Estado'),
            'fieldtype': 'Data',
            'width': 90
        },
        {
            'fieldname': 'customer_nit',
            'label': _('NIT/CI Cliente'),
            'fieldtype': 'Data',
            'width': 120
        },
        {
            'fieldname': 'customer_name',
            'label': _('Cliente'),
            'fieldtype': 'Data',
            'width': 200
        },
        {
            'fieldname': 'total_amount',
            'label': _('Total Venta'),
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
            'fieldname': 'exempt_amount',
            'label': _('Exentas'),
            'fieldtype': 'Currency',
            'width': 100
        },
        {
            'fieldname': 'taxable_amount',
            'label': _('Gravadas'),
            'fieldtype': 'Currency',
            'width': 100
        },
        {
            'fieldname': 'iva_amount',
            'label': _('Débito Fiscal'),
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


def get_sales_invoices(filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Obtiene facturas de venta del período

    Args:
        filters: Filtros del reporte

    Returns:
        List[Dict]: Datos de facturas
    """
    conditions = [
        'docstatus IN (0, 1)',  # Incluir borradores y publicadas
        'company = %s',
        'posting_date BETWEEN %s AND %s'
    ]

    params = [
        filters.get('company'),
        filters.get('from_date'),
        filters.get('to_date')
    ]

    # Filtro opcional de cliente
    if filters.get('customer'):
        conditions.append('customer = %s')
        params.append(filters.get('customer'))

    where_clause = ' AND '.join(conditions)

    # Obtener facturas
    invoices = frappe.db.sql(f"""
        SELECT
            name,
            posting_date,
            customer_name,
            customer,
            grand_total,
            docstatus,
            status
        FROM `tabSales Invoice`
        WHERE {where_clause}
        ORDER BY posting_date, name
    """, params, as_dict=True)

    # Procesar cada factura
    data = []
    nro = 1

    for invoice_doc in invoices:
        invoice = frappe.get_doc('Sales Invoice', invoice_doc.name)

        # Obtener datos de cliente
        customer_nit = frappe.db.get_value('Customer', invoice.customer, 'nit_ci') or ''

        # Obtener CUF y código de control (si es factura electrónica)
        cuf = invoice.get('cuf') or ''
        control_code = invoice.get('control_code') or ''

        # Calcular montos por tipo
        taxable_amount = 0
        iva_amount = 0
        exempt_amount = 0
        ice_amount = 0

        # Procesar items
        for item in invoice.items:
            taxable_amount += item.net_amount

        # Procesar impuestos
        for tax in invoice.taxes:
            if 'IVA' in (tax.description or ''):
                iva_amount += tax.tax_amount
            elif 'ICE' in (tax.description or ''):
                ice_amount += tax.tax_amount

        # Determinar estado
        if invoice_doc.docstatus == 0:
            status = 'Borrador'
        elif invoice.get('is_cancelled'):
            status = 'Anulada'
        else:
            status = 'Válida'

        data.append({
            'nro': nro,
            'posting_date': invoice_doc.posting_date,
            'name': invoice_doc.name,
            'cuf': cuf,
            'status': status,
            'customer_nit': customer_nit,
            'customer_name': invoice_doc.customer_name,
            'total_amount': invoice.grand_total,
            'ice_amount': ice_amount,
            'exempt_amount': exempt_amount,
            'taxable_amount': taxable_amount,
            'iva_amount': iva_amount,
            'control_code': control_code
        })

        nro += 1

    return data


def calculate_totals(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Calcula totales del reporte

    Args:
        data: Datos del reporte

    Returns:
        List[Dict]: Datos con totales
    """
    if not data:
        return data

    # Calcular totales
    totals = {
        'nro': '',
        'posting_date': '',
        'name': 'TOTAL',
        'cuf': '',
        'status': '',
        'customer_nit': '',
        'customer_name': 'TOTAL DEL PERÍODO',
        'total_amount': sum(row.get('total_amount', 0) for row in data),
        'ice_amount': sum(row.get('ice_amount', 0) for row in data),
        'exempt_amount': sum(row.get('exempt_amount', 0) for row in data),
        'taxable_amount': sum(row.get('taxable_amount', 0) for row in data),
        'iva_amount': sum(row.get('iva_amount', 0) for row in data),
        'control_code': ''
    }

    # Agregar totales al final
    data.append(totals)

    return data


@frappe.whitelist()
def export_to_excel(filters):
    """
    Exporta libro de ventas a Excel formato oficial SIN

    Args:
        filters: Filtros del reporte

    Returns:
        str: Ruta del archivo exportado
    """
    from nexo_bolivia.reports.exporters.excel_exporter import export_libro_ventas_to_excel

    if isinstance(filters, str):
        import json
        filters = json.loads(filters)

    columns, data = execute(filters)
    return export_libro_ventas_to_excel(data, columns, filters)


@frappe.whitelist()
def export_to_txt(filters):
    """
    Exporta libro de ventas a TXT formato da Vinci

    Args:
        filters: Filtros del reporte

    Returns:
        str: Ruta del archivo exportado
    """
    from nexo_bolivia.reports.exporters.txt_exporter import export_to_davinci_txt

    if isinstance(filters, str):
        import json
        filters = json.loads(filters)

    columns, data = execute(filters)
    return export_to_davinci_txt(data, columns, 'libro_ventas')


def validate_data(data: List[Dict[str, Any]]) -> bool:
    """
    Valida integridad del reporte

    Args:
        data: Datos del reporte

    Returns:
        bool: True si es válido
    """
    if not data:
        return True

    for row in data:
        # Validar que el cliente tenga NIT
        if row.get('status') == 'Válida' and not row.get('customer_nit'):
            frappe.msgprint(
                _('Factura {} no tiene NIT del cliente').format(row.get('name')),
                title=_('Validación - Falta NIT'),
                indicator='red'
            )

        # Validar débito fiscal
        if row.get('status') == 'Válida':
            expected_iva = round(row.get('taxable_amount', 0) * 0.13, 2)
            actual_iva = row.get('iva_amount', 0)

            if abs(expected_iva - actual_iva) > 0.01:
                frappe.msgprint(
                    _('Factura {}: IVA calculado ({}) no coincide con esperado ({})').format(
                        row.get('name'), actual_iva, expected_iva
                    ),
                    title=_('Validación - IVA'),
                    indicator='yellow'
                )

    return True
