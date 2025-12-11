"""
Notificaciones automáticas por WhatsApp

Proporciona hooks para enviar notificaciones automáticas cuando ocurren ciertos eventos
"""

import frappe
from frappe import _

def notify_invoice_created(doc, method=None):
    """
    Hook: Notifica al cliente cuando se crea/envía factura

    Args:
        doc: Documento de Sales Invoice
        method: Método que disparó el hook (on_submit)
    """
    if doc.docstatus == 1:  # Submitted
        try:
            # Verificar si cliente tiene WhatsApp habilitado
            customer = frappe.get_doc('Customer', doc.customer)
            if customer.get('enable_whatsapp_notifications'):
                from nexo_core.integrations.whatsapp.client import WhatsAppClient
                client = WhatsAppClient()
                result = client.send_invoice_notification(doc.name)
                frappe.msgprint(
                    _("WhatsApp notification sent to {0}").format(customer.customer_name),
                    alert=True
                )
        except Exception as e:
            frappe.log_error(str(e), "WhatsApp Invoice Notification Failed")


def notify_order_created(doc, method=None):
    """
    Hook: Notifica cuando se crea pedido en línea

    Args:
        doc: Documento de Online Order
        method: Método que disparó el hook
    """
    if doc.docstatus == 0:  # Draft - se envía al crear
        try:
            customer = frappe.get_doc('Customer', doc.customer)
            if customer.get('enable_whatsapp_notifications'):
                from nexo_core.integrations.whatsapp.client import WhatsAppClient
                client = WhatsAppClient()
                result = client.send_order_confirmation(doc.name)
                frappe.msgprint(
                    _("WhatsApp order confirmation sent to {0}").format(customer.customer_name),
                    alert=True
                )
        except Exception as e:
            frappe.log_error(str(e), "WhatsApp Order Confirmation Failed")


def notify_order_shipped(doc, method=None):
    """
    Hook: Notifica cuando pedido es enviado

    Args:
        doc: Documento de Online Order
        method: Método que disparó el hook (on_update)
    """
    try:
        # Solo enviar si status cambió a "Shipped"
        if doc.status == 'Shipped':
            customer = frappe.get_doc('Customer', doc.customer)
            if customer.get('enable_whatsapp_notifications'):
                from nexo_core.integrations.whatsapp.client import WhatsAppClient
                client = WhatsAppClient()

                phone_number = customer.get('mobile_no') or customer.get('phone')
                if phone_number:
                    phone_number = client._format_phone_number(phone_number)

                    message = f"""
Hola {customer.customer_name},

Tu pedido #{doc.name} ha sido enviado.

Número de seguimiento: {doc.get('tracking_number', 'N/A')}
Empresa de envío: {doc.get('shipping_provider', 'N/A')}

Rastra tu pedido: {doc.get('tracking_url', '')}

¡Gracias por tu compra!
                    """.strip()

                    client.send_message(phone_number, message)
                    frappe.msgprint(
                        _("WhatsApp shipment notification sent to {0}").format(customer.customer_name),
                        alert=True
                    )
    except Exception as e:
        frappe.log_error(str(e), "WhatsApp Shipment Notification Failed")


def notify_order_cancelled(doc, method=None):
    """
    Hook: Notifica cuando pedido es cancelado

    Args:
        doc: Documento de Online Order
        method: Método que disparó el hook
    """
    try:
        if doc.docstatus == 2:  # Cancelled
            customer = frappe.get_doc('Customer', doc.customer)
            if customer.get('enable_whatsapp_notifications'):
                from nexo_core.integrations.whatsapp.client import WhatsAppClient
                client = WhatsAppClient()

                phone_number = customer.get('mobile_no') or customer.get('phone')
                if phone_number:
                    phone_number = client._format_phone_number(phone_number)

                    message = f"""
Hola {customer.customer_name},

Queremos informarte que tu pedido #{doc.name} ha sido cancelado.

Si tienes alguna pregunta, no dudes en contactarnos.

Soporte: support@nexo.bo
                    """.strip()

                    client.send_message(phone_number, message)
    except Exception as e:
        frappe.log_error(str(e), "WhatsApp Order Cancellation Notification Failed")


def notify_payment_received(doc, method=None):
    """
    Hook: Notifica cuando pago es recibido

    Args:
        doc: Documento de Payment Entry
        method: Método que disparó el hook (on_submit)
    """
    try:
        if doc.docstatus == 1 and doc.party_type == 'Customer':
            customer = frappe.get_doc('Customer', doc.party)
            if customer.get('enable_whatsapp_notifications'):
                from nexo_core.integrations.whatsapp.client import WhatsAppClient
                client = WhatsAppClient()

                phone_number = customer.get('mobile_no') or customer.get('phone')
                if phone_number:
                    phone_number = client._format_phone_number(phone_number)

                    message = f"""
Hola {customer.customer_name},

Confirmamos que hemos recibido tu pago de Bs. {doc.paid_amount:.2f}.

Referencia: {doc.name}
Fecha: {doc.posting_date.strftime('%d/%m/%Y')}

¡Gracias por tu pago!
                    """.strip()

                    client.send_message(phone_number, message)
    except Exception as e:
        frappe.log_error(str(e), "WhatsApp Payment Notification Failed")


@frappe.whitelist()
def bulk_send_notifications(doctype, recipients_list):
    """
    Envía notificaciones masivas a múltiples clientes

    Args:
        doctype: Tipo de documento (Sales Invoice, Online Order, etc)
        recipients_list: Lista de IDs de documentos

    Returns:
        dict: Resultado de envío masivo
    """
    results = {
        'success': 0,
        'failed': 0,
        'errors': []
    }

    try:
        from nexo_core.integrations.whatsapp.client import WhatsAppClient
        client = WhatsAppClient()

        for doc_id in recipients_list:
            try:
                if doctype == 'Sales Invoice':
                    client.send_invoice_notification(doc_id)
                    results['success'] += 1
                elif doctype == 'Online Order':
                    client.send_order_confirmation(doc_id)
                    results['success'] += 1
            except Exception as e:
                results['failed'] += 1
                results['errors'].append({
                    'doc': doc_id,
                    'error': str(e)
                })

        return results
    except Exception as e:
        frappe.log_error(str(e), "Bulk WhatsApp Notification Error")
        return {
            'success': 0,
            'failed': len(recipients_list),
            'error': str(e)
        }


@frappe.whitelist()
def enable_whatsapp_for_customer(customer_name):
    """
    Habilita notificaciones de WhatsApp para un cliente

    Args:
        customer_name: Nombre del cliente

    Returns:
        dict: Resultado
    """
    try:
        customer = frappe.get_doc('Customer', customer_name)
        customer.enable_whatsapp_notifications = 1
        customer.save()
        frappe.db.commit()

        return {
            'success': True,
            'message': _("WhatsApp notifications enabled for {0}").format(customer.customer_name)
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


@frappe.whitelist()
def disable_whatsapp_for_customer(customer_name):
    """
    Deshabilita notificaciones de WhatsApp para un cliente

    Args:
        customer_name: Nombre del cliente

    Returns:
        dict: Resultado
    """
    try:
        customer = frappe.get_doc('Customer', customer_name)
        customer.enable_whatsapp_notifications = 0
        customer.save()
        frappe.db.commit()

        return {
            'success': True,
            'message': _("WhatsApp notifications disabled for {0}").format(customer.customer_name)
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
