"""
Integración con SendGrid para email marketing

Servicio de envío de emails y campañas automáticas
"""

import frappe
from frappe import _
import requests
import json


class SendGridClient:
    """Client para SendGrid email marketing"""

    def __init__(self):
        self.api_key = self._get_config('sendgrid_api_key')
        self.base_url = "https://api.sendgrid.com/v3"
        self.from_email = self._get_config('sendgrid_from_email')

        if not self.api_key:
            frappe.throw(_("SendGrid configuration not found"))

    def _get_config(self, key):
        """Obtiene configuración"""
        try:
            config = frappe.get_single('Integration Config')
            return config.get(key)
        except frappe.DoesNotExistError:
            return None

    def send_email(self, to_email, subject, html_content, plain_text=None):
        """
        Envía email via SendGrid

        Args:
            to_email: Email destino
            subject: Asunto
            html_content: Contenido HTML
            plain_text: Contenido texto plano (opcional)

        Returns:
            dict: Resultado
        """
        url = f"{self.base_url}/mail/send"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "personalizations": [{
                "to": [{"email": to_email}],
                "subject": subject
            }],
            "from": {"email": self.from_email},
            "content": [
                {"type": "text/html", "value": html_content}
            ]
        }

        if plain_text:
            payload["content"].insert(0, {"type": "text/plain", "value": plain_text})

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)

            if response.status_code == 202:
                self._log_email('sent', to_email, subject)
                return {'success': True, 'message': 'Email sent'}
            else:
                frappe.log_error(f"SendGrid Error: {response.text}", "SendGrid Send Failed")
                return {'success': False, 'error': response.text}

        except requests.RequestException as e:
            frappe.log_error(str(e), "SendGrid Connection Error")
            return {'success': False, 'error': str(e)}

    def create_contact_list(self, list_name):
        """
        Crea lista de contactos en SendGrid

        Args:
            list_name: Nombre de la lista

        Returns:
            dict: ID de la lista
        """
        url = f"{self.base_url}/marketing/lists"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {"name": list_name}

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)

            if response.status_code == 201:
                data = response.json()
                return {
                    'success': True,
                    'list_id': data['id'],
                    'name': data['name']
                }
            else:
                return {'success': False, 'error': response.text}

        except requests.RequestException as e:
            return {'success': False, 'error': str(e)}

    def add_to_list(self, list_id, email, first_name=None, last_name=None):
        """
        Agrega contacto a lista

        Args:
            list_id: ID de la lista
            email: Email del contacto
            first_name: Nombre
            last_name: Apellido

        Returns:
            dict: Resultado
        """
        url = f"{self.base_url}/marketing/contacts"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "contacts": [{
                "email": email,
                "first_name": first_name,
                "last_name": last_name
            }],
            "list_ids": [list_id]
        }

        try:
            response = requests.put(url, json=payload, headers=headers, timeout=10)

            if response.status_code == 202:
                return {'success': True}
            else:
                return {'success': False, 'error': response.text}

        except requests.RequestException as e:
            return {'success': False, 'error': str(e)}

    def create_campaign(self, campaign_name, subject, html_content, list_id):
        """
        Crea campaña de email

        Args:
            campaign_name: Nombre de campaña
            subject: Asunto
            html_content: HTML
            list_id: ID de lista destino

        Returns:
            dict: ID de campaña
        """
        url = f"{self.base_url}/marketing/campaigns"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "name": campaign_name,
            "subject": subject,
            "sender_id": 1,
            "list_ids": [list_id],
            "html_content": html_content
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)

            if response.status_code == 201:
                data = response.json()
                return {
                    'success': True,
                    'campaign_id': data['id'],
                    'name': data['name']
                }
            else:
                return {'success': False, 'error': response.text}

        except requests.RequestException as e:
            return {'success': False, 'error': str(e)}

    def _log_email(self, status, to_email, subject):
        """Registra email en log"""
        try:
            frappe.get_doc({
                'doctype': 'Integration Log',
                'integration': 'SendGrid',
                'status': status,
                'reference': to_email,
                'content': subject
            }).insert(ignore_permissions=True)
            frappe.db.commit()
        except Exception as e:
            frappe.log_error(str(e), "Failed to log SendGrid email")


@frappe.whitelist()
def send_sendgrid_email(to_email, subject, html_content):
    """
    API endpoint: Envía email via SendGrid

    Args:
        to_email: Email destino
        subject: Asunto
        html_content: Contenido HTML

    Returns:
        dict: Resultado
    """
    try:
        client = SendGridClient()
        result = client.send_email(to_email, subject, html_content)
        return result
    except Exception as e:
        frappe.log_error(str(e), "SendGrid Send Error")
        return {'success': False, 'error': str(e)}


@frappe.whitelist()
def create_sendgrid_campaign(campaign_name, subject, html_content, list_id):
    """
    API endpoint: Crea campaña en SendGrid

    Args:
        campaign_name: Nombre
        subject: Asunto
        html_content: HTML
        list_id: ID de lista

    Returns:
        dict: ID de campaña
    """
    try:
        client = SendGridClient()
        result = client.create_campaign(campaign_name, subject, html_content, list_id)
        return result
    except Exception as e:
        frappe.log_error(str(e), "SendGrid Campaign Error")
        return {'success': False, 'error': str(e)}
