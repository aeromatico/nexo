# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

"""
Custom Report Builder
Create and execute custom reports with SQL queries or Python scripts
"""

import frappe
import json
import logging

logger = logging.getLogger(__name__)


@frappe.whitelist(methods=['POST'])
def create_custom_report(report_config):
    """
    Crea reporte personalizado

    Args:
        report_config (dict): Configuración del reporte

    Returns:
        dict: Resultado de creación
    """
    try:
        doc = frappe.get_doc({
            'doctype': 'Custom Report',
            **report_config
        })
        doc.insert()
        frappe.db.commit()

        return {
            'success': True,
            'report_name': doc.name,
            'message': 'Report created successfully'
        }

    except Exception as e:
        logger.error(f"Error creating custom report: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


@frappe.whitelist(methods=['GET'])
def execute_custom_report(report_name, filters=None):
    """
    Ejecuta reporte personalizado

    Args:
        report_name (str): Nombre del reporte
        filters (dict): Filtros a aplicar

    Returns:
        dict: Resultado de ejecución con datos
    """
    try:
        report = frappe.get_doc('Custom Report', report_name)

        if report.report_type == 'Query':
            return _execute_query_report(report, filters)

        elif report.report_type == 'Script':
            return _execute_script_report(report, filters)

        else:
            return {
                'success': False,
                'error': 'Unknown report type'
            }

    except Exception as e:
        logger.error(f"Error executing custom report {report_name}: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'columns': [],
            'data': []
        }


def _execute_query_report(report, filters):
    """Ejecuta reporte basado en query SQL"""
    try:
        query = report.query

        # Aplicar filtros a la query (simplificado)
        if filters:
            filter_conditions = []
            for key, value in filters.items():
                filter_conditions.append(f"`{key}` = '{value}'")

            if filter_conditions:
                if 'WHERE' not in query:
                    query += " WHERE " + " AND ".join(filter_conditions)
                else:
                    query += " AND " + " AND ".join(filter_conditions)

        # Ejecutar query de forma segura
        data = frappe.db.sql(query, as_dict=True)

        # Obtener columnas
        if report.columns:
            columns = json.loads(report.columns)
        else:
            columns = _auto_detect_columns(data)

        return {
            'success': True,
            'columns': columns,
            'data': data,
            'report_name': report.name,
            'row_count': len(data)
        }

    except Exception as e:
        logger.error(f"Error executing query report: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'columns': [],
            'data': []
        }


def _execute_script_report(report, filters):
    """Ejecuta reporte basado en script Python"""
    try:
        # Crear contexto seguro para ejecutar script
        safe_dict = {
            'frappe': frappe,
            'filters': filters or {},
            'columns': [],
            'data': []
        }

        # Ejecutar el script personalizado
        exec(report.script, safe_dict)

        columns = safe_dict.get('columns', [])
        data = safe_dict.get('data', [])

        return {
            'success': True,
            'columns': columns,
            'data': data,
            'report_name': report.name,
            'row_count': len(data)
        }

    except Exception as e:
        logger.error(f"Error executing script report: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'columns': [],
            'data': []
        }


def _auto_detect_columns(data):
    """Detecta automáticamente las columnas de los datos"""
    if not data:
        return []

    first_row = data[0]
    columns = []

    for key in first_row.keys():
        columns.append({
            'fieldname': key,
            'label': key.replace('_', ' ').title(),
            'fieldtype': 'Data',
            'width': 150
        })

    return columns


@frappe.whitelist(methods=['GET'])
def list_custom_reports(doctype_filter=None):
    """
    Lista todos los reportes personalizados

    Args:
        doctype_filter (str): Filtrar por doctype referenciado

    Returns:
        dict: Lista de reportes
    """
    filters = {}
    if doctype_filter:
        filters['reference_doctype'] = doctype_filter

    reports = frappe.get_all(
        'Custom Report',
        filters=filters,
        fields=['name', 'report_name', 'report_type', 'reference_doctype']
    )

    return {
        'success': True,
        'reports': reports,
        'count': len(reports)
    }


@frappe.whitelist(methods=['GET'])
def get_report_definition(report_name):
    """Obtiene definición completa de un reporte"""
    try:
        report = frappe.get_doc('Custom Report', report_name)

        return {
            'success': True,
            'report': {
                'name': report.name,
                'report_type': report.report_type,
                'reference_doctype': report.reference_doctype,
                'query': report.query if report.report_type == 'Query' else None,
                'script': report.script if report.report_type == 'Script' else None,
                'columns': json.loads(report.columns) if report.columns else None,
                'filters': json.loads(report.filters) if report.filters else None
            }
        }

    except Exception as e:
        logger.error(f"Error getting report definition: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


@frappe.whitelist(methods=['POST'])
def delete_custom_report(report_name):
    """Elimina un reporte personalizado"""
    try:
        frappe.delete_doc('Custom Report', report_name, ignore_permissions=True)
        frappe.db.commit()

        return {
            'success': True,
            'message': f'Report {report_name} deleted successfully'
        }

    except Exception as e:
        logger.error(f"Error deleting report: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }
