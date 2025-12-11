# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

"""PDF Exporter"""

import frappe
from frappe.utils import now
import logging

logger = logging.getLogger(__name__)


@frappe.whitelist(methods=['POST'])
def export_to_pdf(columns, data, report_name):
    """
    Exporta datos a PDF

    Note: Esta es una implementación simplificada.
    Para mayor funcionalidad, se puede usar weasyprint o reportlab
    """
    try:
        # Crear HTML tabla
        html_content = _create_html_table(columns, data, report_name)

        # Convertir HTML a PDF usando Frappe's built-in method
        timestamp = now().replace(' ', '_').replace(':', '-')
        filename = f"{report_name}_{timestamp}.pdf"
        file_path = f"/tmp/{filename}"

        # Usar frappe.get_print para generar PDF
        # Alternativamente, usar una librería como weasyprint
        try:
            from weasyprint import HTML
            HTML(string=html_content).write_pdf(file_path)

            return {
                'success': True,
                'file_path': file_path,
                'file_name': filename
            }
        except ImportError:
            logger.warning("weasyprint not installed, returning HTML instead")
            # Fallback a HTML
            html_path = file_path.replace('.pdf', '.html')
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            return {
                'success': True,
                'file_path': html_path,
                'file_name': html_path.split('/')[-1],
                'warning': 'PDF library not installed, exported as HTML'
            }

    except Exception as e:
        logger.error(f"Error exporting to PDF: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


def _create_html_table(columns, data, report_name):
    """Crea tabla HTML desde datos"""
    html = f"""
    <html>
        <head>
            <meta charset="UTF-8">
            <title>{report_name}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; }}
                .timestamp {{ color: #666; font-size: 12px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th {{
                    background-color: #4472C4;
                    color: white;
                    padding: 10px;
                    text-align: left;
                    font-weight: bold;
                    border: 1px solid #333;
                }}
                td {{
                    padding: 8px;
                    border: 1px solid #ddd;
                    text-align: left;
                }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
                tr:hover {{ background-color: #f0f0f0; }}
            </style>
        </head>
        <body>
            <h1>{report_name}</h1>
            <p class="timestamp">Generated: {now()}</p>
            <table>
                <thead>
                    <tr>
    """

    # Agregar headers
    for column in columns:
        label = column.get('label', column.get('fieldname', 'Column'))
        html += f"<th>{label}</th>"

    html += """
                    </tr>
                </thead>
                <tbody>
    """

    # Agregar datos
    for row in data:
        html += "<tr>"
        for column in columns:
            fieldname = column.get('fieldname', '')
            value = row.get(fieldname, '')
            html += f"<td>{value}</td>"
        html += "</tr>"

    html += """
                </tbody>
            </table>
        </body>
    </html>
    """

    return html
