"""
Integración con QR Interbank - Bolivia

Sistema de pago mediante códigos QR simples en Bolivia
"""

import requests
import frappe
from frappe import _
from datetime import datetime, timedelta
import base64


class QRInterbankGateway:
    """Gateway para pagos QR Interbank Bolivia"""

    def __init__(self):
        self.base_url = self._get_config('qr_interbank_url') or 'https://api.qrbolivia.com'
        self.merchant_id = self._get_config('qr_interbank_merchant_id')
        self.api_key = self._get_config('qr_interbank_api_key')

        if not self.merchant_id or not self.api_key:
            frappe.throw(_("QR Interbank configuration not found"))

    def _get_config(self, key):
        """Obtiene configuración"""
        try:
            config = frappe.get_single('Integration Config')
            return config.get(key)
        except frappe.DoesNotExistError:
            return None

    def generate_qr(self, order_id, amount, description, expiration_minutes=60):
        """
        Genera código QR para pago en Bolivia

        Args:
            order_id: ID de la orden
            amount: Monto en BOB
            description: Descripción del pago
            expiration_minutes: Minutos antes de expirar

        Returns:
            dict: QR code en base64 y detalles
        """
        url = f"{self.base_url}/v1/qr/generate"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "merchant_id": self.merchant_id,
            "amount": float(amount),
            "currency": "BOB",
            "reference": order_id,
            "description": description[:100],
            "expiration": expiration_minutes * 60  # En segundos
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()

                # Guardar QR en BD
                self._save_qr(order_id, data.get('qr_code'), data.get('qr_id'), amount)

                return {
                    'success': True,
                    'qr_code': data.get('qr_code'),  # Base64 image
                    'qr_id': data.get('qr_id'),
                    'amount': amount,
                    'reference': order_id,
                    'expiration_time': datetime.now() + timedelta(minutes=expiration_minutes)
                }
            else:
                error_msg = response.text
                frappe.log_error(f"QR Generation Error: {error_msg}", "QR Interbank Failed")
                return {
                    'success': False,
                    'error': f"Failed to generate QR: {error_msg}"
                }

        except requests.RequestException as e:
            frappe.log_error(str(e), "QR Interbank Connection Error")
            return {
                'success': False,
                'error': str(e)
            }

    def verify_payment(self, qr_id):
        """
        Verifica si un QR ha sido pagado

        Args:
            qr_id: ID del QR generado

        Returns:
            dict: Estado del pago
        """
        url = f"{self.base_url}/v1/qr/status/{qr_id}"
        headers = {"Authorization": f"Bearer {self.api_key}"}

        try:
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'paid': data.get('status') == 'paid',
                    'amount': data.get('amount'),
                    'paid_at': data.get('paid_at'),
                    'transaction_id': data.get('transaction_id')
                }
            else:
                return {
                    'success': False,
                    'paid': False,
                    'error': response.text
                }

        except requests.RequestException as e:
            frappe.log_error(str(e), "QR Verification Error")
            return {
                'success': False,
                'paid': False,
                'error': str(e)
            }

    def check_pending_payments(self):
        """
        Verifica pagos pendientes en el sistema

        Debe ejecutarse como scheduled job
        """
        # Obtener QRs pendientes creados en las últimas 2 horas
        pending_qrs = frappe.db.get_all('Integration Log',
                                        filters={
                                            'integration': 'QR Interbank',
                                            'status': 'generated',
                                            'creation': ['>=', datetime.now() - timedelta(hours=2)]
                                        },
                                        fields=['name', 'transaction_id', 'reference'])

        for qr_log in pending_qrs:
            qr_id = qr_log.transaction_id
            order_id = qr_log.reference

            # Verificar estado
            result = self.verify_payment(qr_id)

            if result['success'] and result['paid']:
                # Actualizar orden como pagada
                try:
                    order = frappe.get_doc('Online Order', order_id)
                    order.payment_status = 'Paid'
                    order.qr_payment_id = qr_id
                    order.save()

                    # Actualizar log
                    log_doc = frappe.get_doc('Integration Log', qr_log.name)
                    log_doc.status = 'paid'
                    log_doc.save()

                    frappe.db.commit()

                    # Dispara webhooks
                    from nexo_core.integrations.api_gateway.webhook_manager import trigger_webhooks
                    trigger_webhooks('payment.received', {
                        'payment_id': qr_id,
                        'order_id': order_id,
                        'amount': result.get('amount'),
                        'method': 'QR Interbank',
                        'timestamp': result.get('paid_at')
                    })

                except Exception as e:
                    frappe.log_error(str(e), "Error updating order after QR payment")

    def cancel_qr(self, qr_id):
        """
        Cancela un QR generado

        Args:
            qr_id: ID del QR

        Returns:
            dict: Resultado
        """
        url = f"{self.base_url}/v1/qr/cancel/{qr_id}"
        headers = {"Authorization": f"Bearer {self.api_key}"}

        try:
            response = requests.post(url, headers=headers, timeout=10)

            if response.status_code == 200:
                return {'success': True, 'message': 'QR cancelled'}
            else:
                return {'success': False, 'error': response.text}

        except requests.RequestException as e:
            return {'success': False, 'error': str(e)}

    def _save_qr(self, order_id, qr_code, qr_id, amount):
        """
        Guarda QR en Integration Log

        Args:
            order_id: ID de orden
            qr_code: Código QR en base64
            qr_id: ID del QR
            amount: Monto
        """
        try:
            frappe.get_doc({
                'doctype': 'Integration Log',
                'integration': 'QR Interbank',
                'status': 'generated',
                'reference': order_id,
                'transaction_id': qr_id,
                'amount': amount,
                'content': qr_code[:200] if qr_code else None  # Guardar parte del base64
            }).insert(ignore_permissions=True)
            frappe.db.commit()
        except Exception as e:
            frappe.log_error(str(e), "Failed to save QR to Integration Log")


@frappe.whitelist()
def generate_payment_qr(order_id, expiration_minutes=60):
    """
    API endpoint: Genera QR de pago para orden

    Args:
        order_id: ID de la orden
        expiration_minutes: Minutos antes de expirar

    Returns:
        dict: QR code y detalles
    """
    try:
        order = frappe.get_doc('Online Order', order_id)

        gateway = QRInterbankGateway()
        result = gateway.generate_qr(
            order_id=order.name,
            amount=float(order.total),
            description=f"Pago orden {order.name} - {order.customer_name}",
            expiration_minutes=expiration_minutes
        )

        return result
    except Exception as e:
        frappe.log_error(str(e), "QR Generation Error")
        return {'success': False, 'error': str(e)}


@frappe.whitelist()
def verify_qr_payment(qr_id):
    """
    API endpoint: Verifica estado de pago QR

    Args:
        qr_id: ID del QR

    Returns:
        dict: Estado del pago
    """
    try:
        gateway = QRInterbankGateway()
        result = gateway.verify_payment(qr_id)

        if result['success'] and result['paid']:
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

        return result
    except Exception as e:
        frappe.log_error(str(e), "QR Verification Error")
        return {'success': False, 'error': str(e)}


@frappe.whitelist()
def cancel_payment_qr(qr_id):
    """
    API endpoint: Cancela un QR

    Args:
        qr_id: ID del QR

    Returns:
        dict: Resultado
    """
    try:
        gateway = QRInterbankGateway()
        result = gateway.cancel_qr(qr_id)

        if result['success']:
            # Actualizar log
            frappe.db.set_value('Integration Log',
                               {'transaction_id': qr_id},
                               'status', 'cancelled')

        return result
    except Exception as e:
        return {'success': False, 'error': str(e)}
