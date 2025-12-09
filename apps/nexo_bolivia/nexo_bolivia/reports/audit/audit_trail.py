# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

"""
Pista de Auditoría - Audit Trail

Sistema inmutable de registro de todas las transacciones fiscales.
Permite rastrear cambios en facturas, impuestos y otros documentos críticos.
"""

import frappe
from frappe import _
from datetime import datetime
import hashlib
from typing import Dict, List, Any, Optional


def log_fiscal_transaction(
    doctype: str,
    docname: str,
    action: str,
    user: str,
    data: Dict[str, Any],
    description: str = ''
) -> str:
    """
    Registra transacción fiscal en audit trail

    Args:
        doctype: Tipo de documento (ej: 'Sales Invoice')
        docname: Nombre del documento
        action: Acción (create, modify, cancel, submit)
        user: Usuario que realiza la acción
        data: Datos del documento
        description: Descripción adicional

    Returns:
        str: ID del registro de auditoría
    """
    # Crear hash del documento para integridad
    doc_hash = generate_document_hash(data)

    # Obtener hash anterior (para cadena de auditoría)
    previous_hash = get_last_hash(doctype, docname)

    # Crear registro
    audit_entry = frappe.get_doc({
        'doctype': 'Audit Trail Entry',
        'fiscal_document_type': doctype,
        'fiscal_document_name': docname,
        'action': action,
        'user': user,
        'timestamp': datetime.now(),
        'document_hash': doc_hash,
        'previous_hash': previous_hash,
        'description': description,
        'data_snapshot': frappe.as_json(data)
    })

    audit_entry.insert()
    return audit_entry.name


def log_sales_invoice_submit(doc, method=None):
    """Hook: Registra en auditoría cuando se publica factura de venta"""
    data = {
        'name': doc.name,
        'customer': doc.customer,
        'grand_total': doc.grand_total,
        'posting_date': str(doc.posting_date)
    }

    log_fiscal_transaction(
        'Sales Invoice',
        doc.name,
        'submit',
        frappe.session.user,
        data,
        f'Sales Invoice submitted for {doc.customer}'
    )


def log_purchase_invoice_submit(doc, method=None):
    """Hook: Registra en auditoría cuando se publica factura de compra"""
    data = {
        'name': doc.name,
        'supplier': doc.supplier,
        'grand_total': doc.grand_total,
        'posting_date': str(doc.posting_date)
    }

    log_fiscal_transaction(
        'Purchase Invoice',
        doc.name,
        'submit',
        frappe.session.user,
        data,
        f'Purchase Invoice submitted for {doc.supplier}'
    )


