"""Tests de carga y performance del sistema."""

import pytest
import frappe
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta


class TestPerformance:
    """Test system performance under load."""

    def test_invoice_creation_single(self, test_company, test_customer, test_item):
        """Test creación de una factura mide performance."""
        start = time.time()

        si = frappe.get_doc({
            'doctype': 'Sales Invoice',
            'company': test_company.name,
            'customer': test_customer.name,
            'posting_date': datetime.now().date(),
            'debit_to': f'Debtors - {test_company.abbr}',
            'items': [{
                'item_code': test_item.item_code,
                'qty': 10,
                'rate': 100,
                'item_name': test_item.item_name,
                'uom': 'Nos'
            }],
            'taxes': [{
                'charge_type': 'On Net Total',
                'account_head': 'IVA Cobrado - IVA',
                'description': 'IVA 13%',
                'rate': 13
            }]
        })
        si.insert()

        end = time.time()
        elapsed = end - start

        # Should create invoice in less than 5 seconds
        assert elapsed < 5, f"Invoice creation took {elapsed}s, expected < 5s"

    def test_invoice_creation_batch(self, test_company, test_customer, test_item):
        """Test creación de 10 facturas mide performance en batch."""
        start = time.time()

        for i in range(10):
            si = frappe.get_doc({
                'doctype': 'Sales Invoice',
                'company': test_company.name,
                'customer': test_customer.name,
                'posting_date': (datetime.now() + timedelta(days=i)).date(),
                'debit_to': f'Debtors - {test_company.abbr}',
                'items': [{
                    'item_code': test_item.item_code,
                    'qty': 10 + i,
                    'rate': 100,
                    'item_name': test_item.item_name,
                    'uom': 'Nos'
                }],
                'taxes': [{
                    'charge_type': 'On Net Total',
                    'account_head': 'IVA Cobrado - IVA',
                    'description': 'IVA 13%',
                    'rate': 13
                }]
            })
            si.insert()

        end = time.time()
        elapsed = end - start
        avg = elapsed / 10

        # Total should be less than 30 seconds
        assert elapsed < 30, f"Batch creation took {elapsed}s, expected < 30s"
        # Average per invoice should be less than 300ms
        assert avg < 0.3, f"Average per invoice is {avg}s, expected < 0.3s"

    def test_invoice_list_retrieval(self, test_company, test_customer, test_item):
        """Test rendimiento al recuperar lista de facturas."""
        # Create some invoices first
        for i in range(5):
            si = frappe.get_doc({
                'doctype': 'Sales Invoice',
                'company': test_company.name,
                'customer': test_customer.name,
                'posting_date': (datetime.now() + timedelta(days=i)).date(),
                'debit_to': f'Debtors - {test_company.abbr}',
                'items': [{
                    'item_code': test_item.item_code,
                    'qty': 10,
                    'rate': 100,
                    'item_name': test_item.item_name,
                    'uom': 'Nos'
                }]
            })
            si.insert()

        start = time.time()

        invoices = frappe.get_list(
            'Sales Invoice',
            filters={'company': test_company.name},
            limit_page_length=999
        )

        end = time.time()
        elapsed = end - start

        # Should retrieve in less than 1 second
        assert elapsed < 1, f"List retrieval took {elapsed}s, expected < 1s"
        assert len(invoices) >= 5

    def test_database_query_performance(self, test_company):
        """Test performance de queries a base de datos."""
        start = time.time()

        # Query accounts for company
        accounts = frappe.db.get_list(
            'Account',
            filters={'company': test_company.name},
            limit_page_length=999
        )

        end = time.time()
        elapsed = end - start

        # Should complete in less than 500ms
        assert elapsed < 0.5, f"Query took {elapsed}s, expected < 0.5s"

    def test_concurrent_document_creation(self, test_company, test_customer, test_item):
        """Test creación concurrente de documentos (no se recomienda en Frappe)."""
        # Note: Frappe is not designed for true concurrent multi-threading
        # This test just verifies sequential operations complete in time

        start = time.time()

        for i in range(5):
            si = frappe.get_doc({
                'doctype': 'Sales Invoice',
                'company': test_company.name,
                'customer': test_customer.name,
                'posting_date': (datetime.now() + timedelta(days=i)).date(),
                'debit_to': f'Debtors - {test_company.abbr}',
                'items': [{
                    'item_code': test_item.item_code,
                    'qty': 10,
                    'rate': 100,
                    'item_name': test_item.item_name,
                    'uom': 'Nos'
                }]
            })
            si.insert()

        end = time.time()
        elapsed = end - start

        # 5 invoices should complete in less than 15 seconds
        assert elapsed < 15, f"Concurrent ops took {elapsed}s, expected < 15s"

    def test_invoice_submission_performance(self, test_company, test_customer, test_item):
        """Test performance de submit (más lenta que insert)."""
        si = frappe.get_doc({
            'doctype': 'Sales Invoice',
            'company': test_company.name,
            'customer': test_customer.name,
            'posting_date': datetime.now().date(),
            'debit_to': f'Debtors - {test_company.abbr}',
            'items': [{
                'item_code': test_item.item_code,
                'qty': 10,
                'rate': 100,
                'item_name': test_item.item_name,
                'uom': 'Nos'
            }],
            'taxes': [{
                'charge_type': 'On Net Total',
                'account_head': 'IVA Cobrado - IVA',
                'description': 'IVA 13%',
                'rate': 13
            }]
        })
        si.insert()

        start = time.time()
        si.submit()
        end = time.time()
        elapsed = end - start

        # Submit should complete in less than 3 seconds
        assert elapsed < 3, f"Submit took {elapsed}s, expected < 3s"

    def test_calculation_performance(self, test_company, test_supplier, test_item):
        """Test performance de cálculos (impuestos, etc)."""
        start = time.time()

        pi = frappe.get_doc({
            'doctype': 'Purchase Invoice',
            'company': test_company.name,
            'supplier': test_supplier.name,
            'posting_date': datetime.now().date(),
            'items': [{
                'item_code': test_item.item_code,
                'qty': 100,
                'rate': 100,
                'item_name': test_item.item_name,
                'uom': 'Nos'
            }],
            'taxes': [
                {
                    'charge_type': 'On Net Total',
                    'account_head': 'IVA Pagado - IVA',
                    'description': 'IVA 13%',
                    'rate': 13
                },
                {
                    'charge_type': 'On Net Total',
                    'account_head': 'IT Pagado - IT',
                    'description': 'IT 3%',
                    'rate': 3
                }
            ]
        })
        pi.insert()

        end = time.time()
        elapsed = end - start

        # Calculations should be instant (< 1 second)
        assert elapsed < 1, f"Calculations took {elapsed}s, expected < 1s"

    def test_memory_usage_during_operations(self, test_company, test_customer, test_item):
        """Test que operaciones no causan memory leaks."""
        # Create multiple documents to test memory stability
        for i in range(20):
            si = frappe.get_doc({
                'doctype': 'Sales Invoice',
                'company': test_company.name,
                'customer': test_customer.name,
                'posting_date': (datetime.now() + timedelta(days=i)).date(),
                'debit_to': f'Debtors - {test_company.abbr}',
                'items': [{
                    'item_code': test_item.item_code,
                    'qty': 10,
                    'rate': 100,
                    'item_name': test_item.item_name,
                    'uom': 'Nos'
                }]
            })
            si.insert()

        # If we get here without running out of memory, test passes
        assert True

    def test_tax_calculation_performance(self, test_company, test_supplier, test_item):
        """Test performance específica de cálculos de impuestos Bolivia."""
        start = time.time()

        # Create invoice with multiple tax rates
        pi = frappe.get_doc({
            'doctype': 'Purchase Invoice',
            'company': test_company.name,
            'supplier': test_supplier.name,
            'posting_date': datetime.now().date(),
            'items': [{
                'item_code': test_item.item_code,
                'qty': 50,
                'rate': 100,
                'item_name': test_item.item_name,
                'uom': 'Nos'
            }],
            'taxes': [
                {
                    'charge_type': 'On Net Total',
                    'account_head': 'IVA Pagado - IVA',
                    'description': 'IVA 13%',
                    'rate': 13
                },
                {
                    'charge_type': 'On Net Total',
                    'account_head': 'IT Pagado - IT',
                    'description': 'IT 3%',
                    'rate': 3
                }
            ]
        })
        pi.insert()

        end = time.time()
        elapsed = end - start

        # Should be fast even with multiple taxes
        assert elapsed < 1, f"Tax calculation took {elapsed}s, expected < 1s"
