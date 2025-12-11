"""
Integración con BlueExpress - Bolivia

Servicio de envíos nacional e internacional
"""

import requests
import frappe
from frappe import _


class BlueExpressAPI:
    """API client para BlueExpress"""

    def __init__(self):
        self.base_url = "https://api.blueexpress.bo"
        self.api_key = self._get_config('blueexpress_api_key')
        self.account_number = self._get_config('blueexpress_account_number')

        if not self.api_key or not self.account_number:
            frappe.throw(_("BlueExpress configuration not found"))

    def _get_config(self, key):
        """Obtiene configuración"""
        try:
            config = frappe.get_single('Integration Config')
            return config.get(key)
        except frappe.DoesNotExistError:
            return None

    def calculate_shipping(self, origin_zip, dest_zip, weight_kg):
        """
        Calcula costo de envío

        Args:
            origin_zip: Código postal origen
            dest_zip: Código postal destino
            weight_kg: Peso en kg

        Returns:
            dict: Costo y tiempo de entrega
        """
        url = f"{self.base_url}/v1/rates"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "origin_zip": origin_zip,
            "destination_zip": dest_zip,
            "weight": weight_kg,
            "service": "standard"
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'cost': float(data['rate']),
                    'delivery_days': int(data['days']),
                    'currency': 'BOB'
                }
            else:
                frappe.log_error(f"BlueExpress Error: {response.text}", "BlueExpress Calc Failed")
                return {'success': False, 'error': response.text}

        except requests.RequestException as e:
            frappe.log_error(str(e), "BlueExpress Connection Error")
            return {'success': False, 'error': str(e)}

    def create_shipment(self, order_id):
        """
        Crea envío en BlueExpress

        Args:
            order_id: ID de la orden

        Returns:
            dict: Número de seguimiento
        """
        order = frappe.get_doc('Online Order', order_id)

        url = f"{self.base_url}/v1/shipments"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "account": self.account_number,
            "reference": order.name,
            "shipper": {
                "name": "Nexo ERP",
                "address": "Empresa address",
                "city": "La Paz",
                "zip": "LP"
            },
            "recipient": {
                "name": order.customer_name,
                "address": order.shipping_address,
                "city": order.shipping_city or "La Paz",
                "zip": order.shipping_city_code or "LP",
                "phone": order.contact_phone
            },
            "package": {
                "weight": order.total_weight or 1,
                "length": 10,
                "width": 10,
                "height": 10,
                "description": f"Order {order.name}"
            }
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)

            if response.status_code == 201:
                data = response.json()
                tracking_number = data['tracking_number']

                # Actualizar orden
                order.tracking_number = tracking_number
                order.shipping_provider = 'BlueExpress'
                order.shipping_status = 'In Transit'
                order.save()
                frappe.db.commit()

                # Log
                self._log_shipment(order_id, tracking_number, 'created')

                return {
                    'success': True,
                    'tracking_number': tracking_number,
                    'status': 'In Transit'
                }
            else:
                frappe.log_error(f"Shipment Error: {response.text}", "BlueExpress Failed")
                return {'success': False, 'error': response.text}

        except requests.RequestException as e:
            frappe.log_error(str(e), "BlueExpress Connection Error")
            return {'success': False, 'error': str(e)}

    def track_shipment(self, tracking_number):
        """
        Rastrea envío

        Args:
            tracking_number: Número de seguimiento

        Returns:
            dict: Estado del envío
        """
        url = f"{self.base_url}/v1/tracking/{tracking_number}"
        headers = {"Authorization": f"Bearer {self.api_key}"}

        try:
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'status': data['status'],
                    'current_location': data.get('location', ''),
                    'estimated_delivery': data.get('eta', ''),
                    'events': data.get('events', [])
                }
            else:
                return {'success': False, 'error': response.text}

        except requests.RequestException as e:
            return {'success': False, 'error': str(e)}

    def generate_label(self, tracking_number):
        """
        Genera etiqueta de envío

        Args:
            tracking_number: Número de seguimiento

        Returns:
            dict: PDF label en base64
        """
        url = f"{self.base_url}/v1/labels/{tracking_number}"
        headers = {"Authorization": f"Bearer {self.api_key}"}

        try:
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                return {
                    'success': True,
                    'label': response.content.hex(),
                    'format': 'PDF'
                }
            else:
                return {'success': False, 'error': response.text}

        except requests.RequestException as e:
            return {'success': False, 'error': str(e)}

    def _log_shipment(self, order_id, tracking_number, status):
        """Registra envío en log"""
        try:
            frappe.get_doc({
                'doctype': 'Integration Log',
                'integration': 'BlueExpress',
                'status': status,
                'reference': order_id,
                'transaction_id': tracking_number
            }).insert(ignore_permissions=True)
            frappe.db.commit()
        except Exception as e:
            frappe.log_error(str(e), "Failed to log BlueExpress shipment")


@frappe.whitelist()
def create_blueexpress_shipment(order_id):
    """
    API endpoint: Crea envío en BlueExpress

    Args:
        order_id: ID de la orden

    Returns:
        dict: Resultado con número de tracking
    """
    try:
        api = BlueExpressAPI()
        result = api.create_shipment(order_id)
        return result
    except Exception as e:
        frappe.log_error(str(e), "BlueExpress Shipment Error")
        return {'success': False, 'error': str(e)}


@frappe.whitelist()
def track_blueexpress_shipment(tracking_number):
    """
    API endpoint: Rastrea envío de BlueExpress

    Args:
        tracking_number: Número de seguimiento

    Returns:
        dict: Estado del envío
    """
    try:
        api = BlueExpressAPI()
        result = api.track_shipment(tracking_number)
        return result
    except Exception as e:
        frappe.log_error(str(e), "BlueExpress Tracking Error")
        return {'success': False, 'error': str(e)}


@frappe.whitelist()
def get_blueexpress_label(tracking_number):
    """
    API endpoint: Obtiene etiqueta de envío

    Args:
        tracking_number: Número de seguimiento

    Returns:
        dict: Etiqueta en base64
    """
    try:
        api = BlueExpressAPI()
        result = api.generate_label(tracking_number)
        return result
    except Exception as e:
        frappe.log_error(str(e), "BlueExpress Label Error")
        return {'success': False, 'error': str(e)}