def get_audit_trail(filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Obtiene pista de auditoría filtrada

    Args:
        filters: Filtros opcionales
            - doctype: Tipo de documento
            - docname: Nombre del documento
            - from_date: Fecha inicio
            - to_date: Fecha fin
            - user: Usuario
            - action: Acción

    Returns:
        List[Dict]: Registros de auditoría
    """
    if not filters:
        filters = {}

    conditions = []
    params = []

    if filters.get('doctype'):
        conditions.append('fiscal_document_type = %s')
        params.append(filters.get('doctype'))

    if filters.get('docname'):
        conditions.append('fiscal_document_name = %s')
        params.append(filters.get('docname'))

    if filters.get('from_date'):
        conditions.append('DATE(timestamp) >= %s')
        params.append(filters.get('from_date'))

    if filters.get('to_date'):
        conditions.append('DATE(timestamp) <= %s')
        params.append(filters.get('to_date'))

    if filters.get('user'):
        conditions.append('user = %s')
        params.append(filters.get('user'))

    if filters.get('action'):
        conditions.append('action = %s')
        params.append(filters.get('action'))

    where_clause = ' AND '.join(conditions) if conditions else '1=1'

    query = f"""
        SELECT
            name,
            fiscal_document_type,
            fiscal_document_name,
            action,
            user,
            timestamp,
            description,
            document_hash,
            previous_hash
        FROM `tabAudit Trail Entry`
        WHERE {where_clause}
        ORDER BY timestamp DESC
    """

    results = frappe.db.sql(query, params, as_dict=True)
    return results


def verify_audit_integrity() -> Dict[str, Any]:
    """
    Verifica integridad de audit trail

    Valida que la cadena de hashes sea continua y no haya manipulación.

    Returns:
        Dict: Resultado de la verificación
    """
    # Obtener todos los registros ordenados
    entries = frappe.db.sql("""
        SELECT
            name,
            fiscal_document_type,
            fiscal_document_name,
            document_hash,
            previous_hash,
            timestamp
        FROM `tabAudit Trail Entry`
        ORDER BY timestamp ASC
    """, as_dict=True)

    if not entries:
        return {
            'status': 'OK',
            'total_entries': 0,
            'integrity_errors': []
        }

    integrity_errors = []

    # Verificar continuidad de hashes
    for i, entry in enumerate(entries):
        if i > 0:
            previous_entry = entries[i - 1]
            # Verificar que el hash anterior coincida
            if entry['previous_hash'] != previous_entry['document_hash']:
                integrity_errors.append({
                    'entry_id': entry['name'],
                    'error': 'Hash chain broken',
                    'expected': previous_entry['document_hash'],
                    'actual': entry['previous_hash']
                })

    return {
        'status': 'OK' if not integrity_errors else 'ERROR',
        'total_entries': len(entries),
        'integrity_errors': integrity_errors,
        'timestamp': datetime.now()
    }


def generate_document_hash(data: Dict[str, Any]) -> str:
    """
    Genera hash SHA256 de los datos del documento

    Args:
        data: Datos del documento

    Returns:
        str: Hash SHA256
    """
    json_str = frappe.as_json(data)
    hash_obj = hashlib.sha256(json_str.encode())
    return hash_obj.hexdigest()


def get_last_hash(doctype: str, docname: str) -> Optional[str]:
    """
    Obtiene el último hash registrado para un documento

    Args:
        doctype: Tipo de documento
        docname: Nombre del documento

    Returns:
        str: Hash o None si no existe
    """
    last_entry = frappe.db.sql("""
        SELECT document_hash
        FROM `tabAudit Trail Entry`
        WHERE fiscal_document_type = %s
        AND fiscal_document_name = %s
        ORDER BY timestamp DESC
        LIMIT 1
    """, (doctype, docname), as_dict=True)

    if last_entry:
        return last_entry[0]['document_hash']

    return None


@frappe.whitelist()
def get_audit_trail_report(filters: str) -> List[Dict[str, Any]]:
    """
    API para obtener pista de auditoría

    Args:
        filters: JSON string con filtros

    Returns:
        List[Dict]: Registros de auditoría
    """
    if isinstance(filters, str):
        import json
        filters = json.loads(filters)

    return get_audit_trail(filters)


@frappe.whitelist()
def verify_document_integrity(doctype: str, docname: str) -> Dict[str, Any]:
    """
    Verifica integridad de un documento específico

    Args:
        doctype: Tipo de documento
        docname: Nombre del documento

    Returns:
        Dict: Resultado de verificación
    """
    entries = frappe.db.sql("""
        SELECT
            name,
            document_hash,
            previous_hash,
            timestamp
        FROM `tabAudit Trail Entry`
        WHERE fiscal_document_type = %s
        AND fiscal_document_name = %s
        ORDER BY timestamp ASC
    """, (doctype, docname), as_dict=True)

    if not entries:
        return {
            'status': 'NOT_FOUND',
            'message': f'No audit entries found for {doctype} {docname}'
        }

    errors = []

    for i, entry in enumerate(entries):
        if i > 0:
            if entry['previous_hash'] != entries[i-1]['document_hash']:
                errors.append(f'Hash chain broken at entry {entry["name"]}')

    return {
        'status': 'OK' if not errors else 'ERROR',
        'document': f'{doctype}/{docname}',
        'total_entries': len(entries),
        'errors': errors,
        'first_entry': entries[0]['name'] if entries else None,
        'last_entry': entries[-1]['name'] if entries else None
    }
