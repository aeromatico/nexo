# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

"""
Exportador Excel - Formato Oficial SIN

Exporta reportes a formato Excel según especificaciones del SIN.
Incluye formatos oficiales, validaciones y estructura específica.
"""

import frappe
from frappe import _
from typing import List, Dict, Any
import os
from datetime import datetime


def export_libro_ventas_to_excel(data: List[Dict], columns: List[Dict], filters: Dict) -> str:
    """
    Exporta Libro de Ventas a Excel formato oficial SIN

    Args:
        data: Datos del reporte
        columns: Definición de columnas
        filters: Filtros aplicados

    Returns:
        str: Ruta del archivo exportado
    """
    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    except ImportError:
        frappe.throw(_('openpyxl library is required. Please install it.'))

    # Crear workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Libro Ventas IVA"

    # Encabezado con información de la empresa
    company_name = frappe.db.get_value('Company', filters.get('company'), 'company_name')
    company_nit = frappe.db.get_value('Company', filters.get('company'), 'nit_ci')

    ws['A1'] = 'LIBRO DE VENTAS IVA'
    ws['A1'].font = Font(bold=True, size=14)
    ws['A2'] = f'Empresa: {company_name}'
    ws['A3'] = f'NIT: {company_nit}'
    ws['A4'] = f'Período: {filters.get("from_date")} a {filters.get("to_date")}'

    # Encabezados de columnas
    header_row = 6
    for col_idx, column in enumerate(columns, 1):
        cell = ws.cell(row=header_row, column=col_idx)
        cell.value = column.get('label', '')
        cell.font = Font(bold=True, color='FFFFFF')
        cell.fill = PatternFill(start_color='366092', end_color='366092', fill_type='solid')
        cell.alignment = Alignment(horizontal='center')

    # Datos
    for row_idx, row_data in enumerate(data, header_row + 1):
        for col_idx, column in enumerate(columns, 1):
            cell = ws.cell(row=row_idx, column=col_idx)
            field_name = column.get('fieldname')
            cell.value = row_data.get(field_name)

            # Formatear según tipo
            fieldtype = column.get('fieldtype')
            if fieldtype == 'Currency':
                cell.number_format = '#,##0.00'
            elif fieldtype == 'Date':
                cell.number_format = 'dd/mm/yyyy'

            # Destacar fila de totales
            if 'TOTAL' in str(row_data.get('customer_name', '')):
                cell.font = Font(bold=True)
                cell.fill = PatternFill(start_color='E8E8E8', end_color='E8E8E8', fill_type='solid')

    # Ajustar ancho de columnas
    for col in ws.columns:
        max_length = 0
        column_letter = col[0].column_letter
        for cell in col:
            if len(str(cell.value)) > max_length:
                max_length = len(str(cell.value))
        ws.column_dimensions[column_letter].width = min(max_length + 2, 50)

    # Guardar archivo
    filename = f"Libro_Ventas_IVA_{filters.get('from_date')}_{filters.get('to_date')}.xlsx"
    filepath = os.path.join(frappe.get_site_path('private', 'files'), filename)

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    wb.save(filepath)

    # Retornar URL de descarga
    return f'/files/{filename}'


def export_libro_compras_to_excel(data: List[Dict], columns: List[Dict], filters: Dict) -> str:
    """
    Exporta Libro de Compras a Excel formato oficial SIN

    Args:
        data: Datos del reporte
        columns: Definición de columnas
        filters: Filtros aplicados

    Returns:
        str: Ruta del archivo exportado
    """
    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment
    except ImportError:
        frappe.throw(_('openpyxl library is required. Please install it.'))

    # Crear workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Libro Compras IVA"

    # Encabezado
    company_name = frappe.db.get_value('Company', filters.get('company'), 'company_name')
    company_nit = frappe.db.get_value('Company', filters.get('company'), 'nit_ci')

    ws['A1'] = 'LIBRO DE COMPRAS IVA'
    ws['A1'].font = Font(bold=True, size=14)
    ws['A2'] = f'Empresa: {company_name}'
    ws['A3'] = f'NIT: {company_nit}'
    ws['A4'] = f'Período: {filters.get("from_date")} a {filters.get("to_date")}'

    # Encabezados de columnas
    header_row = 6
    for col_idx, column in enumerate(columns, 1):
        cell = ws.cell(row=header_row, column=col_idx)
        cell.value = column.get('label', '')
        cell.font = Font(bold=True, color='FFFFFF')
        cell.fill = PatternFill(start_color='366092', end_color='366092', fill_type='solid')
        cell.alignment = Alignment(horizontal='center')

    # Datos
    for row_idx, row_data in enumerate(data, header_row + 1):
        for col_idx, column in enumerate(columns, 1):
            cell = ws.cell(row=row_idx, column=col_idx)
            field_name = column.get('fieldname')
            cell.value = row_data.get(field_name)

            # Formatear según tipo
            fieldtype = column.get('fieldtype')
            if fieldtype == 'Currency':
                cell.number_format = '#,##0.00'
            elif fieldtype == 'Date':
                cell.number_format = 'dd/mm/yyyy'

            # Destacar fila de totales
            if 'TOTAL' in str(row_data.get('supplier_name', '')):
                cell.font = Font(bold=True)
                cell.fill = PatternFill(start_color='E8E8E8', end_color='E8E8E8', fill_type='solid')

    # Ajustar ancho de columnas
    for col in ws.columns:
        max_length = 0
        column_letter = col[0].column_letter
        for cell in col:
            if len(str(cell.value)) > max_length:
                max_length = len(str(cell.value))
        ws.column_dimensions[column_letter].width = min(max_length + 2, 50)

    # Guardar archivo
    filename = f"Libro_Compras_IVA_{filters.get('from_date')}_{filters.get('to_date')}.xlsx"
    filepath = os.path.join(frappe.get_site_path('private', 'files'), filename)

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    wb.save(filepath)

    return f'/files/{filename}'


