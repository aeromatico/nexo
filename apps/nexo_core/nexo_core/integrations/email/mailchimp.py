"""
Integración con Mailchimp para email marketing

Servicio de listas de correo y campañas de marketing
"""

import frappe
from frappe import _
import requests
import hashlib


class MailchimpClient:
    """Client para Mailchimp email marketing"""

    def __init__(self):
        self.api_key = self._get_config('mailchimp_api_key')
        self.base_url = "https://{}.api.mailchimp.com/3.0".format(
            self.api_key.split('-')[-1] if self.api_key else 'us1'
        )

        if not self.api_key:
            frappe.throw(_("Mailchimp configuration not found"))

    def _get_config(self, key):
        """Obtiene configuración"""
        try:
            config = frappe.get_single('Integration Config')
            return config.get(key)
        except frappe.DoesNotExistError:
            return None

    def _get_headers(self):
        """Headers para solicitudes a Mailchimp"""
        import base64
        auth_str = base64.b64encode(f"any:{self.api_key}".encode()).decode()
        return {
            "Authorization": f"Basic {auth_str}",
            "Content-Type": "application/json"
        }

    def add_subscriber(self, list_id, email, first_name=None, last_name=None, status='subscribed'):
        """
        Agrega suscriptor a lista

        Args:
            list_id: ID de lista Mailchimp
            email: Email del suscriptor
            first_name: Nombre
            last_name: Apellido
            status: Estado (subscribed, unsubscribed, cleaned, pending)

        Returns:
            dict: Resultado
        """
        url = f"{self.base_url}/lists/{list_id}/members"

        # Hash MD5 del email para identificar miembro
        subscriber_hash = hashlib.md5(email.lower().encode()).hexdigest()
        url = f"{self.base_url}/lists/{list_id}/members/{subscriber_hash}"

        payload = {
            "email_address": email,
            "status": status,
            "merge_fields": {
                "FNAME": first_name or "",
                "LNAME": last_name or ""
            }
        }

        try:
            response = requests.put(url, json=payload, headers=self._get_headers(), timeout=10)

            if response.status_code in [200, 201]:
                return {'success': True, 'message': 'Subscriber added'}
            else:
                frappe.log_error(f"Mailchimp Error: {response.text}", "Mailchimp Add Failed")
                return {'success': False, 'error': response.text}

        except requests.RequestException as e:
            frappe.log_error(str(e), "Mailchimp Connection Error")
            return {'success': False, 'error': str(e)}

    def create_campaign(self, list_id, campaign_name, subject, html_content):
        """
        Crea campaña en Mailchimp

        Args:
            list_id: ID de lista
            campaign_name: Nombre de campaña
            subject: Asunto
            html_content: Contenido HTML

        Returns:
            dict: ID de campaña
        """
        # Primero crear campaña
        url = f"{self.base_url}/campaigns"

        payload = {
            "type": "regular",
            "recipients": {
                "list_id": list_id
            },
            "settings": {
                "subject_line": subject,
                "title": campaign_name,
                "from_name": "Nexo ERP",
                "reply_to": self._get_config('mailchimp_from_email')
            }
        }

        try:
            response = requests.post(url, json=payload, headers=self._get_headers(), timeout=10)

            if response.status_code == 201:
                campaign = response.json()
                campaign_id = campaign['id']

                # Agregar contenido
                content_url = f"{self.base_url}/campaigns/{campaign_id}/content"
                content_payload = {
                    "html": html_content
                }

                content_response = requests.put(
                    content_url,
                    json=content_payload,
                    headers=self._get_headers(),
                    timeout=10
                )

                if content_response.status_code == 200:
                    return {
                        'success': True,
                        'campaign_id': campaign_id,
                        'name': campaign_name
                    }
                else:
                    return {'success': False, 'error': 'Failed to add content'}
            else:
                return {'success': False, 'error': response.text}

        except requests.RequestException as e:
            frappe.log_error(str(e), "Mailchimp Campaign Error")
            return {'success': False, 'error': str(e)}

    def send_campaign(self, campaign_id):
        """
        Envía campaña

        Args:
            campaign_id: ID de campaña

        Returns:
            dict: Resultado
        """
        url = f"{self.base_url}/campaigns/{campaign_id}/actions/send"

        try:
            response = requests.post(url, headers=self._get_headers(), timeout=10)

            if response.status_code == 204:
                return {'success': True, 'message': 'Campaign sent'}
            else:
                return {'success': False, 'error': response.text}

        except requests.RequestException as e:
            frappe.log_error(str(e), "Mailchimp Send Error")
            return {'success': False, 'error': str(e)}

    def get_list_stats(self, list_id):
        """
        Obtiene estadísticas de lista

        Args:
            list_id: ID de lista

        Returns:
            dict: Estadísticas
        """
        url = f"{self.base_url}/lists/{list_id}"

        try:
            response = requests.get(url, headers=self._get_headers(), timeout=10)

            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'subscriber_count': data['stats']['member_count'],
                    'unsubscribe_count': data['stats']['unsubscribe_count'],
                    'name': data['name']
                }
            else:
                return {'success': False, 'error': response.text}

        except requests.RequestException as e:
            return {'success': False, 'error': str(e)}


@frappe.whitelist()
def subscribe_to_mailchimp(email, first_name=None, last_name=None):
    """
    API endpoint: Suscribe email a lista Mailchimp

    Args:
        email: Email
        first_name: Nombre
        last_name: Apellido

    Returns:
        dict: Resultado
    """
    try:
        config = frappe.get_single('Integration Config')
        list_id = config.get('mailchimp_list_id')

        if not list_id:
            return {'success': False, 'error': 'Mailchimp list ID not configured'}

        client = MailchimpClient()
        result = client.add_subscriber(list_id, email, first_name, last_name)
        return result
    except Exception as e:
        frappe.log_error(str(e), "Mailchimp Subscribe Error")
        return {'success': False, 'error': str(e)}


@frappe.whitelist()
def create_mailchimp_campaign(campaign_name, subject, html_content):
    """
    API endpoint: Crea campaña en Mailchimp

    Args:
        campaign_name: Nombre
        subject: Asunto
        html_content: HTML

    Returns:
        dict: ID de campaña
    """
    try:
        config = frappe.get_single('Integration Config')
        list_id = config.get('mailchimp_list_id')

        if not list_id:
            return {'success': False, 'error': 'Mailchimp list ID not configured'}

        client = MailchimpClient()
        result = client.create_campaign(list_id, campaign_name, subject, html_content)
        return result
    except Exception as e:
        frappe.log_error(str(e), "Mailchimp Campaign Error")
        return {'success': False, 'error': str(e)}
