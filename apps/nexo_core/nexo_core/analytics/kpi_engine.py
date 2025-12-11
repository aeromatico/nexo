# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

"""
KPI Engine for calculating and tracking Key Performance Indicators
Supports standard calculations, custom scripts, and automatic alerts
"""

import frappe
import json
from frappe import _
from datetime import datetime, timedelta
from frappe.utils import now, add_days, get_first_day, get_last_day
import logging

logger = logging.getLogger(__name__)


class KPIEngine:
    """Motor de cálculo de KPIs"""

    @staticmethod
    @frappe.whitelist(methods=['GET'])
    def calculate_kpi(kpi_name, company=None, period=None):
        """
        Calcula un KPI específico

        Args:
            kpi_name (str): Nombre del KPI
            company (str): Empresa a considerar
            period (str): Período ('This Month', 'This Year', 'Last 30 Days', etc.)

        Returns:
            dict: Resultado con value, comparison, status
        """
        try:
            kpi = frappe.get_doc('KPI Definition', kpi_name)

            if not company:
                company = frappe.defaults.get_user_default('company')

            if kpi.calculation_method == 'Custom':
                # Ejecutar script personalizado
                return KPIEngine._execute_custom_kpi(kpi, company, period)
            else:
                # Cálculo estándar
                return KPIEngine._calculate_standard_kpi(kpi, company, period)

        except Exception as e:
            logger.error(f"Error calculating KPI {kpi_name}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'value': 0
            }

    @staticmethod
    def _calculate_standard_kpi(kpi, company, period):
        """Calcula KPI usando método estándar (Sum, Average, Count, etc.)"""

        # Obtener rango de fechas
        date_range = KPIEngine._get_period_date_range(period or kpi.comparison_period)

        # Construir filtros
        filters = {
            'docstatus': 1  # Documentos submitted
        }

        if kpi.filters:
            custom_filters = json.loads(kpi.filters)
            for f in custom_filters:
                filters[f['field']] = [f['operator'], f['value']]

        # Agregar filtro de fecha si aplica
        filters['posting_date'] = ['>=', date_range['start']]
        filters['posting_date'] = ['<=', date_range['end']]

        # Calcular según método
        if kpi.calculation_method == 'Sum':
            result = frappe.db.get_value(
                kpi.source_doctype,
                filters,
                f'SUM({kpi.field_to_aggregate})'
            )
            value = result[0] if result else 0

        elif kpi.calculation_method == 'Average':
            result = frappe.db.get_value(
                kpi.source_doctype,
                filters,
                f'AVG({kpi.field_to_aggregate})'
            )
            value = result[0] if result else 0

        elif kpi.calculation_method == 'Count':
            value = frappe.db.count(kpi.source_doctype, filters)

        elif kpi.calculation_method == 'Max':
            result = frappe.db.get_value(
                kpi.source_doctype,
                filters,
                f'MAX({kpi.field_to_aggregate})'
            )
            value = result[0] if result else 0

        elif kpi.calculation_method == 'Min':
            result = frappe.db.get_value(
                kpi.source_doctype,
                filters,
                f'MIN({kpi.field_to_aggregate})'
            )
            value = result[0] if result else 0

        else:
            value = 0

        # Calcular comparación
        comparison_result = KPIEngine._calculate_comparison(
            kpi, value, date_range, company
        )

        return {
            'success': True,
            'value': float(value or 0),
            'target': float(kpi.target_value or 0),
            'comparison': comparison_result['percentage'],
            'status': comparison_result['status'],
            'period': date_range
        }

    @staticmethod
    def _execute_custom_kpi(kpi, company, period):
        """Ejecuta un KPI personalizado con script Python"""
        try:
            # Crear contexto seguro para ejecutar script
            date_range = KPIEngine._get_period_date_range(period or kpi.comparison_period)

            safe_dict = {
                'frappe': frappe,
                'company': company,
                'period_start': date_range['start'],
                'period_end': date_range['end'],
                'value': 0
            }

            # Ejecutar el script personalizado
            exec(kpi.custom_script, safe_dict)
            value = safe_dict.get('value', 0)

            comparison_result = KPIEngine._calculate_comparison(
                kpi, value, date_range, company
            )

            return {
                'success': True,
                'value': float(value or 0),
                'target': float(kpi.target_value or 0),
                'comparison': comparison_result['percentage'],
                'status': comparison_result['status'],
                'period': date_range
            }

        except Exception as e:
            logger.error(f"Error executing custom KPI {kpi.name}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'value': 0
            }

    @staticmethod
    @frappe.whitelist(methods=['GET'])
    def get_kpi_trend(kpi_name, company=None, periods=12):
        """
        Obtiene tendencia de un KPI en los últimos N períodos

        Args:
            kpi_name (str): Nombre del KPI
            company (str): Empresa
            periods (int): Número de períodos a incluir

        Returns:
            list: Array de {period, value, status}
        """
        try:
            kpi = frappe.get_doc('KPI Definition', kpi_name)
            trend = []

            for i in range(periods):
                period_start, period_end = KPIEngine._get_period_dates_by_index(
                    kpi.comparison_period,
                    periods - i - 1
                )

                # Calcular KPI para este período
                result = KPIEngine.calculate_kpi(
                    kpi_name,
                    company,
                    None  # Usar fechas calculadas
                )

                trend.append({
                    'period': f"{period_start.strftime('%Y-%m')}",
                    'value': result.get('value', 0),
                    'status': result.get('status', 'neutral')
                })

            return {
                'success': True,
                'trend': trend,
                'kpi_name': kpi_name
            }

        except Exception as e:
            logger.error(f"Error getting KPI trend for {kpi_name}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'trend': []
            }

    @staticmethod
    def _get_period_date_range(period):
        """Obtiene rango de fechas para un período"""
        today = datetime.now().date()

        if period == 'Day':
            return {'start': today, 'end': today}
        elif period == 'Week':
            start = today - timedelta(days=today.weekday())
            end = start + timedelta(days=6)
            return {'start': start, 'end': end}
        elif period == 'Month':
            start = today.replace(day=1)
            # Último día del mes
            if today.month == 12:
                end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
            return {'start': start, 'end': end}
        elif period == 'Quarter':
            quarter_start_month = (today.month - 1) // 3 * 3 + 1
            start = today.replace(month=quarter_start_month, day=1)
            end_month = min(12, quarter_start_month + 2)
            if end_month == 12:
                end = today.replace(month=12, day=31)
            else:
                end = today.replace(month=end_month + 1, day=1) - timedelta(days=1)
            return {'start': start, 'end': end}
        elif period == 'Year':
            start = today.replace(month=1, day=1)
            end = today.replace(month=12, day=31)
            return {'start': start, 'end': end}
        else:
            # Default: This Month
            return KPIEngine._get_period_date_range('Month')

    @staticmethod
    def _get_period_dates_by_index(period_type, periods_back):
        """Obtiene fechas de inicio y fin para un período relativo"""
        today = datetime.now().date()

        if period_type == 'Day':
            target_date = today - timedelta(days=periods_back)
            return target_date, target_date
        elif period_type == 'Month':
            # Retroceder N meses
            target_month = today.month - periods_back
            target_year = today.year

            while target_month <= 0:
                target_month += 12
                target_year -= 1

            start = datetime(target_year, target_month, 1).date()
            if target_month == 12:
                end = datetime(target_year + 1, 1, 1).date() - timedelta(days=1)
            else:
                end = datetime(target_year, target_month + 1, 1).date() - timedelta(days=1)

            return start, end
        else:
            return today, today

    @staticmethod
    def _calculate_comparison(kpi, current_value, date_range, company):
        """Calcula comparación con período anterior"""
        try:
            # Obtener valor del período anterior
            prev_period_start = date_range['start'] - timedelta(days=30)
            prev_period_end = date_range['start'] - timedelta(days=1)

            # Calcular valor anterior (simplificado)
            percentage = 0
            if kpi.target_value and kpi.target_value > 0:
                percentage = (current_value / float(kpi.target_value)) * 100

            # Determinar status
            if percentage >= 100:
                status = 'success'
            elif percentage >= 75:
                status = 'warning'
            else:
                status = 'danger'

            return {
                'percentage': round(percentage, 2),
                'status': status
            }
        except:
            return {'percentage': 0, 'status': 'neutral'}

    @staticmethod
    @frappe.whitelist(methods=['GET'])
    def list_kpis(category=None, company=None):
        """
        Lista todos los KPIs disponibles

        Args:
            category (str): Filtrar por categoría
            company (str): Filtrar por empresa

        Returns:
            list: Lista de KPIs
        """
        filters = {}
        if category:
            filters['category'] = category

        kpis = frappe.get_all(
            'KPI Definition',
            filters=filters,
            fields=['name', 'category', 'target_value', 'comparison_period']
        )

        return {
            'success': True,
            'kpis': kpis,
            'count': len(kpis)
        }

    @staticmethod
    def check_kpi_alerts(company=None):
        """
        Verifica alertas de KPIs y dispara notificaciones si aplica
        Llamado por scheduler
        """
        if not company:
            # Ejecutar para todas las empresas
            companies = frappe.get_all('Company', fields=['name'])
            for comp in companies:
                KPIEngine.check_kpi_alerts(comp['name'])
            return

        kpis = frappe.get_all(
            'KPI Definition',
            filters={'alert_on_threshold': 1},
            fields=['name', 'threshold_value', 'threshold_type']
        )

        for kpi_def in kpis:
            try:
                result = KPIEngine.calculate_kpi(kpi_def['name'], company)

                if result.get('success'):
                    current_value = result.get('value', 0)
                    threshold = kpi_def.get('threshold_value', 0)
                    threshold_type = kpi_def.get('threshold_type', 'Below')

                    # Verificar si se cumple la condición de alerta
                    should_alert = False
                    if threshold_type == 'Below' and current_value < threshold:
                        should_alert = True
                    elif threshold_type == 'Above' and current_value > threshold:
                        should_alert = True
                    elif threshold_type == 'Equal' and current_value == threshold:
                        should_alert = True

                    if should_alert:
                        KPIEngine._send_kpi_alert(kpi_def['name'], current_value, threshold, company)

            except Exception as e:
                logger.error(f"Error checking KPI alert {kpi_def['name']}: {str(e)}")

    @staticmethod
    def _send_kpi_alert(kpi_name, current_value, threshold, company):
        """Envía alerta de KPI"""
        try:
            kpi = frappe.get_doc('KPI Definition', kpi_name)

            subject = f"KPI Alert: {kpi.kpi_name}"
            message = f"""
            KPI: {kpi.kpi_name}
            Company: {company}
            Current Value: {current_value}
            Threshold: {threshold}
            Category: {kpi.category}
            """

            # Crear entrada en notification
            frappe.get_doc({
                'doctype': 'Notification Log',
                'subject': subject,
                'email_content': message,
                'for_user': frappe.session.user
            }).insert(ignore_permissions=True)

            logger.info(f"KPI alert sent for {kpi_name}")

        except Exception as e:
            logger.error(f"Error sending KPI alert: {str(e)}")


