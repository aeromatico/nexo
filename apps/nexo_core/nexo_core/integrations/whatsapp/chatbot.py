"""
Chatbot básico para WhatsApp

Proporciona respuestas automáticas y manejo de consultas comunes
"""

import frappe
from frappe import _
import re


class WhatsAppChatbot:
    """Chatbot básico para WhatsApp"""

    def __init__(self):
        self.intents = {
            'order_status': self._handle_order_status,
            'invoice_inquiry': self._handle_invoice_inquiry,
            'product_info': self._handle_product_info,
            'support': self._handle_support,
            'help': self._handle_help
        }

    def process_message(self, from_number, message):
        """
        Procesa mensaje recibido del chatbot

        Args:
            from_number: Número que envió el mensaje
            message: Contenido del mensaje

        Returns:
            str: Respuesta del chatbot
        """
        # Detectar intención
        intent = self._detect_intent(message)

        # Procesar según intención
        if intent:
            handler = self.intents.get(intent)
            if handler:
                return handler(message, from_number)

        # Respuesta por defecto
        return self._handle_help()

    def _detect_intent(self, message):
        """
        Detecta la intención del mensaje

        Args:
            message: Mensaje del usuario

        Returns:
            str: Intención detectada
        """
        message_lower = message.lower()

        # Palabras clave para cada intención
        if any(word in message_lower for word in ['pedido', 'orden', 'seguimiento', 'tracking']):
            return 'order_status'
        elif any(word in message_lower for word in ['factura', 'invoice', 'recibo']):
            return 'invoice_inquiry'
        elif any(word in message_lower for word in ['producto', 'item', 'disponible', 'precio']):
            return 'product_info'
        elif any(word in message_lower for word in ['soporte', 'ayuda', 'problema', 'error']):
            return 'support'
        elif any(word in message_lower for word in ['hola', 'hi', 'help', 'menú']):
            return 'help'

        return None

    def _handle_order_status(self, message, from_number):
        """
        Maneja consultas de estado de pedidos

        Args:
            message: Mensaje del usuario
            from_number: Número del usuario

        Returns:
            str: Respuesta
        """
        try:
            # Extraer número de pedido si está incluido
            order_match = re.search(r'#?(\d{4,})', message)

            if order_match:
                order_id = order_match.group(1)
                # Buscar el pedido
                order = frappe.db.get_value('Online Order',
                                             filters={'name': order_id},
                                             fieldname=['status', 'tracking_number', 'shipping_provider'])

                if order:
                    status, tracking, provider = order
                    return f"""
Tu pedido #{order_id} está en estado: {status}

Envío: {provider or 'Pendiente'}
Tracking: {tracking or 'No disponible'}

¿Necesitas más información?
                    """.strip()

            return """
Por favor, proporciona el número de tu pedido.
Ejemplo: Mi pedido es #12345

¿O quieres ver otros opciones?
Escribe: menu
                    """.strip()

        except Exception as e:
            frappe.log_error(str(e), "Chatbot Order Status Error")
            return "Lo siento, no pude procesar tu solicitud. Por favor, contáctanos."

    def _handle_invoice_inquiry(self, message, from_number):
        """
        Maneja consultas sobre facturas

        Args:
            message: Mensaje del usuario
            from_number: Número del usuario

        Returns:
            str: Respuesta
        """
        return """
Para consultar una factura, necesitamos el número.
Ejemplo: "Factura SAI-2024-001"

O puedes contactar a nuestro soporte:
📞 support@nexo.bo

¿Qué más necesitas?
        """.strip()

    def _handle_product_info(self, message, from_number):
        """
        Maneja consultas sobre productos

        Args:
            message: Mensaje del usuario
            from_number: Número del usuario

        Returns:
            str: Respuesta
        """
        return """
Para consultar información de productos, visita:
🛒 https://nexo.bo/tienda

O describe lo que buscas y te ayudaremos.

¿Tienes algún producto específico en mente?
        """.strip()

    def _handle_support(self, message, from_number):
        """
        Maneja solicitudes de soporte

        Args:
            message: Mensaje del usuario
            from_number: Número del usuario

        Returns:
            str: Respuesta
        """
        try:
            # Crear ticket de soporte
            support_ticket = frappe.get_doc({
                'doctype': 'Support Ticket',
                'customer_whatsapp': from_number,
                'issue_title': message[:100],
                'issue_details': message,
                'status': 'Open'
            }).insert()

            return f"""
Hemos recibido tu solicitud de soporte.

Ticket de soporte: {support_ticket.name}

Un agente se comunicará contigo pronto.

¿Hay algo más en lo que podamos ayudarte?
            """.strip()

        except Exception as e:
            frappe.log_error(str(e), "Chatbot Support Error")
            return """
Lo siento, hubo un error. Por favor contáctanos directamente:
📧 support@nexo.bo
📞 +591 XXX XXXX
            """.strip()

    def _handle_help(self):
        """
        Maneja solicitudes de ayuda general

        Returns:
            str: Menú de ayuda
        """
        return """
¡Hola! Soy el asistente de Nexo ERP.

¿En qué puedo ayudarte?

1️⃣ Estado de mi pedido
2️⃣ Consulta de factura
3️⃣ Información de productos
4️⃣ Soporte técnico
5️⃣ Promociones

Escribe el número o describe qué necesitas.

¿En qué te puedo ayudar?
        """.strip()


@frappe.whitelist(allow_guest=True)
def handle_whatsapp_message(from_number, message_body):
    """
    Webhook para manejar mensajes recibidos en WhatsApp

    Args:
        from_number: Número que envió el mensaje
        message_body: Contenido del mensaje

    Returns:
        dict: Confirmación de recepción
    """
    try:
        chatbot = WhatsAppChatbot()
        response = chatbot.process_message(from_number, message_body)

        # Registrar mensaje
        frappe.get_doc({
            'doctype': 'Integration Log',
            'integration': 'WhatsApp Chatbot',
            'status': 'received',
            'reference': from_number,
            'content': message_body
        }).insert(ignore_permissions=True)

        # Enviar respuesta
        from nexo_core.integrations.whatsapp.client import WhatsAppClient
        client = WhatsAppClient()
        client.send_message(from_number, response)

        frappe.db.commit()

        return {
            'success': True,
            'message': 'Message processed'
        }

    except Exception as e:
        frappe.log_error(str(e), "WhatsApp Chatbot Error")
        return {
            'success': False,
            'error': str(e)
        }


def setup_chatbot_webhooks():
    """
    Configura los webhooks para recibir mensajes en WhatsApp

    Debe configurarse en el panel de WhatsApp Business
    """
    config = frappe.get_single('Integration Config')

    # URL del webhook
    webhook_url = f"{frappe.utils.get_url()}/api/method/nexo_core.integrations.whatsapp.chatbot.handle_whatsapp_message"

    frappe.msgprint(f"""
Configura este webhook en tu cuenta de WhatsApp Business:

URL: {webhook_url}
Webhook Token: {config.get('whatsapp_webhook_token')}

Events a suscribirse: messages
    """)

    return {'webhook_url': webhook_url}
