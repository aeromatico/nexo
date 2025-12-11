"""
Webhook handlers para procesar confirmaciones de pago desde múltiples gateways
"""

import frappe
import hmac
import hashlib
import json


@frappe.whitelist(allow_guest=True)
def handle_payment_webhook(gateway, payload_signature=None):
    """
    Maneja webhooks de múltiples payment gateways

    Args:
        gateway: Nombre del gateway (stripe, qr_interbank, tigo_money, pagofacil)
        payload_signature: Firma del payload para validación

    Returns:
        dict: Confirmación de recepción
    """
    payload = frappe.request.get_data(as_text=True)

    # Validar firma según gateway
    if gateway == 'stripe':
        return handle_stripe_webhook(payload, payload_signature)
    elif gateway == 'qr_interbank':
        return handle_qr_interbank_webhook(payload)
    elif gateway == 'tigo_money':
        return handle_tigo_money_webhook(payload)
    elif gateway == 'pagofacil':
        return handle_pagofacil_webhook(payload)
    else:
        frappe.log_error(f"Unknown gateway: {gateway}", "Payment Webhook Error")
        return {'success': False, 'error': 'Unknown gateway'}


def handle_stripe_webhook(payload, signature):
    """Maneja webhooks de Stripe"""
    try:
        import stripe

        webhook_secret = frappe.get_single('Integration Config').stripe_webhook_secret

        event = stripe.Webhook.construct_event(payload, signature, webhook_secret)

        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            order_id = payment_intent.get('metadata', {}).get('order_id')

            if order_id:
                order = frappe.get_doc('Online Order', order_id)
                order.payment_status = 'Paid'
                order.stripe_payment_id = payment_intent['id']
                order.save()
                frappe.db.commit()

                # Dispara webhooks personalizados
                from nexo_core.integrations.api_gateway.webhook_manager import trigger_webhooks
                trigger_webhooks('payment.received', {
                    'payment_id': payment_intent['id'],
                    'order_id': order_id,
                    'amount': payment_intent['amount'] / 100,
                    'gateway': 'Stripe'
                })

                return {'success': True, 'message': 'Payment confirmed'}

        return {'success': True, 'message': 'Event received'}

    except Exception as e:
        frappe.log_error(str(e), "Stripe Webhook Handler Error")
        return {'success': False, 'error': str(e)}


def handle_qr_interbank_webhook(payload):
    """Maneja webhooks de QR Interbank"""
    try:
        data = json.loads(payload)

        if data.get('event') == 'payment_completed':
            qr_id = data.get('qr_id')
            amount = data.get('amount')

            # Buscar orden asociada
            log = frappe.db.get_value('Integration Log',
                                     filters={'transaction_id': qr_id},
                                     fieldname='reference')

            if log:
                order = frappe.get_doc('Online Order', log)
                order.payment_status = 'Paid'
                order.qr_payment_id = qr_id
                order.save()
                frappe.db.commit()

                # Dispara webhooks
                from nexo_core.integrations.api_gateway.webhook_manager import trigger_webhooks
                trigger_webhooks('payment.received', {
                    'payment_id': qr_id,
                    'order_id': log,
                    'amount': amount,
                    'gateway': 'QR Interbank'
                })

                return {'success': True, 'message': 'Payment confirmed'}

        return {'success': True, 'message': 'Event received'}

    except Exception as e:
        frappe.log_error(str(e), "QR Interbank Webhook Handler Error")
        return {'success': False, 'error': str(e)}


def handle_tigo_money_webhook(payload):
    """Maneja webhooks de Tigo Money"""
    try:
        data = json.loads(payload)

        if data.get('status') == 'completed':
            request_id = data.get('request_id')
            order_id = data.get('order_id')

            if order_id:
                order = frappe.get_doc('Online Order', order_id)
                order.payment_status = 'Paid'
                order.tigo_money_request_id = request_id
                order.save()
                frappe.db.commit()

                from nexo_core.integrations.api_gateway.webhook_manager import trigger_webhooks
                trigger_webhooks('payment.received', {
                    'payment_id': request_id,
                    'order_id': order_id,
                    'amount': data.get('amount'),
                    'gateway': 'Tigo Money'
                })

                return {'success': True, 'message': 'Payment confirmed'}

        return {'success': True, 'message': 'Event received'}

    except Exception as e:
        frappe.log_error(str(e), "Tigo Money Webhook Handler Error")
        return {'success': False, 'error': str(e)}


def handle_pagofacil_webhook(payload):
    """Maneja webhooks de PagoFácil"""
    try:
        data = json.loads(payload)

        if data.get('status') == 'approved':
            transaction_id = data.get('transaction_id')
            order_id = data.get('order_id')

            if order_id:
                order = frappe.get_doc('Online Order', order_id)
                order.payment_status = 'Paid'
                order.pagofacil_transaction_id = transaction_id
                order.save()
                frappe.db.commit()

                from nexo_core.integrations.api_gateway.webhook_manager import trigger_webhooks
                trigger_webhooks('payment.received', {
                    'payment_id': transaction_id,
                    'order_id': order_id,
                    'amount': data.get('amount'),
                    'gateway': 'PagoFácil'
                })

                return {'success': True, 'message': 'Payment confirmed'}

        return {'success': True, 'message': 'Event received'}

    except Exception as e:
        frappe.log_error(str(e), "PagoFácil Webhook Handler Error")
        return {'success': False, 'error': str(e)}


def validate_webhook_signature(gateway, payload, signature):
    """
    Valida la firma de un webhook

    Args:
        gateway: Nombre del gateway
        payload: Payload original
        signature: Firma proporcionada

    Returns:
        bool: True si la firma es válida
    """
    try:
        if gateway == 'qr_interbank':
            api_key = frappe.get_single('Integration Config').qr_interbank_api_key
            expected_signature = hmac.new(
                api_key.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()

            return hmac.compare_digest(signature, expected_signature)

        elif gateway == 'tigo_money':
            api_key = frappe.get_single('Integration Config').tigo_money_api_key
            expected_signature = hmac.new(
                api_key.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()

            return hmac.compare_digest(signature, expected_signature)

        elif gateway == 'pagofacil':
            api_key = frappe.get_single('Integration Config').pagofacil_api_key
            expected_signature = hmac.new(
                api_key.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()

            return hmac.compare_digest(signature, expected_signature)

        return False

    except Exception as e:
        frappe.log_error(str(e), "Webhook Signature Validation Error")
        return False
