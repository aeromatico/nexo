"""
SIN Integration Hooks
Hook functions para facturación electrónica y sincronización con SIAT
"""

import frappe
from frappe import _
from typing import Optional
from .invoice import create_electronic_invoice
from .qr import generate_qr_for_sales_invoice
from .sync import (
    sync_with_siat,
    validate_siat_status,
    check_cufd_validity,
    renew_cufd
)


def on_submit_sales_invoice(doc, method=None):
    """
    Hook ejecutado cuando se envía (submit) una Sales Invoice

    Envía automáticamente la factura al SIAT si está configurado

    Args:
        doc: Documento Sales Invoice
        method: Método del hook (no usado)
    """
    # Verificar si la facturación electrónica está habilitada para esta empresa
    company_doc = frappe.get_doc('Company', doc.company)
    sin_enabled = getattr(company_doc, 'sin_facturacion_electronica', False)

    if not sin_enabled:
        frappe.logger().info(f"SIN not enabled for company {doc.company}, skipping electronic invoice")
        return

    try:
        # Verificar CUFD válido
        cufd_status = check_cufd_validity(doc.company)
        if not cufd_status.get('valid'):
            # Intentar renovar CUFD automáticamente
            renewal_result = renew_cufd(doc.company)
            if not renewal_result.get('success'):
                frappe.msgprint(
                    _("CUFD inválido. Renovación automática falló. Por favor renueve manualmente."),
                    indicator='orange',
                    alert=True
                )
                # Marcar factura como pendiente
                doc.db_set('sin_estado', 'PENDIENTE')
                return

        # Enviar factura al SIAT
        result = create_electronic_invoice(doc.name)

        if result.get('success'):
            # Generar QR code
            qr_image = generate_qr_for_sales_invoice(doc.name)

            frappe.msgprint(
                _("Factura electrónica enviada exitosamente al SIAT.<br>CUF: {0}").format(result['cuf']),
                indicator='green',
                alert=True
            )
        elif result.get('offline_mode'):
            # Modo offline/contingencia
            doc.db_set('sin_estado', 'PENDIENTE')
            frappe.msgprint(
                _("SIAT no disponible. Factura guardada para envío posterior."),
                indicator='orange',
                alert=True
            )
        else:
            # Error al enviar
            doc.db_set('sin_estado', 'ERROR')
            frappe.msgprint(
                _("Error enviando factura a SIAT: {0}").format(result.get('error', 'Error desconocido')),
                indicator='red',
                alert=True
            )

    except Exception as e:
        frappe.log_error(f"Error in on_submit_sales_invoice: {str(e)}", "SIN Integration Hook Error")
        doc.db_set('sin_estado', 'ERROR')
        frappe.msgprint(
            _("Error procesando factura electrónica: {0}").format(str(e)),
            indicator='red',
            alert=True
        )


def on_cancel_sales_invoice(doc, method=None):
    """
    Hook ejecutado cuando se cancela una Sales Invoice

    Anula la factura en el SIAT si fue enviada

    Args:
        doc: Documento Sales Invoice
        method: Método del hook (no usado)
    """
    # Verificar si tiene CUF (fue enviada al SIAT)
    cuf = doc.get('sin_cuf')
    if not cuf:
        frappe.logger().info(f"Invoice {doc.name} has no CUF, skipping SIAT cancellation")
        return

    company_doc = frappe.get_doc('Company', doc.company)
    sin_enabled = getattr(company_doc, 'sin_facturacion_electronica', False)

    if not sin_enabled:
        return

    try:
        from .invoice import ElectronicInvoice

        einvoice = ElectronicInvoice(doc.name)

        # Código de motivo por defecto: 1 = Anulación (otros: 2=Extravío, 3=Otros)
        reason_code = 1
        reason = frappe.get_value('Sales Invoice', doc.name, 'remarks') or 'Factura anulada'

        result = einvoice.cancel(reason_code, reason)

        if result.get('success'):
            frappe.msgprint(
                _("Factura anulada exitosamente en el SIAT"),
                indicator='green',
                alert=True
            )
        else:
            frappe.msgprint(
                _("Error anulando factura en SIAT: {0}").format(result.get('error', 'Error desconocido')),
                indicator='orange',
                alert=True
            )

    except Exception as e:
        frappe.log_error(f"Error in on_cancel_sales_invoice: {str(e)}", "SIN Cancel Hook Error")
        frappe.msgprint(
            _("Error anulando factura electrónica: {0}").format(str(e)),
            indicator='red',
            alert=True
        )


