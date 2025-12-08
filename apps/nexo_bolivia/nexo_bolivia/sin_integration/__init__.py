"""
Nexo Bolivia - SIN Integration Module
Sistema de Impuestos Nacionales (SIN) - Electronic Invoice Integration

This module provides integration with Bolivia's tax authority (SIN/SIAT) for
electronic invoicing (facturación electrónica).

Main components:
- client: SIAT API client for communication
- invoice: Electronic invoice generation and submission
- qr: QR code generation for invoices
- sync: Synchronization with SIAT servers
"""

from .client import SIATClient
from .invoice import ElectronicInvoice, create_electronic_invoice
from .qr import generate_invoice_qr
from .sync import sync_with_siat, validate_siat_status

__all__ = [
    'SIATClient',
    'ElectronicInvoice',
    'create_electronic_invoice',
    'generate_invoice_qr',
    'sync_with_siat',
    'validate_siat_status',
]
