"""
SIAT Synchronization Module
Sincronización y gestión de contingencia con SIAT
"""

import frappe
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from frappe import _
from .client import SIATClient


def sync_with_siat(company: Optional[str] = None) -> Dict[str, Any]:
    """
    Sincroniza facturas pendientes con SIAT

    Busca facturas que no se pudieron enviar (modo offline) y las reenvía

    Args:
        company: Nombre de la empresa (opcional)

    Returns:
        Dict con resultados de la sincronización
    """
    try:
        client = SIATClient(company)

        # Buscar facturas pendientes de sincronización
        filters = {
            'docstatus': 1,  # Solo facturas submitted
            'sin_estado': ['in', ['PENDIENTE', 'ERROR', None]]
        }

        if company:
            filters['company'] = company

        pending_invoices = frappe.get_all(
            'Sales Invoice',
            filters=filters,
            fields=['name', 'posting_date', 'grand_total', 'sin_cuf', 'sin_estado'],
            order_by='posting_date asc',
            limit=100  # Sincronizar máximo 100 a la vez
        )

        results = {
            'total': len(pending_invoices),
            'success': 0,
            'failed': 0,
            'errors': []
        }

        for invoice in pending_invoices:
            try:
                # Intentar enviar factura
                from .invoice import ElectronicInvoice

                einvoice = ElectronicInvoice(invoice.name)
                result = einvoice.send_to_siat()

                if result.get('success'):
                    results['success'] += 1
                    frappe.logger().info(f"Synced invoice {invoice.name} successfully")
                else:
                    results['failed'] += 1
                    results['errors'].append({
                        'invoice': invoice.name,
                        'error': result.get('error', 'Unknown error')
                    })

                # Pequeña pausa entre facturas
                frappe.db.commit()

            except Exception as e:
                results['failed'] += 1
                results['errors'].append({
                    'invoice': invoice.name,
                    'error': str(e)
                })
                frappe.log_error(f"Error syncing invoice {invoice.name}: {str(e)}", "SIAT Sync Error")

        return results

    except Exception as e:
        frappe.log_error(f"SIAT sync failed: {str(e)}", "SIAT Sync Error")
        return {
            'success': False,
            'error': str(e)
        }


def validate_siat_status(company: Optional[str] = None) -> Dict[str, Any]:
    """
    Valida el estado de la conexión con SIAT

    Args:
        company: Nombre de la empresa (opcional)

    Returns:
        Dict con estado de conexión
    """
    try:
        client = SIATClient(company)
        result = client.test_connection()

        if result.get('success'):
            return {
                'online': True,
                'status': 'ONLINE',
                'message': 'Conexión exitosa con SIAT',
                'last_check': datetime.now().isoformat()
            }
        else:
            return {
                'online': False,
                'status': 'OFFLINE',
                'message': result.get('message', 'No se pudo conectar con SIAT'),
                'last_check': datetime.now().isoformat()
            }

    except Exception as e:
        return {
            'online': False,
            'status': 'ERROR',
            'message': str(e),
            'last_check': datetime.now().isoformat()
        }


def check_cufd_validity(company: str) -> Dict[str, Any]:
    """
    Verifica validez del CUFD (Código Único de Factura Diaria)

    El CUFD debe renovarse diariamente

    Args:
        company: Nombre de la empresa

    Returns:
        Dict con estado del CUFD
    """
    try:
        company_doc = frappe.get_doc('Company', company)
        cufd = getattr(company_doc, 'sin_cufd', None)
        cufd_date = getattr(company_doc, 'sin_cufd_fecha', None)

        if not cufd or not cufd_date:
            return {
                'valid': False,
                'reason': 'CUFD no configurado',
                'needs_renewal': True
            }

        # Verificar si es del día actual
        today = datetime.now().date()
        cufd_date_obj = cufd_date if isinstance(cufd_date, datetime) else datetime.strptime(str(cufd_date), '%Y-%m-%d')

        if cufd_date_obj.date() < today:
            return {
                'valid': False,
                'reason': 'CUFD vencido',
                'needs_renewal': True,
                'expired_date': cufd_date_obj.date().isoformat()
            }

        return {
            'valid': True,
            'cufd': cufd,
            'date': cufd_date_obj.date().isoformat()
        }

    except Exception as e:
        return {
            'valid': False,
            'reason': str(e),
            'needs_renewal': True
        }


def renew_cufd(company: str) -> Dict[str, Any]:
    """
    Renueva el CUFD con SIAT

    Args:
        company: Nombre de la empresa

    Returns:
        Dict con nuevo CUFD
    """
    try:
        client = SIATClient(company)
        client._ensure_token()

        endpoint = f"{client.base_url}/api/v1/cufd"

        headers = {
            'Authorization': f'Bearer {client.token}',
            'Content-Type': 'application/json'
        }

        payload = {
            'nit': client.nit,
            'codigoSucursal': int(client._get_config('sin_sucursal', 0)),
            'codigoPuntoVenta': int(client._get_config('sin_punto_venta', 0))
        }

        import requests
        response = requests.post(endpoint, json=payload, headers=headers, timeout=30)
        response.raise_for_status()

        data = response.json()

        if data.get('transaccion'):
            cufd = data['respuesta']['cufd']
            codigo_control = data['respuesta'].get('codigoControl')

            # Actualizar en Company
            company_doc = frappe.get_doc('Company', company)
            company_doc.db_set('sin_cufd', cufd)
            company_doc.db_set('sin_cufd_fecha', datetime.now().date())
            company_doc.db_set('sin_codigo_control', codigo_control)
            frappe.db.commit()

            frappe.logger().info(f"CUFD renewed successfully for {company}")

            return {
                'success': True,
                'cufd': cufd,
                'codigo_control': codigo_control,
                'fecha': datetime.now().date().isoformat()
            }
        else:
            return {
                'success': False,
                'error': data.get('mensaje', 'Error desconocido')
            }

    except Exception as e:
        frappe.log_error(f"Error renewing CUFD: {str(e)}", "CUFD Renewal Error")
        return {
            'success': False,
            'error': str(e)
        }


def enable_contingency_mode(company: str, reason: str) -> Dict[str, Any]:
    """
    Habilita modo de contingencia cuando SIAT no está disponible

    Args:
        company: Nombre de la empresa
        reason: Razón de la contingencia

    Returns:
        Dict con CAFC (Código de Autorización de Facturas por Contingencia)
    """
    try:
        client = SIATClient(company)
        client._ensure_token()

        endpoint = f"{client.base_url}/api/v1/contingencia/cafc"

        headers = {
            'Authorization': f'Bearer {client.token}',
            'Content-Type': 'application/json'
        }

        payload = {
            'nit': client.nit,
            'codigoSucursal': int(client._get_config('sin_sucursal', 0)),
            'codigoPuntoVenta': int(client._get_config('sin_punto_venta', 0)),
            'descripcion': reason
        }

        import requests
        response = requests.post(endpoint, json=payload, headers=headers, timeout=30)
        response.raise_for_status()

        data = response.json()

        if data.get('transaccion'):
            cafc = data['respuesta']['cafc']

            # Guardar CAFC en Company
            company_doc = frappe.get_doc('Company', company)
            company_doc.db_set('sin_cafc', cafc)
            company_doc.db_set('sin_modo_contingencia', 1)
            company_doc.db_set('sin_contingencia_inicio', datetime.now())
            frappe.db.commit()

            frappe.logger().info(f"Contingency mode enabled for {company}: CAFC {cafc}")

            return {
                'success': True,
                'cafc': cafc,
                'message': 'Modo de contingencia activado'
            }
        else:
            return {
                'success': False,
                'error': data.get('mensaje', 'Error activando contingencia')
            }

    except Exception as e:
        frappe.log_error(f"Error enabling contingency: {str(e)}", "Contingency Mode Error")
        return {
            'success': False,
            'error': str(e)
        }


