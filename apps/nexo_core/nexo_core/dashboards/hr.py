# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

"""HR Dashboard"""

import frappe
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@frappe.whitelist(methods=['GET'])
def get_hr_dashboard(company=None, period='This Month'):
    """Dashboard RRHH completo"""
    try:
        if not company:
            company = frappe.defaults.get_user_default('company')

        # Total empleados
        active_employees = frappe.db.count(
            'Employee',
            {'company': company, 'status': 'Active'}
        )

        inactive_employees = frappe.db.count(
            'Employee',
            {'company': company, 'status': 'Left'}
        )

        # Costo total nómina del mes
        date_range = _get_period_dates(period)
        total_payroll = frappe.db.get_value(
            'Salary Slip',
            {
                'company': company,
                'docstatus': 1,
                'posting_date': ['>=', date_range['start']],
                'posting_date': ['<=', date_range['end']]
            },
            'SUM(gross_pay)'
        )
        total_payroll = total_payroll[0] if total_payroll else 0

        # Promedio salarial
        avg_salary = total_payroll / active_employees if active_employees > 0 else 0

        # Ausencias del mes
        absences = frappe.db.count(
            'Attendance',
            {
                'company': company,
                'status': 'Absent',
                'attendance_date': ['>=', date_range['start']],
                'attendance_date': ['<=', date_range['end']]
            }
        )

        # Próximos cumpleaños
        today = datetime.now()
        next_30_days = today + timedelta(days=30)

        birthdays = frappe.get_all(
            'Employee',
            filters={'company': company, 'status': 'Active'},
            fields=['name', 'employee_name', 'date_of_birth'],
            limit_page_length=10
        )

        return {
            'success': True,
            'dashboard': {
                'active_employees': active_employees,
                'inactive_employees': inactive_employees,
                'total_employees': active_employees + inactive_employees,
                'total_payroll': float(total_payroll or 0),
                'average_salary': float(avg_salary or 0),
                'absences': absences,
                'absence_rate': round((absences / (active_employees * 20) * 100) if (active_employees * 20) > 0 else 0, 2),
                'period': period,
                'generated_at': frappe.utils.now()
            }
        }

    except Exception as e:
        logger.error(f"Error generating HR dashboard: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'dashboard': {}
        }


def _get_period_dates(period):
    """Obtiene rango de fechas para un período"""
    today = datetime.now().date()

    if period == 'This Month':
        start = today.replace(day=1)
        if today.month == 12:
            end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        return {'start': start, 'end': end}

    else:
        return {'start': today.replace(day=1), 'end': today}
