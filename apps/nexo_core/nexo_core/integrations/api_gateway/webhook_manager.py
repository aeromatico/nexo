"""
Gestor de Webhooks Personalizables

Permite que clientes suscriban a eventos y reciban notificaciones
"""

import frappe
import requests
import json
from frappe import _
import hmac
import hashlib


@frappe.whitelist()
def subscribe_webhook(url, event, secret=None):
    """
    Suscribe webhook a un evento

    Args:
        url: URL del webhook donde enviar notificaciones
        event: Evento a suscribirse (invoice.created, order.paid, etc)
        secret: Secret para firmar payloads (opcional)

    Returns:
        dict: ID del webhook creado
    """
    try:
        doc = frappe.get_doc({
            'doctype': 'Webhook Subscription',
            'webhook_url': url,
            'event': event,
            'secret': secret,
            'enabled': 1,
            'user': frappe.session.user
        })
        doc.insert()
        frappe.db.commit()

        return {
            'success': True,
            'webhook_id': doc.name,
            'message': 'Webhook subscription created'
        }
    except Exception as e:
        frappe.log_error(str(e), "Webhook Creation Error")
        return {'success': False, 'error': str(e)}


@frappe.whitelist()
def unsubscribe_webhook(webhook_id):
    """
    Desuscribe webhook

    Args:
        webhook_id: ID del webhook a eliminar

    Returns:
        dict: Resultado
    """
    try:
        frappe.delete_doc('Webhook Subscription', webhook_id, ignore_permissions=True)
        frappe.db.commit()

        return {'success': True, 'message': 'Webhook unsubscribed'}
    except Exception as e:
        frappe.log_error(str(e), "Webhook Deletion Error")
        return {'success': False, 'error': str(e)}


@frappe.whitelist()
def list_webhooks():
    """
    Lista webhooks del usuario actual

    Returns:
        list: Webhooks suscritos
    """
    try:
        user = frappe.session.user

        webhooks = frappe.get_all('Webhook Subscription',
                                  filters={'user': user},
                                  fields=['name', 'webhook_url', 'event', 'enabled', 'creation'])

        return webhooks
    except Exception as e:
        frappe.log_error(str(e), "List Webhooks Error")
        return []


def trigger_webhooks(event, data):
    """
    Dispara webhooks para un evento específico

    Args:
        event: Nombre del evento (invoice.created, order.paid, etc)
        data: Datos a enviar en el webhook
    """
    try:
        # Obtener subscripciones activas para este evento
        subscriptions = frappe.get_all('Webhook Subscription',
                                       filters={'event': event, 'enabled': 1},
                                       fields=['name', 'webhook_url', 'secret'])

        for sub in subscriptions:
            try:
                send_webhook(sub.webhook_url, data, sub.secret)
                log_webhook_delivery(sub.name, 'success', data)
            except Exception as e:
                log_webhook_delivery(sub.name, 'failed', data, str(e))
                frappe.log_error(str(e), f"Webhook Delivery Failed: {sub.name}")

    except Exception as e:
        frappe.log_error(str(e), "Trigger Webhooks Error")


def send_webhook(url, data, secret=None):
    """
    Envía webhook POST request

    Args:
        url: URL del webhook
        data: Datos a enviar
        secret: Secret para firmar (opcional)

    Raises:
        Exception: Si falla el envío
    """
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Nexo ERP/2.0'
    }

    payload = json.dumps(data)

    # Firmar con HMAC SHA256 si hay secret
    if secret:
        signature = hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()

        headers['X-Webhook-Signature'] = signature
        headers['X-Webhook-Signature-Algorithm'] = 'sha256'

    # Agregar timestamp
    from frappe.utils import now_datetime
    headers['X-Webhook-Timestamp'] = now_datetime().isoformat()

    response = requests.post(url, data=payload, headers=headers, timeout=10)
    response.raise_for_status()


