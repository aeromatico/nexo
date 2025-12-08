"""
QR Code Generation Module
Generación de códigos QR para facturas electrónicas según especificaciones SIAT
"""

import frappe
import qrcode
import io
import base64
from typing import Optional, Dict, Any
from frappe import _


def generate_invoice_qr(
    nit: str,
    numero_factura: str,
    nit_cliente: str,
    fecha_emision: str,
    monto_total: float,
    cuf: str,
    codigo_control: Optional[str] = None
) -> str:
    """
    Genera código QR para factura electrónica según especificaciones del SIAT

    El QR contiene información de la factura separada por pipes (|)

    Args:
        nit: NIT del emisor
        numero_factura: Número de la factura
        nit_cliente: NIT del cliente
        fecha_emision: Fecha de emisión (YYYY-MM-DD)
        monto_total: Monto total de la factura
        cuf: Código Único de Factura
        codigo_control: Código de control (opcional para contingencia)

    Returns:
        String con imagen QR en base64
    """
    # Construir string de datos del QR según especificación SIAT
    # Formato: NIT|FACTURA|NIT_CLIENTE|FECHA|MONTO|CODIGO_CONTROL|CUF
    qr_data = f"{nit}|{numero_factura}|{nit_cliente}|{fecha_emision}|{monto_total}"

    if codigo_control:
        qr_data += f"|{codigo_control}"

    qr_data += f"|{cuf}"

    # Generar QR code
    qr = qrcode.QRCode(
        version=1,  # Tamaño automático
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

    qr.add_data(qr_data)
    qr.make(fit=True)

    # Crear imagen
    img = qr.make_image(fill_color="black", back_color="white")

    # Convertir a base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    img_base64 = base64.b64encode(buffer.getvalue()).decode()

    return f"data:image/png;base64,{img_base64}"


def generate_qr_for_sales_invoice(sales_invoice: str) -> Optional[str]:
    """
    Genera QR para una Sales Invoice existente

    Args:
        sales_invoice: Nombre del documento Sales Invoice

    Returns:
        String con imagen QR en base64, o None si falta información
    """
    try:
        doc = frappe.get_doc('Sales Invoice', sales_invoice)
        company_doc = frappe.get_doc('Company', doc.company)

        # Validar que tenga CUF (ya fue enviada a SIAT)
        cuf = doc.get('sin_cuf')
        if not cuf:
            frappe.msgprint(_("Esta factura aún no tiene CUF asignado. Debe ser enviada al SIAT primero."))
            return None

        # Obtener NIT de la empresa
        nit = getattr(company_doc, 'sin_nit', None) or frappe.conf.get('sin_nit')
        if not nit:
            frappe.throw(_("NIT de la empresa no configurado"))

        # Obtener NIT del cliente
        customer = frappe.get_doc('Customer', doc.customer)
        nit_cliente = getattr(customer, 'tax_id', None) or '0'

        # Generar QR
        qr_image = generate_invoice_qr(
            nit=nit,
            numero_factura=str(doc.name),
            nit_cliente=nit_cliente,
            fecha_emision=doc.posting_date.strftime('%Y-%m-%d') if doc.posting_date else '',
            monto_total=float(doc.grand_total),
            cuf=cuf,
            codigo_control=doc.get('sin_codigo_control')
        )

        # Guardar QR en el documento
        doc.db_set('sin_qr_code', qr_image)
        frappe.db.commit()

        return qr_image

    except Exception as e:
        frappe.log_error(f"Error generating QR for {sales_invoice}: {str(e)}", "QR Generation Error")
        return None


def verify_qr_content(qr_data: str) -> Dict[str, Any]:
    """
    Verifica y extrae información de un QR de factura

    Args:
        qr_data: String con datos del QR

    Returns:
        Dict con información extraída
    """
    try:
        parts = qr_data.split('|')

        if len(parts) < 6:
            return {
                'valid': False,
                'error': 'Formato de QR inválido'
            }

        return {
            'valid': True,
            'nit': parts[0],
            'numero_factura': parts[1],
            'nit_cliente': parts[2],
            'fecha_emision': parts[3],
            'monto_total': float(parts[4]),
            'codigo_control': parts[5] if len(parts) > 6 else None,
            'cuf': parts[-1]
        }

    except Exception as e:
        return {
            'valid': False,
            'error': str(e)
        }


@frappe.whitelist()
def generate_qr_code(sales_invoice: str) -> Optional[str]:
    """
    API endpoint para generar QR de una factura

    Args:
        sales_invoice: Nombre del documento Sales Invoice

    Returns:
        String con imagen QR en base64
    """
    return generate_qr_for_sales_invoice(sales_invoice)


@frappe.whitelist()
def verify_qr(qr_data: str) -> Dict[str, Any]:
    """
    API endpoint para verificar contenido de un QR

    Args:
        qr_data: String con datos del QR

    Returns:
        Dict con información extraída
    """
    return verify_qr_content(qr_data)
