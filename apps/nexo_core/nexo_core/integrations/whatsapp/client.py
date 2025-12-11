"""
Cliente para WhatsApp Business API

Proporciona funcionalidad para enviar mensajes, templates y notificaciones via WhatsApp
"""

import requests
import json
import frappe
from frappe import _

class WhatsAppClient:
    """Cliente para interactuar con WhatsApp Business API"""

    def __init__(self, phone_number_id=None, access_token=None):
        """
        Inicializa el cliente de WhatsApp

        Args:
            phone_number_id: ID del número de teléfono registrado
            access_token: Token de acceso para WhatsApp API
        """
        self.phone_number_id = phone_number_id or self._get_config('whatsapp_phone_number_id')
        self.access_token = access_token or self._get_config('whatsapp_access_token')
        self.base_url = f"https://graph.facebook.com/v18.0/{self.phone_number_id}"

        if not self.phone_number_id or not self.access_token:
            frappe.throw(_("WhatsApp configuration not found. Please configure Integration Config."))

    def _get_config(self, key):
        """Obtiene configuración de Integration Config"""
        try:
            config = frappe.get_single('Integration Config')
            return config.get(key)
        except frappe.DoesNotExistError:
            return None

    def send_message(self, to_number, message):
        """
        Envía mensaje de texto simple por WhatsApp

        Args:
            to_number: Número de teléfono destino (formato: 591XXXXXXXX)
            message: Contenido del mensaje

        Returns:
            dict: Respuesta de la API con ID del mensaje
        """
        # Formatear número de teléfono
        to_number = self._format_phone_number(to_number)

        url = f"{self.base_url}/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "text",
            "text": {"body": message}
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)

            if response.status_code == 200:
                result = response.json()
                self._log_message('sent', to_number, message)
                return result
            else:
                error_msg = response.text
                frappe.log_error(f"WhatsApp Error: {error_msg}", "WhatsApp Send Failed")
                raise Exception(f"Failed to send WhatsApp message: {error_msg}")
        except requests.RequestException as e:
            frappe.log_error(str(e), "WhatsApp Connection Error")
            raise Exception(f"WhatsApp connection error: {str(e)}")

    def send_template(self, to_number, template_name, parameters=None):
        """
        Envía mensaje usando template aprobado en WhatsApp

        Args:
            to_number: Número de teléfono destino
            template_name: Nombre del template aprobado
            parameters: Lista de parámetros para llenar el template

        Returns:
            dict: Respuesta de la API
        """
        # Formatear número de teléfono
        to_number = self._format_phone_number(to_number)

        url = f"{self.base_url}/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": "es"},
                "components": []
            }
        }

        if parameters:
            payload["template"]["components"].append({
                "type": "body",
                "parameters": [{"type": "text", "text": str(p)} for p in parameters]
            })

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)

            if response.status_code == 200:
                result = response.json()
                self._log_message('template_sent', to_number, template_name)
                return result
            else:
                error_msg = response.text
                frappe.log_error(f"WhatsApp Template Error: {error_msg}", "WhatsApp Template Failed")
                raise Exception(f"Failed to send WhatsApp template: {error_msg}")
        except requests.RequestException as e:
            frappe.log_error(str(e), "WhatsApp Connection Error")
            raise Exception(f"WhatsApp connection error: {str(e)}")

    def send_invoice_notification(self, invoice_name):
        """
        Envía notificación de factura por WhatsApp al cliente

        Args:
            invoice_name: Nombre de la factura de venta

        Returns:
            dict: Respuesta de la API
        """
        invoice = frappe.get_doc('Sales Invoice', invoice_name)
        customer = frappe.get_doc('Customer', invoice.customer)

        # Obtener número de WhatsApp del cliente
        phone_number = customer.get('mobile_no') or customer.get('phone')
        if not phone_number:
            frappe.throw(_("Customer {0} does not have a phone number").format(customer.name))

        # Formatear número
        phone_number = self._format_phone_number(phone_number)

        # Enviar usando template "invoice_notification"
        parameters = [
            customer.customer_name,
            invoice.name,
            f"Bs. {invoice.grand_total:.2f}",
            invoice.posting_date.strftime("%d/%m/%Y")
        ]

        return self.send_template(phone_number, "invoice_notification", parameters)

    def send_order_confirmation(self, order_id):
        """
        Envía confirmación de pedido por WhatsApp

        Args:
            order_id: ID del pedido en línea

        Returns:
            dict: Respuesta de la API
        """
        order = frappe.get_doc('Online Order', order_id)
        customer = frappe.get_doc('Customer', order.customer)

        phone_number = customer.get('mobile_no') or customer.get('phone')
        if not phone_number:
            frappe.throw(_("Customer {0} does not have a phone number").format(customer.name))

        phone_number = self._format_phone_number(phone_number)

        parameters = [
            customer.customer_name,
            order.name,
            str(order.total),
            order.creation.strftime("%d/%m/%Y")
        ]

        return self.send_template(phone_number, "order_confirmation", parameters)

    def send_shipment_notification(self, order_id, tracking_number):
        """
        Envía notificación de envío con tracking por WhatsApp

        Args:
            order_id: ID del pedido
            tracking_number: Número de seguimiento

        Returns:
            dict: Respuesta de la API
        """
        order = frappe.get_doc('Online Order', order_id)
        customer = frappe.get_doc('Customer', order.customer)

        phone_number = customer.get('mobile_no') or customer.get('phone')
        if not phone_number:
            return None

        phone_number = self._format_phone_number(phone_number)

        message = f"""
Hola {customer.customer_name},

Tu pedido #{order.name} ha sido enviado.

Número de seguimiento: {tracking_number}
Empresa de envío: {order.get('shipping_provider', 'N/A')}

Puedes rastrear tu pedido en: https://tracking.example.com/{tracking_number}

¡Gracias por tu compra!
        """.strip()

        return self.send_message(phone_number, message)

    def _format_phone_number(self, phone):
        """
        Formatea número de teléfono para WhatsApp (591XXXXXXXX)

        Args:
            phone: Número de teléfono en cualquier formato

        Returns:
            str: Número formateado para WhatsApp
        """
        # Remover caracteres especiales
        phone = phone.replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '')

        # Si no comienza con 591, agregar el código de país Bolivia
        if not phone.startswith('591'):
            # Si comienza con 1, reemplazarlo con 591 (Bolivia)
            if phone.startswith('1'):
                phone = '591' + phone[1:]
            else:
                phone = '591' + phone

        return phone

    def _log_message(self, status, to_number, content):
        """
        Registra mensaje en Integration Log

        Args:
            status: Estado del envío (sent, template_sent, failed)
            to_number: Número de teléfono destino
            content: Contenido del mensaje
        """
        try:
            frappe.get_doc({
                'doctype': 'Integration Log',
                'integration': 'WhatsApp',
                'status': status,
                'reference': to_number,
                'content': str(content)[:500]  # Limitar a 500 caracteres
            }).insert(ignore_permissions=True)
            frappe.db.commit()
        except Exception as e:
            frappe.log_error(str(e), "Failed to log WhatsApp message")


