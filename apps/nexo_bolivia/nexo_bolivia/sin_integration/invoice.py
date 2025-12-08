"""
Electronic Invoice Module
Generación y gestión de facturas electrónicas para SIAT
"""

import frappe
import hashlib
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from frappe import _
from .client import SIATClient
from .qr import generate_invoice_qr


class ElectronicInvoice:
    """
    Clase para gestionar facturas electrónicas del SIAT

    Maneja la conversión de Sales Invoice de ERPNext al formato SIAT
    """

    def __init__(self, sales_invoice: str):
        """
        Inicializa con una Sales Invoice de ERPNext

        Args:
            sales_invoice: Nombre del documento Sales Invoice
        """
        self.doc = frappe.get_doc('Sales Invoice', sales_invoice)
        self.company_doc = frappe.get_doc('Company', self.doc.company)
        self.client = SIATClient(self.doc.company)

    def generate_cuf(self) -> str:
        """
        Genera el Código Único de Factura (CUF)

        El CUF es un identificador único de 44 caracteres alfanuméricos
        generado según especificaciones del SIAT

        Returns:
            String CUF de 44 caracteres
        """
        # Componentes del CUF según SIAT
        nit = self.client.nit or '0'
        fecha = datetime.now().strftime('%Y%m%d%H%M%S')
        sucursal = self._get_config('sin_sucursal', '0')
        modalidad = self._get_config('sin_modalidad', '1')
        tipo_emision = self._get_config('sin_tipo_emision', '1')
        codigo_documento = self._get_config('sin_codigo_documento', '1')
        tipo_factura = self._get_config('sin_tipo_factura', '1')
        punto_venta = self._get_config('sin_punto_venta', '0')

        # Número de factura
        numero = str(self.doc.name).replace('/', '').replace('-', '')[-10:].zfill(10)

        # Base para hash
        base_string = f"{nit}{fecha}{sucursal}{modalidad}{tipo_emision}{codigo_documento}{numero}{punto_venta}"

        # Generar hash SHA256 y tomar primeros 8 caracteres
        hash_obj = hashlib.sha256(base_string.encode())
        hash_hex = hash_obj.hexdigest()[:8].upper()

        # Construir CUF completo
        cuf = f"{nit}{fecha}{sucursal}{modalidad}{tipo_emision}{codigo_documento}{numero}{punto_venta}{hash_hex}"

        # Asegurar 44 caracteres (pad si es necesario)
        cuf = cuf[:44].ljust(44, '0')

        return cuf

    def _get_config(self, key: str, default: Any = None) -> Any:
        """Obtiene configuración desde la empresa"""
        return getattr(self.company_doc, key, None) or frappe.conf.get(key, default)

    def generate_invoice_data(self) -> Dict[str, Any]:
        """
        Genera la estructura de datos de factura en formato SIAT

        Returns:
            Dict con estructura completa de factura para SIAT
        """
        cuf = self.generate_cuf()

        invoice_data = {
            # Cabecera
            'nitEmisor': self.client.nit,
            'razonSocialEmisor': self.company_doc.company_name,
            'municipio': self._get_config('sin_municipio', 'La Paz'),
            'telefono': self.company_doc.phone or '',
            'numeroFactura': str(self.doc.name),
            'cuf': cuf,
            'cufd': self._get_config('sin_cufd', ''),  # Código Único de Factura Diaria
            'codigoSucursal': int(self._get_config('sin_sucursal', 0)),
            'direccion': self.company_doc.address or '',
            'codigoPuntoVenta': int(self._get_config('sin_punto_venta', 0)),

            # Fecha y hora
            'fechaEmision': self.doc.posting_date.strftime('%Y-%m-%d') if self.doc.posting_date else datetime.now().strftime('%Y-%m-%d'),
            'nombreRazonSocial': self.doc.customer_name,
            'codigoTipoDocumentoIdentidad': self._get_document_type(),
            'numeroDocumento': self._get_customer_nit(),
            'complemento': self._get_customer_complement(),

            # Cliente
            'codigoCliente': self.doc.customer,
            'codigoMetodoPago': self._get_payment_method_code(),
            'numeroTarjeta': None,
            'montoTotal': float(self.doc.grand_total),
            'montoTotalSujetoIva': float(self.doc.net_total),
            'codigoMoneda': 1,  # 1 = BOB (Bolivianos)
            'tipoCambio': 1,

            # Datos adicionales
            'montoGiftCard': None,
            'descuentoAdicional': float(self.doc.discount_amount or 0),
            'codigoExcepcion': self._get_exception_code(),
            'cafc': None,  # Código de Autorización de Facturas por Contingencia

            # Leyenda
            'leyenda': self._get_leyenda(),

            # Usuario
            'usuario': frappe.session.user,

            # Tipo de documento
            'codigoDocumentoSector': int(self._get_config('sin_codigo_documento', 1)),

            # Detalle de items
            'detalle': self._generate_items_detail()
        }

        return invoice_data

    def _get_document_type(self) -> int:
        """
        Obtiene el código de tipo de documento de identidad

        Returns:
            Código SIAT: 1=CI, 2=CEX, 3=PAS, 4=OD, 5=NIT
        """
        customer = frappe.get_doc('Customer', self.doc.customer)
        doc_type = getattr(customer, 'tipo_documento_identidad', 'NIT')

        type_mapping = {
            'CI': 1,
            'CEX': 2,
            'PAS': 3,
            'OD': 4,
            'NIT': 5
        }

        return type_mapping.get(doc_type, 5)  # Default NIT

    def _get_customer_nit(self) -> str:
        """Obtiene el NIT del cliente"""
        customer = frappe.get_doc('Customer', self.doc.customer)
        return getattr(customer, 'tax_id', None) or '0'

    def _get_customer_complement(self) -> Optional[str]:
        """Obtiene el complemento del NIT/CI"""
        customer = frappe.get_doc('Customer', self.doc.customer)
        return getattr(customer, 'tax_id_complement', None)

    def _get_payment_method_code(self) -> int:
        """
        Obtiene el código de método de pago

        Returns:
            Código SIAT: 1=Efectivo, 2=Tarjeta, 3=Cheque, etc.
        """
        # Mapeo básico de modos de pago
        if self.doc.mode_of_payment:
            mode_lower = self.doc.mode_of_payment.lower()
            if 'efectivo' in mode_lower or 'cash' in mode_lower:
                return 1
            elif 'tarjeta' in mode_lower or 'card' in mode_lower:
                return 2
            elif 'cheque' in mode_lower or 'check' in mode_lower:
                return 3
            elif 'transferencia' in mode_lower or 'transfer' in mode_lower:
                return 4

        return 1  # Default: Efectivo

    def _get_exception_code(self) -> Optional[int]:
        """Obtiene código de excepción si aplica"""
        # 1 = Factura fuera de línea por contingencia
        # TODO: Implementar lógica de contingencia
        return None

    def _get_leyenda(self) -> str:
        """
        Genera la leyenda obligatoria de la factura

        Returns:
            Leyenda según actividad económica
        """
        # Leyenda por defecto
        return "Ley N° 453: Tienes derecho a un trato equitativo y a la reparación e indemnización por daños y perjuicios, en caso corresponda."

    def _generate_items_detail(self) -> List[Dict[str, Any]]:
        """
        Genera el detalle de items de la factura

        Returns:
            Lista de items en formato SIAT
        """
        detalle = []

        for idx, item in enumerate(self.doc.items, start=1):
            detalle_item = {
                'actividadEconomica': self._get_config('sin_actividad_economica', '620100'),
                'codigoProductoSin': self._get_sin_product_code(item),
                'codigoProducto': item.item_code,
                'descripcion': item.item_name or item.description,
                'cantidad': float(item.qty),
                'unidadMedida': self._get_unit_measure(item),
                'precioUnitario': float(item.rate),
                'montoDescuento': float(item.discount_amount or 0),
                'subTotal': float(item.amount),
                'numeroSerie': None,
                'numeroImei': None
            }

            detalle.append(detalle_item)

        return detalle

    def _get_sin_product_code(self, item) -> str:
        """
        Obtiene el código de producto según catálogo SIN

        Args:
            item: Item de la factura

        Returns:
            Código SIN del producto (default: 99100 = Otros servicios)
        """
        # TODO: Implementar mapeo de items a códigos SIN
        # Por ahora retornar código genérico
        return '99100'

    def _get_unit_measure(self, item) -> int:
        """
        Obtiene el código de unidad de medida SIN

        Args:
            item: Item de la factura

        Returns:
            Código SIAT de unidad de medida
        """
        # Mapeo básico de UOM a códigos SIAT
        uom_mapping = {
            'Nos': 1,  # Unidad
            'Kg': 2,   # Kilogramo
            'Mt': 3,   # Metro
            'Lt': 4,   # Litro
            'Pza': 1,  # Pieza = Unidad
            'Set': 1,  # Set = Unidad
            'Box': 1,  # Caja = Unidad
        }

        uom = item.uom or 'Nos'
        return uom_mapping.get(uom, 1)  # Default: Unidad

    def send_to_siat(self) -> Dict[str, Any]:
        """
        Envía la factura al SIAT

        Returns:
            Dict con resultado del envío incluyendo CUF
        """
        try:
            invoice_data = self.generate_invoice_data()
            result = self.client.send_invoice(invoice_data)

            if result.get('success'):
                # Actualizar documento con datos SIAT
                self.doc.db_set('sin_cuf', result['cuf'])
                self.doc.db_set('sin_estado', result['estado'])
                self.doc.db_set('sin_fecha_envio', datetime.now())

                frappe.db.commit()

                return {
                    'success': True,
                    'cuf': result['cuf'],
                    'estado': result['estado'],
                    'mensaje': result.get('mensaje', 'Factura enviada exitosamente')
                }
            else:
                # Manejar error
                frappe.log_error(
                    f"Error sending invoice {self.doc.name} to SIAT: {result.get('error')}",
                    "SIAT Invoice Error"
                )

                return {
                    'success': False,
                    'error': result.get('error'),
                    'offline_mode': result.get('offline_mode', False)
                }

        except Exception as e:
            frappe.log_error(f"Exception sending invoice to SIAT: {str(e)}", "SIAT Exception")
            return {
                'success': False,
                'error': str(e)
            }

    def verify_status(self) -> Dict[str, Any]:
        """
        Verifica el estado de la factura en SIAT

        Returns:
            Dict con estado actual
        """
        cuf = self.doc.get('sin_cuf')
        if not cuf:
            return {
                'success': False,
                'error': 'Factura no tiene CUF asignado'
            }

        return self.client.verify_invoice(cuf)

    def cancel(self, reason_code: int, reason: str) -> Dict[str, Any]:
        """
        Anula la factura en SIAT

        Args:
            reason_code: Código del motivo (1-3)
            reason: Descripción del motivo

        Returns:
            Dict con resultado de anulación
        """
        cuf = self.doc.get('sin_cuf')
        if not cuf:
            return {
                'success': False,
                'error': 'Factura no tiene CUF asignado'
            }

        result = self.client.cancel_invoice(cuf, reason_code, reason)

        if result.get('success'):
            self.doc.db_set('sin_estado', 'ANULADA')
            self.doc.db_set('sin_fecha_anulacion', datetime.now())
            frappe.db.commit()

        return result