def export_form_200_to_excel(data: Dict, filters: Dict) -> str:
    """
    Exporta Form 200 a Excel

    Args:
        data: Datos del formulario
        filters: Filtros aplicados

    Returns:
        str: Ruta del archivo exportado
    """
    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment
    except ImportError:
        frappe.throw(_('openpyxl library is required. Please install it.'))

    # Crear workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Form 200"

    # Encabezado
    ws['A1'] = 'DECLARACIÓN JURADA IVA - FORM 200'
    ws['A1'].font = Font(bold=True, size=14)

    # Información general
    row = 3
    ws[f'A{row}'] = 'Empresa:'
    ws[f'B{row}'] = data.get('company')
    row += 1
    ws[f'A{row}'] = 'Período:'
    ws[f'B{row}'] = data.get('period')

    # Sección I - Ventas
    row += 2
    ws[f'A{row}'] = 'I. VENTAS'
    ws[f'A{row}'].font = Font(bold=True, size=12)
    row += 1

    sales = data.get('i_sales', {})
    ws[f'A{row}'] = 'Total Débito Fiscal (Ventas)'
    ws[f'B{row}'] = sales.get('total_debit_fiscal', 0)
    ws[f'B{row}'].number_format = '#,##0.00'

    # Sección II - Compras
    row += 2
    ws[f'A{row}'] = 'II. COMPRAS'
    ws[f'A{row}'].font = Font(bold=True, size=12)
    row += 1

    purchases = data.get('ii_purchases', {})
    ws[f'A{row}'] = 'Total Crédito Fiscal (Compras)'
    ws[f'B{row}'] = purchases.get('total_credit_fiscal', 0)
    ws[f'B{row}'].number_format = '#,##0.00'

    # Sección III - Determinación
    row += 2
    ws[f'A{row}'] = 'III. DETERMINACIÓN'
    ws[f'A{row}'].font = Font(bold=True, size=12)
    row += 1

    determination = data.get('iii_determination', {})
    ws[f'A{row}'] = 'Débito Fiscal'
    ws[f'B{row}'] = determination.get('debit_fiscal', 0)
    ws[f'B{row}'].number_format = '#,##0.00'
    row += 1

    ws[f'A{row}'] = 'Menos: Crédito Fiscal'
    ws[f'B{row}'] = determination.get('credit_fiscal', 0)
    ws[f'B{row}'].number_format = '#,##0.00'
    row += 1

    ws[f'A{row}'] = 'BALANCE'
    ws[f'A{row}'].font = Font(bold=True)
    ws[f'B{row}'] = determination.get('balance', 0)
    ws[f'B{row}'].font = Font(bold=True)
    ws[f'B{row}'].number_format = '#,##0.00'
    row += 1

    ws[f'A{row}'] = 'Total a Pagar'
    ws[f'A{row}'].font = Font(bold=True)
    ws[f'B{row}'] = determination.get('total_to_pay', 0)
    ws[f'B{row}'].font = Font(bold=True)
    ws[f'B{row}'].number_format = '#,##0.00'
    ws[f'B{row}'].fill = PatternFill(start_color='FFFF00', end_color='FFFF00', fill_type='solid')

    # Ajustar ancho
    ws.column_dimensions['A'].width = 35
    ws.column_dimensions['B'].width = 20

    # Guardar archivo
    filename = f"Form_200_{data.get('period')}.xlsx"
    filepath = os.path.join(frappe.get_site_path('private', 'files'), filename)

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    wb.save(filepath)

    return f'/files/{filename}'
