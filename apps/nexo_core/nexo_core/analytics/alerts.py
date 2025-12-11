# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

"""
Data Alert System for triggering notifications based on conditions
Supports email, SMS, and in-app notifications
"""

import frappe
import json
from frappe.utils import now, add_days
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@frappe.whitelist(methods=['POST'])
def create_alert(alert_config):
    """
    Crea nueva alerta

    Args:
        alert_config (dict): Configuración de la alerta

    Returns:
        dict: Resultado de creación
    """
    try:
        doc = frappe.get_doc({
            'doctype': 'Data Alert',
            **alert_config
        })
        doc.insert()
        frappe.db.commit()

        return {
            'success': True,
            'alert_name': doc.name,
            'message': 'Alert created successfully'
        }

    except Exception as e:
        logger.error(f"Error creating alert: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


@frappe.whitelist(methods=['GET'])
def list_alerts(enabled_only=True):
    """
    Lista todas las alertas

    Args:
        enabled_only (bool): Solo alertas habilitadas

    Returns:
        dict: Lista de alertas
    """
    filters = {}
    if enabled_only:
        filters['enabled'] = 1

    alerts = frappe.get_all(
        'Data Alert',
        filters=filters,
        fields=['name', 'alert_name', 'alert_type', 'enabled', 'last_triggered']
    )

    return {
        'success': True,
        'alerts': alerts,
        'count': len(alerts)
    }


def check_all_alerts(company=None):
    """
    Verifica todas las alertas activas y dispara notificaciones si aplica
    Llamado por scheduler (hourly)

    Args:
        company (str): Empresa específica o None para todas
    """
    try:
        filters = {'enabled': 1}

        alerts = frappe.get_all('Data Alert', filters=filters)

        for alert_record in alerts:
            alert_doc = frappe.get_doc('Data Alert', alert_record['name'])

            try:
                if _evaluate_alert_condition(alert_doc):
                    trigger_alert(alert_doc)

            except Exception as e:
                logger.error(f"Error checking alert {alert_record['name']}: {str(e)}")

    except Exception as e:
        logger.error(f"Error in check_all_alerts: {str(e)}")


def _evaluate_alert_condition(alert_doc):
    """
    Evalúa si se cumple la condición de la alerta

    Args:
        alert_doc: Documento de alerta

    Returns:
        bool: True si se cumple la condición
    """
    try:
        condition = json.loads(alert_doc.condition)

        # Estructura esperada: {"field": "stock_qty", "operator": "<", "value": 10}
        # O para documentos: {"doctype": "Item", "field": "stock_qty", "operator": "<", "value": 10}

        doctype = alert_doc.document_type or condition.get('doctype')
        field = condition.get('field')
        operator = condition.get('operator')
        threshold = condition.get('value')

        if not all([doctype, field, operator, threshold]):
            logger.warning(f"Invalid alert condition for {alert_doc.name}")
            return False

        # Construir filtro
        if operator == '<':
            filters = {field: ['<', threshold]}
        elif operator == '>':
            filters = {field: ['>', threshold]}
        elif operator == '==':
            filters = {field: threshold}
        elif operator == '!=':
            filters = {field: ['!=', threshold]}
        elif operator == '>=':
            filters = {field: ['>=', threshold]}
        elif operator == '<=':
            filters = {field: ['<=', threshold]}
        else:
            logger.warning(f"Unknown operator {operator} in alert {alert_doc.name}")
            return False

        # Obtener registros que cumplen la condición
        matching_records = frappe.get_all(doctype, filters=filters)

        return len(matching_records) > 0

    except Exception as e:
        logger.error(f"Error evaluating alert condition: {str(e)}")
        return False


def trigger_alert(alert_doc):
    """
    Dispara la alerta (envía notificaciones)

    Args:
        alert_doc: Documento de alerta
    """
    try:
        if alert_doc.notification_method in ['Email', 'All']:
            _send_alert_email(alert_doc)

        if alert_doc.notification_method in ['In-App', 'All']:
            _create_in_app_notification(alert_doc)

        if alert_doc.notification_method in ['SMS', 'All']:
            _send_alert_sms(alert_doc)

        # Actualizar last_triggered
        alert_doc.last_triggered = now()
        alert_doc.save()

        logger.info(f"Alert {alert_doc.name} triggered successfully")

    except Exception as e:
        logger.error(f"Error triggering alert {alert_doc.name}: {str(e)}")


def _send_alert_email(alert_doc):
    """Envía alerta por email"""
    try:
        recipients = []

        # Obtener recipients desde tabla
        if alert_doc.recipients:
            for recipient in alert_doc.recipients:
                if recipient.recipient_type == 'User':
                    user_doc = frappe.get_doc('User', recipient.recipient_value)
                    recipients.append(user_doc.email)
                elif recipient.recipient_type == 'Email':
                    recipients.append(recipient.recipient_value)
                elif recipient.recipient_type == 'Role':
                    role_users = frappe.get_all(
                        'User',
                        filters={'role_profile_name': recipient.recipient_value}
                    )
                    for user in role_users:
                        user_doc = frappe.get_doc('User', user['name'])
                        recipients.append(user_doc.email)

        if not recipients:
            # Usar usuario actual
            recipients = [frappe.session.user]

        subject = f"Alert: {alert_doc.alert_name}"
        message = f"""
        <h3>Data Alert Triggered</h3>
        <p><strong>Alert:</strong> {alert_doc.alert_name}</p>
        <p><strong>Type:</strong> {alert_doc.alert_type}</p>
        <p><strong>Document:</strong> {alert_doc.document_type}</p>
        <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        """

        # Usar frappe.sendmail para enviar
        frappe.sendmail(
            recipients=recipients,
            subject=subject,
            message=message,
            reference_doctype='Data Alert',
            reference_name=alert_doc.name
        )

        logger.info(f"Alert email sent to {recipients}")

    except Exception as e:
        logger.error(f"Error sending alert email: {str(e)}")


def _create_in_app_notification(alert_doc):
    """Crea notificación dentro de la aplicación"""
    try:
        frappe.get_doc({
            'doctype': 'Notification Log',
            'document_type': alert_doc.document_type,
            'document_name': alert_doc.name,
            'subject': f"Alert: {alert_doc.alert_name}",
            'email_content': f"Data alert {alert_doc.alert_name} has been triggered",
            'for_user': frappe.session.user
        }).insert(ignore_permissions=True)

        logger.info(f"In-app notification created for alert {alert_doc.name}")

    except Exception as e:
        logger.error(f"Error creating in-app notification: {str(e)}")


def _send_alert_sms(alert_doc):
    """Envía alerta por SMS (placeholder para integración futura)"""
    logger.info(f"SMS alert placeholder for {alert_doc.name}")
    # Implementar integración con proveedor SMS
    pass


@frappe.whitelist(methods=['GET'])
def get_triggered_alerts(user=None, days=7):
    """
    Obtiene alertas disparadas recientemente

    Args:
        user (str): Usuario específico
        days (int): Número de días a incluir

    Returns:
        dict: Alertas disparadas
    """
    try:
        cutoff_date = add_days(now(), -days)

        filters = {
            'last_triggered': ['>=', cutoff_date],
            'last_triggered': ['!=', '']
        }

        alerts = frappe.get_all(
            'Data Alert',
            filters=filters,
            fields=['name', 'alert_name', 'alert_type', 'last_triggered'],
            order_by='last_triggered desc'
        )

        return {
            'success': True,
            'alerts': alerts,
            'count': len(alerts),
            'period_days': days
        }

    except Exception as e:
        logger.error(f"Error getting triggered alerts: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'alerts': []
        }


@frappe.whitelist(methods=['GET'])
def get_alert_stats():
    """
    Obtiene estadísticas de alertas

    Returns:
        dict: Estadísticas consolidadas
    """
    try:
        total_alerts = frappe.db.count('Data Alert')
        enabled_alerts = frappe.db.count('Data Alert', {'enabled': 1})
        triggered_alerts = frappe.db.count('Data Alert', {'last_triggered': ['!=', '']})

        # Alertas disparadas en últimas 24 horas
        cutoff = add_days(now(), -1)
        recently_triggered = frappe.db.count(
            'Data Alert',
            {'last_triggered': ['>=', cutoff]}
        )

        # Alertas por tipo
        alerts_by_type = {}
        all_alerts = frappe.get_all(
            'Data Alert',
            fields=['alert_type']
        )
        for alert in all_alerts:
            alert_type = alert.get('alert_type', 'Other')
            alerts_by_type[alert_type] = alerts_by_type.get(alert_type, 0) + 1

        return {
            'success': True,
            'stats': {
                'total_alerts': total_alerts,
                'enabled_alerts': enabled_alerts,
                'disabled_alerts': total_alerts - enabled_alerts,
                'triggered_alerts': triggered_alerts,
                'recently_triggered': recently_triggered,
                'by_type': alerts_by_type
            }
        }

    except Exception as e:
        logger.error(f"Error getting alert stats: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'stats': {}
        }


@frappe.whitelist(methods=['POST'])
def test_alert(alert_name):
    """
    Prueba una alerta enviando notificación de test

    Args:
        alert_name (str): Nombre de la alerta

    Returns:
        dict: Resultado de prueba
    """
    try:
        alert_doc = frappe.get_doc('Data Alert', alert_name)

        # Crear email de prueba
        recipients = [frappe.session.user]

        subject = f"TEST ALERT: {alert_doc.alert_name}"
        message = f"""
        <h3>Test Alert Notification</h3>
        <p>This is a test message from alert: {alert_doc.alert_name}</p>
        <p>Alert Type: {alert_doc.alert_type}</p>
        <p>Document Type: {alert_doc.document_type}</p>
        <p>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        """

        frappe.sendmail(
            recipients=recipients,
            subject=subject,
            message=message
        )

        return {
            'success': True,
            'message': f'Test alert sent to {frappe.session.user}'
        }

    except Exception as e:
        logger.error(f"Error testing alert: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }
