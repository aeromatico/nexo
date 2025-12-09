# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

"""
Exportador TXT - Formato da Vinci

Exporta reportes a formato TXT delimitado por pipes (|)
según especificaciones de importación en sistema da Vinci del SIN.
"""

import frappe
from frappe import _
from typing import List, Dict, Any
import os
from datetime import datetime


def export_to_davinci_txt(data: List[Dict], columns: List[Dict], report_type: str) -> str:
    """
    Exporta a formato TXT da Vinci

    Formato: Delimitado por pipes (|)
    Encoding: UTF-8 sin BOM

    Args:
        data: Datos del reporte
        columns: Definición de columnas
        report_type: Tipo de reporte (libro_ventas, libro_compras, etc)

    Returns:
        str: Ruta del archivo exportado
    """
    try:
        # Crear contenido
        lines = []

        # Encabezado
        header = '|'.join([col.get('label', '') for col in columns])
        lines.append(header)

        # Datos
        for row_data in data:
            row_values = []
            for column in columns:
                field_name = column.get('fieldname')
                value = row_data.get(field_name, '')

                # Formatear valor
                if value is None or value == '':
                    value = ''
                elif isinstance(value, float):
                    value = f'{value:.2f}'
                else:
                    value = str(value)

                # Escapar pipes en valores
                value = value.replace('|', '\\|')
                row_values.append(value)

            line = '|'.join(row_values)
            lines.append(line)

        # Guardar archivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{report_type}_davinci_{timestamp}.txt"
        filepath = os.path.join(frappe.get_site_path('private', 'files'), filename)

        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        # Escribir con encoding UTF-8 sin BOM
        with open(filepath, 'w', encoding='utf-8') as f:
            for line in lines:
                f.write(line + '\n')

        return f'/files/{filename}'

    except Exception as e:
        frappe.throw(_(f'Error al exportar a TXT: {str(e)}'))


def export_libro_ventas_davinci(data: List[Dict], filters: Dict) -> str:
    """
    Exporta Libro de Ventas a TXT da Vinci

    Args:
        data: Datos del reporte
        filters: Filtros aplicados

    Returns:
        str: Ruta del archivo exportado
    """
    # Definir columnas para da Vinci (simplificado)
    columns = [
        {'fieldname': 'nro', 'label': 'NRO'},
        {'fieldname': 'posting_date', 'label': 'FECHA'},
        {'fieldname': 'name', 'label': 'FACTURA'},
        {'fieldname': 'cuf', 'label': 'CUF'},
        {'fieldname': 'customer_nit', 'label': 'NIT_CLIENTE'},
        {'fieldname': 'customer_name', 'label': 'CLIENTE'},
        {'fieldname': 'total_amount', 'label': 'TOTAL'},
        {'fieldname': 'taxable_amount', 'label': 'BASE_GRAVADA'},
        {'fieldname': 'iva_amount', 'label': 'IVA'},
    ]

    return export_to_davinci_txt(data, columns, 'libro_ventas')


def export_libro_compras_davinci(data: List[Dict], filters: Dict) -> str:
    """
    Exporta Libro de Compras a TXT da Vinci

    Args:
        data: Datos del reporte
        filters: Filtros aplicados

    Returns:
        str: Ruta del archivo exportado
    """
    columns = [
        {'fieldname': 'nro', 'label': 'NRO'},
        {'fieldname': 'posting_date', 'label': 'FECHA'},
        {'fieldname': 'name', 'label': 'FACTURA'},
        {'fieldname': 'dui', 'label': 'DUI'},
        {'fieldname': 'supplier_nit', 'label': 'NIT_PROVEEDOR'},
        {'fieldname': 'supplier_name', 'label': 'PROVEEDOR'},
        {'fieldname': 'total_amount', 'label': 'TOTAL'},
        {'fieldname': 'credit_amount', 'label': 'CON_CREDITO'},
        {'fieldname': 'credit_fiscal', 'label': 'CREDITO_FISCAL'},
    ]

    return export_to_davinci_txt(data, columns, 'libro_compras')


def export_form_200_davinci(form_200_data: Dict) -> str:
    """
    Exporta Form 200 a TXT da Vinci

    Args:
        form_200_data: Datos del formulario

    Returns:
        str: Ruta del archivo exportado
    """
    try:
        lines = []

        # Encabezado
        lines.append('FORM|200|DECLARACION_JURADA_IVA')
        lines.append(f"EMPRESA|{form_200_data.get('company', '')}")
        lines.append(f"PERIODO|{form_200_data.get('period', '')}")

        # Sección I - Ventas
        lines.append('SECCION|I|VENTAS')
        sales = form_200_data.get('i_sales', {})
        lines.append(f"TOTAL_DEBITO_FISCAL|{sales.get('total_debit_fiscal', 0):.2f}")

        # Sección II - Compras
        lines.append('SECCION|II|COMPRAS')
        purchases = form_200_data.get('ii_purchases', {})
        lines.append(f"TOTAL_CREDITO_FISCAL|{purchases.get('total_credit_fiscal', 0):.2f}")

        # Sección III - Determinación
        lines.append('SECCION|III|DETERMINACION')
        determination = form_200_data.get('iii_determination', {})
        lines.append(f"BALANCE|{determination.get('balance', 0):.2f}")
        lines.append(f"TOTAL_A_PAGAR|{determination.get('total_to_pay', 0):.2f}")

        # Guardar archivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"form_200_davinci_{timestamp}.txt"
        filepath = os.path.join(frappe.get_site_path('private', 'files'), filename)

        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            for line in lines:
                f.write(line + '\n')

        return f'/files/{filename}'

    except Exception as e:
        frappe.throw(_(f'Error al exportar Form 200 a TXT: {str(e)}'))
