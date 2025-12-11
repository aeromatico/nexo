"""
Integración con Chilexpress - Bolivia

Servicio de envíos y courier a nivel nacional
"""

import requests
import frappe
from frappe import _


class ChilexpressAPI:
    """API client para Chilexpress"""

    def __init__(self):
        self.base_url = "https://api.chilexpress.cl/v1"
        self.api_key = self._get_config('chilexpress_api_key')
        self.subscriber_id = self._get_config('chilexpress_subscriber_id')

        if not self.api_key or not self.subscriber_id:
            frappe.throw(_("Chilexpress configuration not found"))

    def _get_config(self, key):
        """Obtiene configuración"""
        try:
            config = frappe.get_single('Integration Config')
            return config.get(key)
        except frappe.DoesNotExistError:
            return None

    def calculate_shipping(self, origin_city, dest_city, weight_kg, dimensions=None):
        """
        Calcula costo de envío

        Args:
            origin_city: Código de ciudad origen (ej: LP para La Paz)
            dest_city: Código de ciudad destino
            weight_kg: Peso en kg
            dimensions: Dimensiones opcionales

        Returns:
            dict: Costo y tiempo de entrega
        """
        url = f"{self.base_url}/shipping/calculate"
        headers = {
            "Ocp-Apim-Subscription-Key": self.api_key,
            "Content-Type": "application/json"
        }

        payload = {
            "subscriberId": self.subscriber_id,
            "originCountyCode": origin_city,
            "destinationCountyCode": dest_city,
            "package": [{
                "weight": weight_kg,
                "height": dimensions.get('height', 10) if dimensions else 10,
                "width": dimensions.get('width', 10) if dimensions else 10,
                "length": dimensions.get('length', 10) if dimensions else 10
            }]
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                service = data['data']['courierServiceOptions'][0]
                return {
                    'success': True,
                    'cost': float(service['serviceValue']),
                    'delivery_time': int(service['deliveryTime']),
                    'currency': 'BOB'
                }
            else:
                frappe.log_error(f"Chilexpress Error: {response.text}", "Shipping Calc Failed")
                return {'success': False, 'error': response.text}

        except requests.RequestException as e:
            frappe.log_error(str(e), "Chilexpress Connection Error")
            return {'success': False, 'error': str(e)}

    def create_shipment(self, order_id):
        """
        Crea envío en Chilexpress

        Args:
            order_id: ID de la orden

        Returns:
            dict: Número de seguimiento
        """
        order = frappe.get_doc('Online Order', order_id)

        url = f"{self.base_url}/shipments"
        headers = {
            "Ocp-Apim-Subscription-Key": self.api_key,
            "Content-Type": "application/json"
        }

        payload = {
            "subscriberId": self.subscriber_id,
            "reference": order.name,
            "recipient": {
                "name": order.customer_name,
                "address": order.shipping_address,
                "phone": order.contact_phone,
                "city": order.shipping_city_code or "LP"
            },
            "package": {
                "weight": order.total_weight or 1,
                "height": 10,
                "width": 10,
                "length": 10
            }
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)

            if response.status_code == 201:
                data = response.json()
                tracking_number = data['data']['trackingNumber']

                # Actualizar orden
                order.tracking_number = tracking_number
                order.shipping_provider = 'Chilexpress'
                order.shipping_status = 'Picked Up'
                order.save()
                frappe.db.commit()

                # Log
                self._log_shipment(order_id, tracking_number, 'created')

                return {
                    'success': True,
                    'tracking_number': tracking_number,
                    'status': 'Picked Up'
                }
            else:
                frappe.log_error(f"Shipment Creation Error: {response.text}", "Chilexpress Failed")
                return {'success': False, 'error': response.text}

        except requests.RequestException as e:
            frappe.log_error(str(e), "Chilexpress Connection Error")
            return {'success': False, 'error': str(e)}

    def track_shipment(self, tracking_number):
        """
        Rastrea envío

        Args:
            tracking_number: Número de seguimiento

        Returns:
            dict: Estado del envío
        """
        url = f"{self.base_url}/shipments/track/{tracking_number}"
        headers = {"Ocp-Apim-Subscription-Key": self.api_key}

        try:
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'status': data['data']['status'],
                    'location': data['data'].get('currentLocation', ''),
                    'estimated_delivery': data['data'].get('estimatedDelivery', ''),
                    'last_update': data['data'].get('lastUpdate', '')
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
                'integration': 'Chilexpress',
                'status': status,
                'reference': order_id,
                'transaction_id': tracking_number
            }).insert(ignore_permissions=True)
            frappe.db.commit()
        except Exception as e:
            frappe.log_error(str(e), "Failed to log Chilexpress shipment")


@frappe.whitelist()
def calculate_shipping_cost(order_id):
    """
    API endpoint: Calcula costo de envío para orden

    Args:
        order_id: ID de la orden

    Returns:
        dict: Costo de envío
    """
    try:
        order = frappe.get_doc('Online Order', order_id)

        api = ChilexpressAPI()
        result = api.calculate_shipping(
            origin_city='LP',  # La Paz por defecto
            dest_city=order.shipping_city_code or 'LP',
            weight_kg=order.total_weight or 1
        )

        if result['success']:
            # Actualizar orden con costo de envío
            order.shipping_cost = result['cost']
            order.estimated_delivery_days = result['delivery_time']
            order.save()
            frappe.db.commit()

        return result
    except Exception as e:
        frappe.log_error(str(e), "Calculate Shipping Error")
        return {'success': False, 'error': str(e)}


@frappe.whitelist()
def create_chilexpress_shipment(order_id):
    """
    API endpoint: Crea envío en Chilexpress

    Args:
        order_id: ID de la orden

    Returns:
        dict: Resultado con número de tracking
    """
    try:
        api = ChilexpressAPI()
        result = api.create_shipment(order_id)
        return result
    except Exception as e:
        frappe.log_error(str(e), "Create Shipment Error")
        return {'success': False, 'error': str(e)}


@frappe.whitelist()
def track_chilexpress_shipment(tracking_number):
    """
    API endpoint: Rastrea envío de Chilexpress

    Args:
        tracking_number: Número de seguimiento

    Returns:
        dict: Estado del envío
    """
    try:
        api = ChilexpressAPI()
        result = api.track_shipment(tracking_number)
        return result
    except Exception as e:
        frappe.log_error(str(e), "Track Shipment Error")
        return {'success': False, 'error': str(e)}