def create_electronic_invoice(sales_invoice: str) -> Dict[str, Any]:
    """
    Crea y envía una factura electrónica al SIAT

    Args:
        sales_invoice: Nombre del documento Sales Invoice

    Returns:
        Dict con resultado
    """
    try:
        einvoice = ElectronicInvoice(sales_invoice)
        return einvoice.send_to_siat()
    except Exception as e:
        frappe.log_error(f"Error creating electronic invoice: {str(e)}", "Electronic Invoice Error")
        return {
            'success': False,
            'error': str(e)
        }


@frappe.whitelist()
def send_invoice_to_siat(sales_invoice: str) -> Dict[str, Any]:
    """
    API endpoint para enviar factura a SIAT

    Args:
        sales_invoice: Nombre del documento Sales Invoice

    Returns:
        Dict con resultado
    """
    return create_electronic_invoice(sales_invoice)


@frappe.whitelist()
def verify_invoice_status(sales_invoice: str) -> Dict[str, Any]:
    """
    API endpoint para verificar estado de factura en SIAT

    Args:
        sales_invoice: Nombre del documento Sales Invoice

    Returns:
        Dict con estado
    """
    try:
        einvoice = ElectronicInvoice(sales_invoice)
        return einvoice.verify_status()
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


@frappe.whitelist()
def cancel_invoice_in_siat(sales_invoice: str, reason_code: int, reason: str) -> Dict[str, Any]:
    """
    API endpoint para anular factura en SIAT

    Args:
        sales_invoice: Nombre del documento Sales Invoice
        reason_code: Código del motivo
        reason: Descripción del motivo

    Returns:
        Dict con resultado
    """
    try:
        einvoice = ElectronicInvoice(sales_invoice)
        return einvoice.cancel(int(reason_code), reason)
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
