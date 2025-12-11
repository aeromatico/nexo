# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

"""Visual Query Builder without writing SQL"""

import frappe
import json
import logging

logger = logging.getLogger(__name__)


@frappe.whitelist(methods=['POST'])
def build_query(config):
    """
    Construye query SQL desde configuración visual

    config = {
        'doctype': 'Sales Invoice',
        'fields': ['name', 'customer', 'grand_total', 'posting_date'],
        'filters': [
            {'field': 'posting_date', 'operator': '>', 'value': '2024-01-01'},
            {'field': 'grand_total', 'operator': '>=', 'value': 1000}
        ],
        'group_by': 'customer',
        'order_by': 'grand_total DESC',
        'limit': 100
    }
    """
    try:
        doctype = config.get('doctype')
        fields = config.get('fields', ['*'])
        filters = config.get('filters', [])
        group_by = config.get('group_by')
        order_by = config.get('order_by')
        limit = config.get('limit')

        if not doctype:
            return {
                'success': False,
                'error': 'DocType is required'
            }

        # Construir query
        fields_str = ', '.join([f'`{f}`' if f != '*' else '*' for f in fields])
        query = f"SELECT {fields_str} FROM `tab{doctype}`"

        # WHERE clause
        if filters:
            where_clauses = []
            for f in filters:
                field = f.get('field')
                operator = f.get('operator', '=')
                value = f.get('value')

                if operator == 'LIKE':
                    clause = f"`{field}` LIKE '%{value}%'"
                elif operator in ['>', '<', '>=', '<=', '=', '!=']:
                    clause = f"`{field}` {operator} '{value}'"
                elif operator == 'IN':
                    clause = f"`{field}` IN ({','.join([f\"'{v}\"' for v in value])})"
                else:
                    clause = f"`{field}` = '{value}'"

                where_clauses.append(clause)

            query += " WHERE " + " AND ".join(where_clauses)

        # GROUP BY
        if group_by:
            query += f" GROUP BY `{group_by}`"

        # ORDER BY
        if order_by:
            query += f" ORDER BY {order_by}"

        # LIMIT
        if limit:
            query += f" LIMIT {limit}"

        return {
            'success': True,
            'query': query,
            'config': config
        }

    except Exception as e:
        logger.error(f"Error building query: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


@frappe.whitelist(methods=['POST'])
def preview_query_results(config, limit=10):
    """
    Preview de resultados de query

    Args:
        config (dict): Configuración de la query
        limit (int): Número máximo de registros a mostrar

    Returns:
        dict: Preview de resultados
    """
    try:
        # Construir query
        build_result = build_query(config)

        if not build_result.get('success'):
            return build_result

        query = build_result.get('query')

        # Aplicar limit para preview
        if 'LIMIT' not in query:
            query += f" LIMIT {limit}"

        # Ejecutar query
        data = frappe.db.sql(query, as_dict=True)

        # Auto-detectar columnas
        columns = []
        if data:
            for key in data[0].keys():
                columns.append({
                    'fieldname': key,
                    'label': key.replace('_', ' ').title()
                })

        return {
            'success': True,
            'columns': columns,
            'data': data,
            'row_count': len(data),
            'query': query
        }

    except Exception as e:
        logger.error(f"Error previewing query results: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'columns': [],
            'data': []
        }


@frappe.whitelist(methods=['GET'])
def get_doctype_fields(doctype):
    """Obtiene campos disponibles de un DocType"""
    try:
        meta = frappe.get_meta(doctype)
        fields = []

        for field in meta.fields:
            fields.append({
                'fieldname': field.fieldname,
                'label': field.label,
                'fieldtype': field.fieldtype
            })

        return {
            'success': True,
            'fields': fields,
            'doctype': doctype
        }

    except Exception as e:
        logger.error(f"Error getting doctype fields: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'fields': []
        }


@frappe.whitelist(methods=['GET'])
def list_doctypes():
    """Lista todos los DocTypes disponibles"""
    try:
        doctypes = frappe.get_all(
            'DocType',
            filters={'disabled': 0},
            fields=['name', 'module'],
            order_by='name ASC'
        )

        return {
            'success': True,
            'doctypes': doctypes,
            'count': len(doctypes)
        }

    except Exception as e:
        logger.error(f"Error listing doctypes: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'doctypes': []
        }
