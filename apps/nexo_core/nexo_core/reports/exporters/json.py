# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

"""JSON Exporter"""

import frappe
import json
from frappe.utils import now
import logging

logger = logging.getLogger(__name__)


@frappe.whitelist(methods=['POST'])
def export_to_json(columns, data, report_name):
    """Exporta datos a JSON"""
    try:
        # Crear estructura JSON
        output = {
            'metadata': {
                'report_name': report_name,
                'generated_at': now(),
                'row_count': len(data)
            },
            'columns': columns,
            'data': data
        }

        # Guardar archivo
        timestamp = now().replace(' ', '_').replace(':', '-')
        filename = f"{report_name}_{timestamp}.json"
        file_path = f"/tmp/{filename}"

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, default=str)

        return {
            'success': True,
            'file_path': file_path,
            'file_name': filename,
            'size_bytes': len(json.dumps(output))
        }

    except Exception as e:
        logger.error(f"Error exporting to JSON: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }
