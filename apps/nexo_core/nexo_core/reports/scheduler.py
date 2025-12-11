# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

"""Report Scheduler - Scheduled report execution"""

import frappe
from datetime import datetime, timedelta
from frappe.utils import now
import logging

logger = logging.getLogger(__name__)


def execute_scheduled_reports():
    """
    Ejecuta reportes programados (llamado por scheduler daily)
    Verifica qué reportes deben ejecutarse y los distribuye por email
    """
    try:
        current_time = now()

        # Obtener reportes que deben ejecutarse
        schedules = frappe.get_all(
            'Report Schedule',
            filters={
                'enabled': 1,
                'next_run': ['<=', current_time]
            }
        )

        for schedule_record in schedules:
            schedule_doc = frappe.get_doc('Report Schedule', schedule_record['name'])

            try:
                _execute_and_distribute_report(schedule_doc)

                # Calcular próxima ejecución
                schedule_doc.last_run = current_time
                schedule_doc.next_run = _calculate_next_run(schedule_doc)
                schedule_doc.save()

                logger.info(f"Report {schedule_doc.report} executed successfully")

            except Exception as e:
                logger.error(f"Error executing scheduled report {schedule_doc.name}: {str(e)}")

    except Exception as e:
        logger.error(f"Error in execute_scheduled_reports: {str(e)}")


def _execute_and_distribute_report(schedule_doc):
    """Ejecuta reporte y lo distribuye por email"""
    try:
        from .report_builder import execute_custom_report
        from .exporters import excel as excel_exporter

        # Obtener el reporte
        report_name = schedule_doc.report

        # Ejecutar reporte
        result = execute_custom_report(report_name)

        if not result.get('success'):
            logger.error(f"Report {report_name} execution failed: {result.get('error')}")
            return

        # Exportar al formato solicitado
        format_type = schedule_doc.format or 'Excel'

        if format_type == 'Excel':
            file_path = excel_exporter.export_to_excel(
                result.get('columns', []),
                result.get('data', []),
                report_name
            )
        elif format_type == 'PDF':
            file_path = None  # Implementar PDF export
        else:
            file_path = None

        # Enviar por email
        if file_path and schedule_doc.recipients:
            _send_report_email(
                schedule_doc.recipients.split(','),
                report_name,
                file_path
            )

    except Exception as e:
        logger.error(f"Error in _execute_and_distribute_report: {str(e)}")


def _calculate_next_run(schedule_doc):
    """Calcula próxima fecha de ejecución"""
    from datetime import datetime, timedelta

    current = datetime.now()

    if schedule_doc.frequency == 'Daily':
        return current + timedelta(days=1)

    elif schedule_doc.frequency == 'Weekly':
        day_of_week_map = {
            'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3,
            'Friday': 4, 'Saturday': 5, 'Sunday': 6
        }
        target_weekday = day_of_week_map.get(schedule_doc.day_of_week, 0)
        days_ahead = target_weekday - current.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        return current + timedelta(days=days_ahead)

    elif schedule_doc.frequency == 'Monthly':
        day = schedule_doc.day_of_month or 1
        if current.month == 12:
            return datetime(current.year + 1, 1, day)
        else:
            return datetime(current.year, current.month + 1, day)

    elif schedule_doc.frequency == 'Quarterly':
        quarter_months = {0: [1, 4, 7, 10], 1: [4, 7, 10, 1], 2: [7, 10, 1, 4], 3: [10, 1, 4, 7]}
        current_quarter = (current.month - 1) // 3
        next_month = quarter_months[current_quarter][1]
        return datetime(current.year, next_month, schedule_doc.day_of_month or 1)

    elif schedule_doc.frequency == 'Yearly':
        return datetime(current.year + 1, current.month, schedule_doc.day_of_month or 1)

    return current + timedelta(days=1)


def _send_report_email(recipients, report_name, file_path):
    """Envía reporte por email"""
    try:
        email_list = [r.strip() for r in recipients]

        subject = f"Scheduled Report: {report_name}"
        message = f"Attached is your scheduled report: {report_name}"

        frappe.sendmail(
            recipients=email_list,
            subject=subject,
            message=message,
            attachments=[file_path] if file_path else None
        )

        logger.info(f"Report {report_name} sent to {email_list}")

    except Exception as e:
        logger.error(f"Error sending report email: {str(e)}")