@frappe.whitelist()
def send_whatsapp_invoice(invoice_name):
    """
    API endpoint para enviar factura por WhatsApp

    Args:
        invoice_name: Nombre de la factura

    Returns:
        dict: Resultado de envío
    """
    try:
        client = WhatsAppClient()
        result = client.send_invoice_notification(invoice_name)
        return {"success": True, "result": result}
    except Exception as e:
        frappe.log_error(str(e), "WhatsApp Invoice Send Error")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def send_whatsapp_order_confirmation(order_id):
    """
    API endpoint para enviar confirmación de pedido por WhatsApp

    Args:
        order_id: ID del pedido

    Returns:
        dict: Resultado de envío
    """
    try:
        client = WhatsAppClient()
        result = client.send_order_confirmation(order_id)
        return {"success": True, "result": result}
    except Exception as e:
        frappe.log_error(str(e), "WhatsApp Order Confirmation Error")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def test_whatsapp_connection():
    """
    Prueba conexión con WhatsApp Business API

    Returns:
        dict: Estado de conexión
    """
    try:
        client = WhatsAppClient()

        # Obtener número de prueba de configuración
        config = frappe.get_single('Integration Config')
        test_number = config.get('whatsapp_test_number')

        if not test_number:
            return {
                "success": False,
                "message": "WhatsApp test number not configured"
            }

        # Enviar mensaje de prueba
        client.send_message(test_number, "✅ Conexión exitosa con WhatsApp Business API desde Nexo ERP!")

        return {
            "success": True,
            "message": "WhatsApp test message sent successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
