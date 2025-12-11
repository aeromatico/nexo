# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

"""CSV Exporter"""

import frappe
import csv
from io import StringIO
from frappe.utils import now
import logging

logger = logging.getLogger(__name__)


@frappe.whitelist(methods=['POST'])
def export_to_csv(columns, data, report_name):
    """Exporta datos a CSV"""
    try:
        output = StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=[c.get('fieldname', c.get('label')) for c in columns]
        )

        # Escribir headers
        writer.writeheader()

        # Escribir datos
        for row in data:
            filtered_row = {c.get('fieldname', c.get('label')): row.get(c.get('fieldname', c.get('label')), '') for c in columns}
            writer.writerow(filtered_row)

        # Guardar archivo
        timestamp = now().replace(' ', '_').replace(':', '-')
        filename = f"{report_name}_{timestamp}.csv"
        file_path = f"/tmp/{filename}"

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(output.getvalue())

        return {
            'success': True,
            'file_path': file_path,
            'file_name': filename
        }

    except Exception as e:
        logger.error(f"Error exporting to CSV: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }
