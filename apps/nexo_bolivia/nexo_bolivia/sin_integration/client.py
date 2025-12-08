"""
SIAT API Client
Cliente para comunicación con API del Sistema Integrado de Administración Tributaria

Documentation: https://siat.impuestos.gob.bo/
"""

import frappe
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from frappe import _


class SIATClient:
    """
    Cliente para interactuar con la API del SIAT (Sistema Integrado de Administración Tributaria)

    Maneja autenticación, envío de facturas, consultas y anulaciones
    """

    def __init__(self, company: Optional[str] = None):
        """
        Inicializa el cliente SIAT

        Args:
            company: Nombre de la empresa (Company doctype)
        """
        self.company = company or frappe.defaults.get_user_default('Company')
        self.base_url = self._get_config('sin_api_url') or 'https://pilotosiat.impuestos.gob.bo'
        self.nit = self._get_config('sin_nit')
        self.token = None
        self.token_expiry = None

    def _get_config(self, key: str) -> Optional[str]:
        """Obtiene configuración desde Company o Site Config"""
        # Primero intentar desde la empresa
        if self.company:
            company_doc = frappe.get_doc('Company', self.company)
            if hasattr(company_doc, key):
                return getattr(company_doc, key)

        # Si no, desde site config
        return frappe.conf.get(key)

    def _ensure_token(self):
        """Asegura que tengamos un token válido"""
        if not self.token or (self.token_expiry and datetime.now() >= self.token_expiry):
            self.authenticate()

    def authenticate(self) -> Dict[str, Any]:
        """
        Autentica con el SIAT y obtiene token de acceso

        Returns:
            Dict con información del token

        Raises:
            frappe.ValidationError: Si la autenticación falla
        """
        endpoint = f"{self.base_url}/api/v1/auth/login"

        # Obtener credenciales
        username = self._get_config('sin_username')
        password = self._get_config('sin_password')

        if not username or not password:
            frappe.throw(_("SIN credentials not configured. Please set sin_username and sin_password"))

        payload = {
            'nit': self.nit,
            'username': username,
            'password': password,
            'sistema': 'FACTURACION',
            'modalidad': self._get_config('sin_modalidad') or '1'  # 1=Electronica, 2=Computarizada
        }

        try:
            response = requests.post(endpoint, json=payload, timeout=30)
            response.raise_for_status()

            data = response.json()

            if data.get('transaccion') and data.get('codigo') == 200:
                self.token = data['respuesta']['token']
                # Token válido por 1 hora
                self.token_expiry = datetime.now() + timedelta(hours=1)

                frappe.logger().info(f"SIAT authentication successful for NIT {self.nit}")

                return {
                    'success': True,
                    'token': self.token,
                    'expiry': self.token_expiry
                }
            else:
                error_msg = data.get('mensaje', 'Authentication failed')
                frappe.throw(_("SIAT authentication failed: {0}").format(error_msg))

        except requests.exceptions.RequestException as e:
            frappe.log_error(f"SIAT connection error: {str(e)}", "SIAT Client Error")
            frappe.throw(_("Could not connect to SIAT: {0}").format(str(e)))

    def send_invoice(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Envía una factura al SIAT

        Args:
            invoice_data: Datos de la factura en formato SIAT

        Returns:
            Dict con respuesta del SIAT incluyendo CUF y estado
        """
        self._ensure_token()

        endpoint = f"{self.base_url}/api/v1/factura/emision"

        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(endpoint, json=invoice_data, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json()

            if data.get('transaccion') and data.get('codigo') == 200:
                frappe.logger().info(f"Invoice sent successfully: {invoice_data.get('codigoDocumentoSector')}")
                return {
                    'success': True,
                    'cuf': data['respuesta']['cuf'],
                    'cuf_qr': data['respuesta'].get('cufQr'),
                    'estado': data['respuesta'].get('estado', 'VALIDA'),
                    'mensaje': data.get('mensaje', 'Factura registrada correctamente'),
                    'fecha_recepcion': data['respuesta'].get('fechaRecepcion')
                }
            else:
                return {
                    'success': False,
                    'error': data.get('mensaje', 'Error desconocido'),
                    'codigo': data.get('codigo')
                }

        except requests.exceptions.RequestException as e:
            frappe.log_error(f"Error sending invoice to SIAT: {str(e)}", "SIAT Send Invoice Error")
            return {
                'success': False,
                'error': str(e),
                'offline_mode': True
            }

    def verify_invoice(self, cuf: str) -> Dict[str, Any]:
        """
        Verifica el estado de una factura en el SIAT

        Args:
            cuf: Código Único de Factura

        Returns:
            Dict con estado de la factura
        """
        self._ensure_token()

        endpoint = f"{self.base_url}/api/v1/factura/verificar"

        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }

        payload = {
            'cuf': cuf,
            'nit': self.nit
        }

        try:
            response = requests.post(endpoint, json=payload, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json()

            if data.get('transaccion'):
                return {
                    'success': True,
                    'estado': data['respuesta'].get('estado'),
                    'valida': data['respuesta'].get('valida'),
                    'mensaje': data.get('mensaje')
                }
            else:
                return {
                    'success': False,
                    'error': data.get('mensaje')
                }

        except requests.exceptions.RequestException as e:
            frappe.log_error(f"Error verifying invoice: {str(e)}", "SIAT Verify Error")
            return {
                'success': False,
                'error': str(e)
            }

    def cancel_invoice(self, cuf: str, reason_code: int, reason: str) -> Dict[str, Any]:
        """
        Anula una factura en el SIAT

        Args:
            cuf: Código Único de Factura
            reason_code: Código del motivo (1-3)
            reason: Descripción del motivo

        Returns:
            Dict con resultado de la anulación
        """
        self._ensure_token()

        endpoint = f"{self.base_url}/api/v1/factura/anular"

        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }

        payload = {
            'cuf': cuf,
            'nit': self.nit,
            'codigoMotivo': reason_code,
            'motivo': reason
        }

        try:
            response = requests.post(endpoint, json=payload, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json()

            if data.get('transaccion'):
                frappe.logger().info(f"Invoice cancelled successfully: {cuf}")
                return {
                    'success': True,
                    'estado': 'ANULADA',
                    'mensaje': data.get('mensaje'),
                    'fecha_anulacion': data['respuesta'].get('fechaAnulacion')
                }
            else:
                return {
                    'success': False,
                    'error': data.get('mensaje')
                }

        except requests.exceptions.RequestException as e:
            frappe.log_error(f"Error cancelling invoice: {str(e)}", "SIAT Cancel Error")
            return {
                'success': False,
                'error': str(e)
            }

    def get_parametrics(self, parametric_type: str) -> Dict[str, Any]:
        """
        Obtiene parámetros desde SIAT (tipos de documentos, actividades económicas, etc.)

        Args:
            parametric_type: Tipo de parámetro a consultar
                - actividades_economicas
                - tipos_documento_identidad
                - tipos_documento_sector
                - tipos_emision
                - tipos_factura
                - tipos_metodo_pago
                - tipos_moneda
                - unidades_medida

        Returns:
            Dict con lista de parámetros
        """
        self._ensure_token()

        endpoint = f"{self.base_url}/api/v1/parametros/{parametric_type}"

        headers = {
            'Authorization': f'Bearer {self.token}'
        }

        try:
            response = requests.get(endpoint, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json()

            if data.get('transaccion'):
                return {
                    'success': True,
                    'data': data['respuesta']
                }
            else:
                return {
                    'success': False,
                    'error': data.get('mensaje')
                }

        except requests.exceptions.RequestException as e:
            frappe.log_error(f"Error getting parametrics: {str(e)}", "SIAT Parametrics Error")
            return {
                'success': False,
                'error': str(e)
            }

    def test_connection(self) -> Dict[str, Any]:
        """
        Prueba la conexión con el SIAT

        Returns:
            Dict con resultado de la prueba
        """
        try:
            result = self.authenticate()
            if result.get('success'):
                return {
                    'success': True,
                    'message': 'Conexión exitosa con SIAT',
                    'url': self.base_url,
                    'nit': self.nit
                }
            else:
                return {
                    'success': False,
                    'message': 'Falló la autenticación con SIAT'
                }
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }


@frappe.whitelist()
def test_siat_connection(company: str = None) -> Dict[str, Any]:
    """
    API endpoint para probar conexión SIAT

    Args:
        company: Nombre de la empresa

    Returns:
        Dict con resultado de la prueba
    """
    client = SIATClient(company)
    return client.test_connection()


@frappe.whitelist()
def get_siat_parametrics(parametric_type: str, company: str = None) -> Dict[str, Any]:
    """
    API endpoint para obtener parámetros SIAT

    Args:
        parametric_type: Tipo de parámetro
        company: Nombre de la empresa

    Returns:
        Dict con parámetros
    """
    client = SIATClient(company)
    return client.get_parametrics(parametric_type)
