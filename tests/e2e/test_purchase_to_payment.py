"""Test workflow completo: Compra → Factura → Pago"""

import pytest
import frappe
from datetime import datetime, timedelta


class TestPurchaseToPaymentFlow:
    """Test complete purchase workflow from order to payment."""

    def test_complete_purchase_flow(self, test_company, test_supplier, test_item, create_purchase_invoice):
        """Test flujo completo de compra: PO → Receipt → Invoice → Payment."""
        # 1. Crear Purchase Order
        po = frappe.get_doc({
            'doctype': 'Purchase Order',
            'company': test_company.name,
            'supplier': test_supplier.name,
            'posting_date': datetime.now().date(),
            'expected_delivery_date': (datetime.now() + timedelta(days=7)).date(),
            'items': [{
                'item_code': test_item.item_code,
                'qty': 10,
                'rate': 100,
                'item_name': test_item.item_name,
                'uom': 'Nos'
            }]
        })
        po.insert()
        po.submit()

        assert po.docstatus == 1, "Purchase Order should be submitted"
        assert po.status == 'To Receive'

        # 2. Crear Purchase Receipt
        pr = frappe.get_doc({
            'doctype': 'Purchase Receipt',
            'company': test_company.name,
            'supplier': test_supplier.name,
            'posting_date': datetime.now().date(),
            'items': [{
                'item_code': test_item.item_code,
                'qty': 10,
                'rate': 100,
                'item_name': test_item.item_name,
                'uom': 'Nos',
                'purchase_order': po.name
            }]
        })
        pr.insert()
        pr.submit()

        assert pr.docstatus == 1, "Purchase Receipt should be submitted"

        # 3. Crear Purchase Invoice
        pi = create_purchase_invoice(qty=10, rate=100, submit=False)

        assert pi.net_total == 1000, "Net total should be 1000"
        assert pi.docstatus == 0, "Invoice should not be submitted yet"

        pi.submit()

        assert pi.docstatus == 1, "Invoice should be submitted"

        # 4. Verificar cálculos de impuestos Bolivia (IVA 13%)
        pi.reload()
        assert pi.net_total == 1000
        assert any(tax.rate == 13 for tax in pi.taxes), "IVA 13% should be applied"

        total_tax = sum(tax.tax_amount for tax in pi.taxes)
        assert total_tax == 130, f"Total tax should be 130 but got {total_tax}"
        assert pi.grand_total == 1130

        # 5. Crear Payment Entry
        pe = frappe.get_doc({
            'doctype': 'Payment Entry',
            'payment_type': 'Pay',
            'company': test_company.name,
            'party_type': 'Supplier',
            'party': test_supplier.name,
            'posting_date': datetime.now().date(),
            'paid_amount': pi.grand_total,
            'mode_of_payment': 'Bank Transfer',
            'references': [{
                'reference_doctype': 'Purchase Invoice',
                'reference_name': pi.name,
                'allocated_amount': pi.grand_total
            }]
        })
        pe.insert()
        pe.submit()

        assert pe.docstatus == 1, "Payment Entry should be submitted"

        # 6. Verificar estado final
        pi.reload()
        assert pi.outstanding_amount == 0, "Outstanding amount should be 0 after payment"
        assert pi.status == 'Paid'

    def test_partial_purchase_payment(self, test_company, test_supplier, test_item, create_purchase_invoice):
        """Test partial payment on purchase invoice."""
        # Create and submit invoice
        pi = create_purchase_invoice(qty=5, rate=200, submit=True)

        assert pi.grand_total == 1130  # 1000 + 130 tax

        # Make partial payment
        pe = frappe.get_doc({
            'doctype': 'Payment Entry',
            'payment_type': 'Pay',
            'company': test_company.name,
            'party_type': 'Supplier',
            'party': test_supplier.name,
            'posting_date': datetime.now().date(),
            'paid_amount': 565,  # Half of grand total
            'mode_of_payment': 'Bank Transfer',
            'references': [{
                'reference_doctype': 'Purchase Invoice',
                'reference_name': pi.name,
                'allocated_amount': 565
            }]
        })
        pe.insert()
        pe.submit()

        pi.reload()
        assert pi.outstanding_amount == 565, "Outstanding should be half of grand total"

    def test_purchase_with_multiple_items(self, test_company, test_supplier):
        """Test purchase invoice with multiple items."""
        # Create multiple items
        items_data = []
        for i in range(3):
            item = frappe.get_doc({
                'doctype': 'Item',
                'item_code': f'TEST-MULTI-{datetime.now().timestamp()}-{i}',
                'item_name': f'Test Item {i}',
                'item_group': 'Products',
                'stock_uom': 'Nos',
                'is_stock_item': 1,
                'standard_rate': (i + 1) * 100,
            })
            try:
                item.insert()
            except frappe.DuplicateError:
                item = frappe.get_doc('Item', item.item_code)

            items_data.append({
                'item_code': item.item_code,
                'qty': (i + 1) * 5,
                'rate': (i + 1) * 100,
                'item_name': item.item_name,
                'uom': 'Nos'
            })

        # Create purchase invoice
        pi = frappe.get_doc({
            'doctype': 'Purchase Invoice',
            'company': test_company.name,
            'supplier': test_supplier.name,
            'posting_date': datetime.now().date(),
            'items': items_data,
            'taxes': [{
                'charge_type': 'On Net Total',
                'account_head': 'IVA Pagado - IVA',
                'description': 'IVA 13%',
                'rate': 13
            }]
        })
        pi.insert()
        pi.submit()

        assert len(pi.items) == 3
        # Net total: (5*100) + (10*200) + (15*300) = 500 + 2000 + 4500 = 7000
        assert pi.net_total == 7000
        # Tax: 7000 * 0.13 = 910
        assert pi.taxes[0].tax_amount == 910
        assert pi.grand_total == 7910

    def test_purchase_invoice_cancellation(self, test_company, test_supplier, test_item, create_purchase_invoice):
        """Test cancellation of purchase invoice."""
        pi = create_purchase_invoice(qty=10, rate=100, submit=True)

        assert pi.docstatus == 1

        # Cancel the invoice
        pi.cancel()

        pi.reload()
        assert pi.docstatus == 2, "Invoice should be cancelled"

    def test_purchase_with_discount(self, test_company, test_supplier, test_item):
        """Test purchase invoice with discount."""
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
                'uom': 'Nos',
                'discount_percentage': 10  # 10% discount
            }],
            'taxes': [{
                'charge_type': 'On Net Total',
                'account_head': 'IVA Pagado - IVA',
                'description': 'IVA 13%',
                'rate': 13
            }]
        })
        pi.insert()

        # Net total with discount: 1000 - 100 = 900
        assert pi.net_total == 900
        # Tax on discounted amount: 900 * 0.13 = 117
        assert pi.taxes[0].tax_amount == 117
        assert pi.grand_total == 1017

        pi.submit()
        assert pi.docstatus == 1
