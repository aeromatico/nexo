# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

"""Excel Exporter with professional formatting"""

import frappe
from frappe.utils import now
from io import BytesIO
import logging

logger = logging.getLogger(__name__)


@frappe.whitelist(methods=['POST'])
def export_to_excel(columns, data, report_name):
    """
    Exporta datos a Excel con formato profesional

    Args:
        columns (list): Definición de columnas
        data (list): Datos a exportar
        report_name (str): Nombre del reporte

    Returns:
        str: Ruta del archivo creado
    """
    try:
        try:
            import openpyxl
            from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        except ImportError:
            return {
                'success': False,
                'error': 'openpyxl library not installed'
            }

        # Crear workbook
        workbook = openpyxl.Workbook()
        worksheet = workbook.active
        worksheet.title = 'Report Data'

        # Estilos
        header_font = Font(bold=True, color='FFFFFF')
        header_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
        header_alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

        # Escribir headers
        for col_num, column in enumerate(columns, 1):
            cell = worksheet.cell(row=1, column=col_num)
            cell.value = column.get('label', column.get('fieldname', 'Column'))
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment

        # Escribir datos
        for row_num, row in enumerate(data, 2):
            for col_num, column in enumerate(columns, 1):
                cell = worksheet.cell(row=row_num, column=col_num)
                value = row.get(column.get('fieldname', ''), '')
                cell.value = value

                # Aplicar alineación según tipo
                fieldtype = column.get('fieldtype', 'Data')
                if fieldtype in ['Currency', 'Float', 'Integer']:
                    cell.alignment = Alignment(horizontal='right')
                else:
                    cell.alignment = Alignment(horizontal='left')

        # Auto-ajustar ancho de columnas
        for col_num, column in enumerate(columns, 1):
            max_length = len(str(column.get('label', '')))

            for row in data:
                value = row.get(column.get('fieldname', ''), '')
                max_length = max(max_length, len(str(value)))

            worksheet.column_dimensions[openpyxl.utils.get_column_letter(col_num)].width = min(max_length + 2, 50)

        # Guardar archivo
        timestamp = now().replace(' ', '_').replace(':', '-')
        filename = f"{report_name}_{timestamp}.xlsx"
        file_path = f"/tmp/{filename}"

        with open(file_path, 'wb') as f:
            workbook.save(f)

        # Guardar en Frappe File
        file_doc = frappe.get_doc({
            'doctype': 'File',
            'file_name': filename,
            'file_path': file_path,
            'attached_to_doctype': 'Custom Report',
            'attached_to_name': report_name,
            'is_private': 1
        })
        file_doc.insert(ignore_permissions=True)

        return {
            'success': True,
            'file_path': file_path,
            'file_name': filename,
            'file_url': file_doc.file_url
        }

    except Exception as e:
        logger.error(f"Error exporting to Excel: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }
