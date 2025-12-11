"""
Integración con PagoFácil - Bolivia

Sistema de pago con tarjeta de crédito/débito
"""

import requests
import frappe
from frappe import _


class PagoFacilGateway:
    """Gateway para pagos con PagoFácil"""

    def __init__(self):
        self.base_url = self._get_config('pagofacil_url') or 'https://api.pagofacil.bo'
        self.commerce_id = self._get_config('pagofacil_commerce_id')
        self.api_key = self._get_config('pagofacil_api_key')

        if not self.commerce_id or not self.api_key:
            frappe.throw(_("PagoFácil configuration not found"))

    def _get_config(self, key):
        """Obtiene configuración"""
        try:
            config = frappe.get_single('Integration Config')
            return config.get(key)
        except frappe.DoesNotExistError:
            return None

    def create_transaction(self, order_id, amount, card_token, description):
        """
        Crea transacción de pago con PagoFácil

        Args:
            order_id: ID de orden
            amount: Monto en BOB
            card_token: Token de tarjeta
            description: Descripción

        Returns:
            dict: Resultado
        """
        url = f"{self.base_url}/v1/transaction"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "commerce_id": self.commerce_id,
            "transaction_id": order_id,
            "amount": float(amount),
            "currency": "BOB",
            "card_token": card_token,
            "description": description
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                status = 'approved' if data.get('status') == 'approved' else 'pending'
                self._save_transaction(order_id, data.get('transaction_id'), status, amount)

                return {
                    'success': data.get('status') == 'approved',
                    'transaction_id': data.get('transaction_id'),
                    'status': status,
                    'message': data.get('message')
                }
            else:
                frappe.log_error(f"PagoFácil Error: {response.text}", "PagoFacil Transaction Failed")
                return {'success': False, 'error': response.text}

        except requests.RequestException as e:
            frappe.log_error(str(e), "PagoFácil Connection Error")
            return {'success': False, 'error': str(e)}

    def refund_transaction(self, transaction_id, amount=None):
        """
        Reembolsa una transacción

        Args:
            transaction_id: ID de transacción
            amount: Monto a reembolsar

        Returns:
            dict: Resultado
        """
        url = f"{self.base_url}/v1/transaction/refund"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "commerce_id": self.commerce_id,
            "transaction_id": transaction_id
        }

        if amount:
            payload['amount'] = float(amount)

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'refund_id': data.get('refund_id'),
                    'status': 'refunded'
                }
            else:
                return {'success': False, 'error': response.text}

        except requests.RequestException as e:
            return {'success': False, 'error': str(e)}

    def _save_transaction(self, order_id, transaction_id, status, amount):
        """Guarda transacción en log"""
        try:
            frappe.get_doc({
                'doctype': 'Integration Log',
                'integration': 'PagoFácil',
                'status': status,
                'reference': order_id,
                'transaction_id': transaction_id,
                'amount': amount
            }).insert(ignore_permissions=True)
            frappe.db.commit()
        except Exception as e:
            frappe.log_error(str(e), "Failed to log PagoFácil transaction")


@frappe.whitelist()
def create_pagofacil_transaction(order_id, card_token):
    """
    API endpoint: Crea transacción PagoFácil

    Args:
        order_id: ID de orden
        card_token: Token de tarjeta

    Returns:
        dict: Resultado
    """
    try:
        order = frappe.get_doc('Online Order', order_id)
        gateway = PagoFacilGateway()

        result = gateway.create_transaction(
            order_id=order.name,
            amount=float(order.total),
            card_token=card_token,
            description=f"Pago orden {order.name}"
        )

        return result
    except Exception as e:
        frappe.log_error(str(e), "PagoFácil Payment Error")
        return {'success': False, 'error': str(e)}
