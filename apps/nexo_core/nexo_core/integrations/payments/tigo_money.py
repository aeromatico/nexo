"""
Integración con Tigo Money - Bolivia

Sistema de transferencia de dinero móvil de Tigo
"""

import requests
import frappe
from frappe import _


class TigoMoneyGateway:
    """Gateway para pagos con Tigo Money"""

    def __init__(self):
        self.base_url = self._get_config('tigo_money_url') or 'https://api.tigo.bo'
        self.api_key = self._get_config('tigo_money_api_key')
        self.merchant_code = self._get_config('tigo_money_merchant_code')

        if not self.api_key or not self.merchant_code:
            frappe.throw(_("Tigo Money configuration not found"))

    def _get_config(self, key):
        """Obtiene configuración"""
        try:
            config = frappe.get_single('Integration Config')
            return config.get(key)
        except frappe.DoesNotExistError:
            return None

    def create_payment_request(self, order_id, amount, phone_number, description):
        """
        Crea solicitud de pago por Tigo Money

        Args:
            order_id: ID de orden
            amount: Monto en BOB
            phone_number: Número Tigo Money del cliente
            description: Descripción

        Returns:
            dict: Resultado
        """
        url = f"{self.base_url}/v1/payment/request"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "merchant_code": self.merchant_code,
            "order_id": order_id,
            "amount": float(amount),
            "currency": "BOB",
            "phone_number": phone_number,
            "description": description,
            "return_url": f"{frappe.utils.get_url()}/payment/callback"
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                self._save_transaction(order_id, data.get('request_id'), 'pending', amount)
                return {
                    'success': True,
                    'request_id': data.get('request_id'),
                    'status_url': data.get('status_url')
                }
            else:
                frappe.log_error(f"Tigo Money Error: {response.text}", "Tigo Money Request Failed")
                return {'success': False, 'error': response.text}

        except requests.RequestException as e:
            frappe.log_error(str(e), "Tigo Money Connection Error")
            return {'success': False, 'error': str(e)}

    def check_payment_status(self, request_id):
        """
        Verifica estado de solicitud de pago

        Args:
            request_id: ID de solicitud

        Returns:
            dict: Estado
        """
        url = f"{self.base_url}/v1/payment/status/{request_id}"
        headers = {"Authorization": f"Bearer {self.api_key}"}

        try:
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'status': data.get('status'),
                    'amount': data.get('amount'),
                    'completed_at': data.get('completed_at')
                }
            else:
                return {'success': False, 'error': response.text}

        except requests.RequestException as e:
            return {'success': False, 'error': str(e)}

    def _save_transaction(self, order_id, request_id, status, amount):
        """Guarda transacción en log"""
        try:
            frappe.get_doc({
                'doctype': 'Integration Log',
                'integration': 'Tigo Money',
                'status': status,
                'reference': order_id,
                'transaction_id': request_id,
                'amount': amount
            }).insert(ignore_permissions=True)
            frappe.db.commit()
        except Exception as e:
            frappe.log_error(str(e), "Failed to log Tigo Money transaction")


@frappe.whitelist()
def create_tigo_money_payment(order_id, phone_number):
    """
    API endpoint: Crea solicitud de pago Tigo Money

    Args:
        order_id: ID de orden
        phone_number: Número Tigo Money

    Returns:
        dict: Resultado
    """
    try:
        order = frappe.get_doc('Online Order', order_id)
        gateway = TigoMoneyGateway()

        result = gateway.create_payment_request(
            order_id=order.name,
            amount=float(order.total),
            phone_number=phone_number,
            description=f"Pago orden {order.name}"
        )

        return result
    except Exception as e:
        frappe.log_error(str(e), "Tigo Money Payment Error")
        return {'success': False, 'error': str(e)}