def daily_cufd_renewal():
    """
    Scheduled task: Renueva el CUFD diariamente para todas las empresas con SIN habilitado

    Se ejecuta automáticamente cada día
    """
    frappe.logger().info("Starting daily CUFD renewal task")

    try:
        # Obtener todas las empresas con facturación electrónica habilitada
        companies = frappe.get_all(
            'Company',
            filters={'sin_facturacion_electronica': 1},
            fields=['name']
        )

        for company in companies:
            try:
                # Verificar si necesita renovación
                cufd_status = check_cufd_validity(company.name)

                if cufd_status.get('needs_renewal'):
                    frappe.logger().info(f"Renewing CUFD for company {company.name}")

                    result = renew_cufd(company.name)

                    if result.get('success'):
                        frappe.logger().info(f"CUFD renewed successfully for {company.name}: {result['cufd']}")
                    else:
                        frappe.log_error(
                            f"Failed to renew CUFD for {company.name}: {result.get('error')}",
                            "CUFD Renewal Failed"
                        )
                else:
                    frappe.logger().info(f"CUFD still valid for {company.name}")

            except Exception as e:
                frappe.log_error(f"Error renewing CUFD for {company.name}: {str(e)}", "CUFD Renewal Error")

        frappe.logger().info("Daily CUFD renewal task completed")

    except Exception as e:
        frappe.log_error(f"Error in daily_cufd_renewal task: {str(e)}", "CUFD Task Error")


def sync_pending_invoices():
    """
    Scheduled task: Sincroniza facturas pendientes con SIAT

    Se ejecuta automáticamente cada día
    """
    frappe.logger().info("Starting sync pending invoices task")

    try:
        # Obtener todas las empresas con facturación electrónica habilitada
        companies = frappe.get_all(
            'Company',
            filters={'sin_facturacion_electronica': 1},
            fields=['name']
        )

        for company in companies:
            try:
                frappe.logger().info(f"Syncing pending invoices for company {company.name}")

                result = sync_with_siat(company.name)

                if result.get('total', 0) > 0:
                    frappe.logger().info(
                        f"Sync completed for {company.name}: "
                        f"{result.get('success', 0)} success, {result.get('failed', 0)} failed"
                    )

                    if result.get('failed', 0) > 0:
                        frappe.log_error(
                            f"Some invoices failed to sync for {company.name}: {result.get('errors')}",
                            "Invoice Sync Partial Failure"
                        )

            except Exception as e:
                frappe.log_error(f"Error syncing invoices for {company.name}: {str(e)}", "Sync Task Error")

        frappe.logger().info("Sync pending invoices task completed")

    except Exception as e:
        frappe.log_error(f"Error in sync_pending_invoices task: {str(e)}", "Sync Task Error")


def check_siat_connection():
    """
    Scheduled task: Verifica el estado de conexión con SIAT cada hora

    Monitorea disponibilidad del SIAT y registra estados
    """
    frappe.logger().info("Starting SIAT connection check")

    try:
        # Obtener todas las empresas con facturación electrónica habilitada
        companies = frappe.get_all(
            'Company',
            filters={'sin_facturacion_electronica': 1},
            fields=['name']
        )

        for company in companies:
            try:
                status = validate_siat_status(company.name)

                if not status.get('online'):
                    # SIAT no disponible, registrar
                    frappe.log_error(
                        f"SIAT offline for company {company.name}: {status.get('message')}",
                        "SIAT Offline Alert"
                    )

                    # Verificar si debe activar modo contingencia automático
                    company_doc = frappe.get_doc('Company', company.name)
                    auto_contingency = getattr(company_doc, 'sin_auto_contingencia', False)

                    if auto_contingency and not getattr(company_doc, 'sin_modo_contingencia', False):
                        from .sync import enable_contingency_mode
                        enable_contingency_mode(company.name, 'Activación automática - SIAT no disponible')
                        frappe.logger().info(f"Auto-contingency enabled for {company.name}")

            except Exception as e:
                frappe.log_error(f"Error checking SIAT status for {company.name}: {str(e)}", "SIAT Check Error")

        frappe.logger().info("SIAT connection check completed")

    except Exception as e:
        frappe.log_error(f"Error in check_siat_connection task: {str(e)}", "SIAT Check Task Error")
