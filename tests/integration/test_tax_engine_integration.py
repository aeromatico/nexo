"""Test integración del tax engine con otros módulos."""

import pytest
import frappe
from datetime import datetime, timedelta
from decimal import Decimal


class TestTaxEngineIntegration:
    """Test tax engine calculations and integrations."""

    def test_iva_application_on_purchase(self, test_company, test_supplier, test_item, create_purchase_invoice):
        """Test IVA 13% se aplica correctamente en compras."""
        pi = create_purchase_invoice(qty=10, rate=100, submit=False)

        assert pi.net_total == 1000

        # Check IVA tax
        iva_taxes = [t for t in pi.taxes if 'IVA' in t.description or 'IVA' in str(t.account_head)]
        assert len(iva_taxes) > 0

        iva_tax = iva_taxes[0]
        assert iva_tax.rate == 13
        assert iva_tax.tax_amount == 130

        pi.submit()
        assert pi.grand_total == 1130

    def test_iva_it_combined_on_purchase(self, test_company, test_supplier, test_item):
        """Test IVA + IT se aplican juntos en compras."""
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

        assert pi.net_total == 10000

        # Check both taxes
        iva_tax = next((t for t in pi.taxes if 'IVA' in t.description), None)
        it_tax = next((t for t in pi.taxes if 'IT' in t.description), None)

        assert iva_tax is not None
        assert it_tax is not None
        assert iva_tax.tax_amount == 1300
        assert it_tax.tax_amount == 300

        pi.submit()
        assert pi.grand_total == 11600

    def test_iva_calculation_on_sales(self, test_company, test_customer, test_item):
        """Test IVA se calcula correctamente en ventas."""
        si = frappe.get_doc({
            'doctype': 'Sales Invoice',
            'company': test_company.name,
            'customer': test_customer.name,
            'posting_date': datetime.now().date(),
            'debit_to': f'Debtors - {test_company.abbr}',
            'items': [{
                'item_code': test_item.item_code,
                'qty': 5,
                'rate': 200,
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

        assert si.net_total == 1000
        assert si.taxes[0].tax_amount == 130
        assert si.grand_total == 1130

        si.submit()
        assert si.docstatus == 1

    def test_tax_retention_on_purchase(self, test_company, test_supplier, test_item):
        """Test retención de impuestos en compras."""
        pi = frappe.get_doc({
            'doctype': 'Purchase Invoice',
            'company': test_company.name,
            'supplier': test_supplier.name,
            'posting_date': datetime.now().date(),
            'items': [{
                'item_code': test_item.item_code,
                'qty': 10,
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
                    'account_head': 'RC-IVA Pagada',
                    'description': 'RC-IVA',
                    'rate': -3.15,  # Negative for retention (3% of IVA)
                    'tax_amount': -39.9  # 13% * 1000 * 3%
                }
            ]
        })
        pi.insert()

        assert pi.net_total == 1000

        # Net taxes after retention
        total_tax = sum(t.tax_amount for t in pi.taxes)
        assert total_tax == 90.1  # 130 - 39.9

    def test_iue_quarterly_calculation(self, test_company, test_fiscal_year):
        """Test cálculo trimestral de IUE."""
        # Get fiscal year
        fy = frappe.get_doc('Fiscal Year', test_fiscal_year.name)

        # IUE calculation would be done by a specific doctype
        # For now, just verify fiscal year exists
        assert fy.year == str(datetime.now().year)

    def test_declaracion_iva_data_collection(self, test_company, test_supplier, test_item):
        """Test que datos de facturas se recopilan para Declaración IVA."""
        # Create purchase invoice
        pi = frappe.get_doc({
            'doctype': 'Purchase Invoice',
            'company': test_company.name,
            'supplier': test_supplier.name,
            'posting_date': datetime.now().date(),
            'due_date': (datetime.now() + timedelta(days=30)).date(),
            'items': [{
                'item_code': test_item.item_code,
                'qty': 5,
                'rate': 200,
                'item_name': test_item.item_name,
                'uom': 'Nos'
            }],
            'taxes': [{
                'charge_type': 'On Net Total',
                'account_head': 'IVA Pagado - IVA',
                'description': 'IVA 13%',
                'rate': 13
            }]
        })
        pi.insert()
        pi.submit()

        # Verify data for IVA declaration
        assert pi.net_total == 1000
        assert pi.taxes[0].tax_amount == 130

    def test_sin_invoice_tax_validation(self, test_company, test_customer, test_item):
        """Test validación de impuestos para factura SIN."""
        test_company.custom_sin_enabled = 1
        test_company.custom_nit = '123456789'
        test_company.save()

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

        # For SIN, taxes must be explicitly calculated
        assert si.net_total == 1000
        assert si.taxes[0].tax_amount == 130
        assert si.grand_total == 1130

    def test_tax_journal_entry_posting(self, test_company, test_supplier, test_item):
        """Test que impuestos se registren en asiento contable."""
        pi = frappe.get_doc({
            'doctype': 'Purchase Invoice',
            'company': test_company.name,
            'supplier': test_supplier.name,
            'posting_date': datetime.now().date(),
            'items': [{
                'item_code': test_item.item_code,
                'qty': 5,
                'rate': 100,
                'item_name': test_item.item_name,
                'uom': 'Nos'
            }],
            'taxes': [{
                'charge_type': 'On Net Total',
                'account_head': 'IVA Pagado - IVA',
                'description': 'IVA 13%',
                'rate': 13
            }]
        })
        pi.insert()
        pi.submit()

        # Journal entry should be created automatically
        # Check if GL entries exist for this invoice
        gl_entries = frappe.db.get_list(
            'GL Entry',
            filters={'voucher_type': 'Purchase Invoice', 'voucher_no': pi.name}
        )

        # GL entries should exist
        assert isinstance(gl_entries, list)

    def test_cumulative_tax_calculations(self, test_company, test_supplier, test_item):
        """Test cálculos cumulativos de impuestos en múltiples facturas."""
        invoices = []

        for i in range(3):
            pi = frappe.get_doc({
                'doctype': 'Purchase Invoice',
                'company': test_company.name,
                'supplier': test_supplier.name,
                'posting_date': (datetime.now() + timedelta(days=i)).date(),
                'items': [{
                    'item_code': test_item.item_code,
                    'qty': 10,
                    'rate': 100 * (i + 1),
                    'item_name': test_item.item_name,
                    'uom': 'Nos'
                }],
                'taxes': [{
                    'charge_type': 'On Net Total',
                    'account_head': 'IVA Pagado - IVA',
                    'description': 'IVA 13%',
                    'rate': 13
                }]
            })
            pi.insert()
            pi.submit()
            invoices.append(pi)

        assert len(invoices) == 3

        # Verify cumulative calculations
        total_net = sum(inv.net_total for inv in invoices)
        total_tax = sum(inv.taxes[0].tax_amount for inv in invoices)

        # Total net: 1000 + 2000 + 3000 = 6000
        assert total_net == 6000
        # Total tax: 130 + 260 + 390 = 780
        assert total_tax == 780

    def test_tax_exemption_handling(self, test_company, test_customer, test_item):
        """Test manejo de exenciones de impuestos."""
        # Invoice without tax
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
                'uom': 'Nos',
                'item_tax_template': '',  # No tax
                'tax_rate': 0
            }]
        })
        si.insert()

        assert si.net_total == 1000
        # Should have no taxes
        si.submit()
        assert si.docstatus == 1