def log_webhook_delivery(subscription_id, status, data, error=None):
    """
    Registra entrega de webhook

    Args:
        subscription_id: ID de subscription
        status: Estado (success, failed)
        data: Datos enviados
        error: Mensaje de error si aplica
    """
    try:
        frappe.get_doc({
            'doctype': 'Integration Log',
            'integration': 'Webhook',
            'status': status,
            'reference': subscription_id,
            'content': json.dumps(data)[:500],
            'error': error
        }).insert(ignore_permissions=True)
        frappe.db.commit()
    except Exception as e:
        frappe.log_error(str(e), "Failed to log webhook delivery")


# Eventos disponibles
WEBHOOK_EVENTS = [
    'invoice.created',
    'invoice.paid',
    'invoice.cancelled',
    'order.created',
    'order.confirmed',
    'order.shipped',
    'order.delivered',
    'order.cancelled',
    'payment.received',
    'payment.failed',
    'customer.created',
    'customer.updated',
    'product.created',
    'product.updated',
    'product.deleted'
]


@frappe.whitelist(allow_guest=True)
def get_available_events():
    """
    API endpoint: Obtiene lista de eventos disponibles

    Returns:
        list: Eventos disponibles para webhooks
    """
    return WEBHOOK_EVENTS


# Hooks para disparar webhooks automáticamente

def on_invoice_submit(doc, method=None):
    """Hook: Dispara webhook cuando se crea factura"""
    if doc.docstatus == 1:
        trigger_webhooks('invoice.created', {
            'invoice_id': doc.name,
            'customer': doc.customer,
            'total': float(doc.grand_total),
            'date': doc.posting_date.isoformat(),
            'event': 'invoice.created',
            'timestamp': frappe.utils.now()
        })


def on_invoice_paid(doc, method=None):
    """Hook: Dispara webhook cuando factura es pagada"""
    trigger_webhooks('invoice.paid', {
        'invoice_id': doc.name,
        'amount': float(doc.grand_total),
        'date': frappe.utils.today(),
        'event': 'invoice.paid',
        'timestamp': frappe.utils.now()
    })


def on_online_order_submit(doc, method=None):
    """Hook: Dispara webhook cuando se crea orden"""
    trigger_webhooks('order.created', {
        'order_id': doc.name,
        'customer': doc.customer,
        'total': float(doc.total),
        'status': doc.status,
        'date': doc.creation.isoformat(),
        'event': 'order.created',
        'timestamp': frappe.utils.now()
    })


def on_online_order_update(doc, method=None):
    """Hook: Dispara webhook cuando cambia estado de orden"""
    if doc.status == 'Shipped':
        trigger_webhooks('order.shipped', {
            'order_id': doc.name,
            'tracking_number': doc.tracking_number,
            'carrier': doc.shipping_provider,
            'event': 'order.shipped',
            'timestamp': frappe.utils.now()
        })

    elif doc.status == 'Delivered':
        trigger_webhooks('order.delivered', {
            'order_id': doc.name,
            'delivery_date': frappe.utils.today(),
            'event': 'order.delivered',
            'timestamp': frappe.utils.now()
        })

    elif doc.docstatus == 2:  # Cancelled
        trigger_webhooks('order.cancelled', {
            'order_id': doc.name,
            'reason': doc.get('cancellation_reason'),
            'event': 'order.cancelled',
            'timestamp': frappe.utils.now()
        })


def on_payment_entry_submit(doc, method=None):
    """Hook: Dispara webhook cuando se recibe pago"""
    if doc.docstatus == 1 and doc.party_type == 'Customer':
        trigger_webhooks('payment.received', {
            'payment_id': doc.name,
            'customer': doc.party,
            'amount': float(doc.paid_amount),
            'method': doc.mode_of_payment,
            'date': doc.posting_date.isoformat(),
            'event': 'payment.received',
            'timestamp': frappe.utils.now()
        })


def on_customer_submit(doc, method=None):
    """Hook: Dispara webhook cuando se crea cliente"""
    trigger_webhooks('customer.created', {
        'customer_id': doc.name,
        'name': doc.customer_name,
        'type': doc.customer_type,
        'email': doc.email_id,
        'event': 'customer.created',
        'timestamp': frappe.utils.now()
    })