def disable_contingency_mode(company: str) -> Dict[str, Any]:
    """
    Deshabilita modo de contingencia y sincroniza facturas pendientes

    Args:
        company: Nombre de la empresa

    Returns:
        Dict con resultado
    """
    try:
        company_doc = frappe.get_doc('Company', company)

        if not getattr(company_doc, 'sin_modo_contingencia', False):
            return {
                'success': False,
                'message': 'No está en modo de contingencia'
            }

        # Sincronizar facturas pendientes
        sync_result = sync_with_siat(company)

        # Deshabilitar modo
        company_doc.db_set('sin_modo_contingencia', 0)
        company_doc.db_set('sin_cafc', None)
        company_doc.db_set('sin_contingencia_fin', datetime.now())
        frappe.db.commit()

        frappe.logger().info(f"Contingency mode disabled for {company}")

        return {
            'success': True,
            'message': 'Modo de contingencia desactivado',
            'sync_result': sync_result
        }

    except Exception as e:
        frappe.log_error(f"Error disabling contingency: {str(e)}", "Contingency Disable Error")
        return {
            'success': False,
            'error': str(e)
        }


def get_pending_invoices_count(company: Optional[str] = None) -> int:
    """
    Obtiene cantidad de facturas pendientes de sincronización

    Args:
        company: Nombre de la empresa (opcional)

    Returns:
        Cantidad de facturas pendientes
    """
    filters = {
        'docstatus': 1,
        'sin_estado': ['in', ['PENDIENTE', 'ERROR', None]]
    }

    if company:
        filters['company'] = company

    return frappe.db.count('Sales Invoice', filters)


@frappe.whitelist()
def sync_invoices(company: str = None) -> Dict[str, Any]:
    """
    API endpoint para sincronizar facturas

    Args:
        company: Nombre de la empresa (opcional)

    Returns:
        Dict con resultados
    """
    return sync_with_siat(company)


@frappe.whitelist()
def check_siat_status(company: str = None) -> Dict[str, Any]:
    """
    API endpoint para verificar estado SIAT

    Args:
        company: Nombre de la empresa (opcional)

    Returns:
        Dict con estado
    """
    return validate_siat_status(company)


@frappe.whitelist()
def get_cufd_status(company: str) -> Dict[str, Any]:
    """
    API endpoint para verificar estado CUFD

    Args:
        company: Nombre de la empresa

    Returns:
        Dict con estado CUFD
    """
    return check_cufd_validity(company)


@frappe.whitelist()
def request_new_cufd(company: str) -> Dict[str, Any]:
    """
    API endpoint para renovar CUFD

    Args:
        company: Nombre de la empresa

    Returns:
        Dict con nuevo CUFD
    """
    return renew_cufd(company)


@frappe.whitelist()
def start_contingency(company: str, reason: str) -> Dict[str, Any]:
    """
    API endpoint para iniciar modo contingencia

    Args:
        company: Nombre de la empresa
        reason: Razón de contingencia

    Returns:
        Dict con CAFC
    """
    return enable_contingency_mode(company, reason)


@frappe.whitelist()
def end_contingency(company: str) -> Dict[str, Any]:
    """
    API endpoint para finalizar modo contingencia

    Args:
        company: Nombre de la empresa

    Returns:
        Dict con resultado
    """
    return disable_contingency_mode(company)


@frappe.whitelist()
def get_pending_count(company: str = None) -> Dict[str, Any]:
    """
    API endpoint para obtener cantidad de facturas pendientes

    Args:
        company: Nombre de la empresa (opcional)

    Returns:
        Dict con cantidad
    """
    count = get_pending_invoices_count(company)
    return {
        'count': count,
        'company': company or 'All'
    }
