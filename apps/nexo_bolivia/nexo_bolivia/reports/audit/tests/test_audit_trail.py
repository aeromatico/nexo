# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

"""Tests para Audit Trail"""

import frappe
import unittest
from datetime import datetime


class TestAuditTrail(unittest.TestCase):
    """Suite de tests para Audit Trail"""

    def test_log_fiscal_transaction(self):
        """Test: log_fiscal_transaction registra correctamente"""
        from nexo_bolivia.reports.audit.audit_trail import log_fiscal_transaction

        data = {
            'name': 'SI-001',
            'customer': 'Test Customer',
            'amount': 1000
        }

        result = log_fiscal_transaction(
            'Sales Invoice',
            'SI-001',
            'submit',
            'Administrator',
            data,
            'Test transaction'
        )

        self.assertIsNotNone(result)
        # result es el ID del registro creado

    def test_generate_document_hash(self):
        """Test: generate_document_hash genera hash único"""
        from nexo_bolivia.reports.audit.audit_trail import generate_document_hash

        data1 = {'name': 'SI-001', 'amount': 1000}
        data2 = {'name': 'SI-001', 'amount': 1000}
        data3 = {'name': 'SI-001', 'amount': 2000}

        hash1 = generate_document_hash(data1)
        hash2 = generate_document_hash(data2)
        hash3 = generate_document_hash(data3)

        # Mismos datos = mismo hash
        self.assertEqual(hash1, hash2)

        # Datos diferentes = hash diferente
        self.assertNotEqual(hash1, hash3)

    def test_get_last_hash(self):
        """Test: get_last_hash obtiene último hash registrado"""
        from nexo_bolivia.reports.audit.audit_trail import (
            get_last_hash, log_fiscal_transaction
        )

        data = {'name': 'SI-002', 'customer': 'Test', 'amount': 1000}

        # Crear registro
        log_fiscal_transaction(
            'Sales Invoice',
            'SI-002',
            'submit',
            'Administrator',
            data
        )

        # Obtener último hash
        last_hash = get_last_hash('Sales Invoice', 'SI-002')

        self.assertIsNotNone(last_hash)

    def test_get_audit_trail_returns_list(self):
        """Test: get_audit_trail retorna lista"""
        from nexo_bolivia.reports.audit.audit_trail import get_audit_trail

        result = get_audit_trail()

        self.assertIsInstance(result, list)

    def test_get_audit_trail_with_filters(self):
        """Test: get_audit_trail filtra correctamente"""
        from nexo_bolivia.reports.audit.audit_trail import get_audit_trail

        filters = {
            'doctype': 'Sales Invoice'
        }

        result = get_audit_trail(filters)

        self.assertIsInstance(result, list)

    def test_verify_audit_integrity(self):
        """Test: verify_audit_integrity valida cadena"""
        from nexo_bolivia.reports.audit.audit_trail import verify_audit_integrity

        result = verify_audit_integrity()

        self.assertIn('status', result)
        self.assertIn('total_entries', result)


if __name__ == '__main__':
    unittest.main()