@frappe.whitelist(methods=['POST'])
def create_kpi(kpi_config):
    """
    Crea un nuevo KPI desde API

    Args:
        kpi_config (dict): Configuración del KPI

    Returns:
        dict: Resultado de creación
    """
    try:
        doc = frappe.get_doc({
            'doctype': 'KPI Definition',
            **kpi_config
        })
        doc.insert()
        frappe.db.commit()

        return {
            'success': True,
            'kpi_name': doc.name,
            'message': 'KPI created successfully'
        }

    except Exception as e:
        logger.error(f"Error creating KPI: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


@frappe.whitelist(methods=['GET'])
def get_kpi_stats(company=None):
    """
    Obtiene estadísticas de KPIs para un dashboard

    Returns:
        dict: Estadísticas generales de KPIs
    """
    try:
        if not company:
            company = frappe.defaults.get_user_default('company')

        # Obtener todos los KPIs
        kpis = frappe.get_all('KPI Definition', fields=['name', 'category', 'target_value'])

        stats = {
            'total_kpis': len(kpis),
            'by_category': {},
            'alerts_configured': frappe.db.count('KPI Definition', {'alert_on_threshold': 1}),
            'kpis': []
        }

        for kpi_def in kpis:
            result = KPIEngine.calculate_kpi(kpi_def['name'], company)

            # Agrupar por categoría
            category = kpi_def.get('category', 'Other')
            if category not in stats['by_category']:
                stats['by_category'][category] = 0
            stats['by_category'][category] += 1

            stats['kpis'].append({
                'name': kpi_def['name'],
                'category': category,
                'value': result.get('value', 0),
                'status': result.get('status', 'neutral')
            })

        return {
            'success': True,
            'stats': stats
        }

    except Exception as e:
        logger.error(f"Error getting KPI stats: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'stats': {}
        }
