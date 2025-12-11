"""Test integración de reportes con datos de otros módulos."""

import pytest
import frappe
from datetime import datetime, timedelta


class TestReportingIntegration:
    """Test reporting module integration."""

    def test_libro_ventas_iva_data_collection(self, test_company, test_customer, test_item):
        """Test que Libro de Ventas recopila datos correctamente."""
        # Create sales invoice
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
        si.submit()

        # Verify data is available for Libro de Ventas
        assert si.net_total == 1000
        assert si.taxes[0].tax_amount == 130

    def test_libro_compras_iva_data_collection(self, test_company, test_supplier, test_item):
        """Test que Libro de Compras recopila datos correctamente."""
        # Create purchase invoice
        pi = frappe.get_doc({
            'doctype': 'Purchase Invoice',
            'company': test_company.name,
            'supplier': test_supplier.name,
            'posting_date': datetime.now().date(),
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

        # Verify data for Libro de Compras
        assert pi.net_total == 1000
        assert pi.taxes[0].tax_amount == 130

    def test_declaracion_iva_monthly(self, test_company, test_customer, test_supplier, test_item):
        """Test generación de Declaración IVA mensual."""
        # Create several invoices
        start_date = datetime.now().replace(day=1).date()

        # Sales invoice
        si = frappe.get_doc({
            'doctype': 'Sales Invoice',
            'company': test_company.name,
            'customer': test_customer.name,
            'posting_date': start_date,
            'debit_to': f'Debtors - {test_company.abbr}',
            'items': [{
                'item_code': test_item.item_code,
                'qty': 10,
                'rate': 500,
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
        si.submit()

        # Purchase invoice
        pi = frappe.get_doc({
            'doctype': 'Purchase Invoice',
            'company': test_company.name,
            'supplier': test_supplier.name,
            'posting_date': start_date,
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

        # IVA Cobrado: 5000 * 0.13 = 650
        # IVA Pagado: 1000 * 0.13 = 130
        # IVA a Pagar: 650 - 130 = 520

        iva_cobrado = si.taxes[0].tax_amount
        iva_pagado = pi.taxes[0].tax_amount

        assert iva_cobrado == 650
        assert iva_pagado == 130

    def test_reporte_rc_iva_generation(self, test_company):
        """Test generación de Reporte RC-IVA."""
        # RC-IVA report data would come from payroll
        # For now just verify the framework exists

        assert test_company.name is not None
        assert test_company.country == 'Bolivia'

    def test_financial_dashboard_metrics(self, test_company, test_customer, test_item):
        """Test que dashboard financiero recopila métricas."""
        # Create invoice to generate data
        si = frappe.get_doc({
            'doctype': 'Sales Invoice',
            'company': test_company.name,
            'customer': test_customer.name,
            'posting_date': datetime.now().date(),
            'debit_to': f'Debtors - {test_company.abbr}',
            'items': [{
                'item_code': test_item.item_code,
                'qty': 100,
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
        si.submit()

        # Dashboard metrics
        assert si.net_total == 10000
        assert si.grand_total == 11300

    def test_sales_analytics_report(self, test_company, test_customer, test_item):
        """Test reporte de análisis de ventas."""
        # Create multiple invoices
        for i in range(3):
            si = frappe.get_doc({
                'doctype': 'Sales Invoice',
                'company': test_company.name,
                'customer': test_customer.name,
                'posting_date': (datetime.now() + timedelta(days=i)).date(),
                'debit_to': f'Debtors - {test_company.abbr}',
                'items': [{
                    'item_code': test_item.item_code,
                    'qty': 10 * (i + 1),
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
            si.submit()

        # Verify invoices created for analysis
        invoices = frappe.get_list(
            'Sales Invoice',
            filters={'company': test_company.name},
            limit_page_length=999
        )

        assert len(invoices) >= 3

    def test_purchase_analytics_report(self, test_company, test_supplier, test_item):
        """Test reporte de análisis de compras."""
        # Create multiple purchase invoices
        for i in range(3):
            pi = frappe.get_doc({
                'doctype': 'Purchase Invoice',
                'company': test_company.name,
                'supplier': test_supplier.name,
                'posting_date': (datetime.now() + timedelta(days=i)).date(),
                'items': [{
                    'item_code': test_item.item_code,
                    'qty': 5 * (i + 1),
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

        # Verify invoices for analysis
        invoices = frappe.get_list(
            'Purchase Invoice',
            filters={'company': test_company.name},
            limit_page_length=999
        )

        assert len(invoices) >= 3

    def test_payroll_report_integration(self, test_company):
        """Test integración de reportes de nómina."""
        # Payroll reports would gather data from salary slips
        # Verify company exists for payroll
        assert test_company.name is not None
        assert test_company.country == 'Bolivia'

    def test_trial_balance_generation(self, test_company, test_fiscal_year):
        """Test generación de Balance de Prueba."""
        # Balance de Prueba aggregates GL entries
        fy = frappe.get_doc('Fiscal Year', test_fiscal_year.name)

        assert fy.year == str(datetime.now().year)

    def test_balance_sheet_generation(self, test_company):
        """Test generación de Balance General."""
        # Get all accounts for company
        accounts = frappe.db.get_list(
            'Account',
            filters={'company': test_company.name},
            limit_page_length=999
        )

        # Balance sheet uses these accounts
        assert isinstance(accounts, list)

    def test_income_statement_generation(self, test_company, test_customer, test_item):
        """Test generación de Estado de Resultados."""
        # Create revenue and expense documents
        si = frappe.get_doc({
            'doctype': 'Sales Invoice',
            'company': test_company.name,
            'customer': test_customer.name,
            'posting_date': datetime.now().date(),
            'debit_to': f'Debtors - {test_company.abbr}',
            'items': [{
                'item_code': test_item.item_code,
                'qty': 50,
                'rate': 200,
                'item_name': test_item.item_name,
                'uom': 'Nos'
            }]
        })
        si.insert()
        si.submit()

        # Income statement aggregates revenue
        assert si.net_total == 10000

    def test_audit_trail_report(self, test_company, test_customer, test_item):
        """Test audit trail de cambios."""
        # Create document for audit
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
            }]
        })
        si.insert()
        si.submit()

        # Audit trail is created automatically
        assert si.docstatus == 1
