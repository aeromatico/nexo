# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

"""Report Distribution via Email and other channels"""

import frappe
import logging

logger = logging.getLogger(__name__)


@frappe.whitelist(methods=['POST'])
def send_report_email(recipients, report_name, file_path, subject=None, message=None):
    """
    Envía reporte por email

    Args:
        recipients (list or str): Email addresses
        report_name (str): Nombre del reporte
        file_path (str): Ruta del archivo adjunto
        subject (str): Asunto personalizado
        message (str): Mensaje personalizado

    Returns:
        dict: Resultado del envío
    """
    try:
        # Convertir string a lista si es necesario
        if isinstance(recipients, str):
            email_list = [r.strip() for r in recipients.split(',')]
        else:
            email_list = recipients

        # Validar emails
        email_list = [e for e in email_list if '@' in e]

        if not email_list:
            return {
                'success': False,
                'error': 'No valid email addresses provided'
            }

        # Usar valores por defecto si no se proporcionan
        if not subject:
            subject = f"Report: {report_name}"

        if not message:
            message = f"Please find attached the report: {report_name}"

        # Enviar email
        frappe.sendmail(
            recipients=email_list,
            subject=subject,
            message=message,
            attachments=[file_path] if file_path else None
        )

        return {
            'success': True,
            'recipients': email_list,
            'message': f'Report sent to {len(email_list)} recipients'
        }

    except Exception as e:
        logger.error(f"Error sending report email: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


@frappe.whitelist(methods=['POST'])
def schedule_report_distribution(report_name, recipients, frequency='Daily', format_type='Excel'):
    """
    Crea programación de distribución de reporte

    Args:
        report_name (str): Nombre del reporte
        recipients (str): Emails separados por coma
        frequency (str): Frecuencia (Daily, Weekly, Monthly)
        format_type (str): Formato (Excel, PDF, CSV)

    Returns:
        dict: Resultado de programación
    """
    try:
        doc = frappe.get_doc({
            'doctype': 'Report Schedule',
            'report': report_name,
            'recipients': recipients,
            'frequency': frequency,
            'format': format_type,
            'enabled': 1
        })
        doc.insert()
        frappe.db.commit()

        return {
            'success': True,
            'schedule_name': doc.name,
            'message': f'Report distribution scheduled successfully'
        }

    except Exception as e:
        logger.error(f"Error scheduling report distribution: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


@frappe.whitelist(methods=['GET'])
def get_report_distribution_status(report_name):
    """Obtiene estado de distribución de un reporte"""
    try:
        schedules = frappe.get_all(
            'Report Schedule',
            filters={'report': report_name},
            fields=['name', 'frequency', 'enabled', 'last_run', 'next_run']
        )

        return {
            'success': True,
            'schedules': schedules,
            'count': len(schedules)
        }

    except Exception as e:
        logger.error(f"Error getting report distribution status: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'schedules': []
        }
