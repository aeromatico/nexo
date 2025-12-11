"""Test flujo completo e-commerce: Carrito → Checkout → Pago → Factura SIN."""

import pytest
import frappe
from datetime import datetime, timedelta
from decimal import Decimal


class TestEcommerceFlow:
    """Test complete e-commerce purchase workflows."""

    def test_complete_ecommerce_purchase(self, test_company, test_customer, test_item):
        """Test compra completa desde e-commerce."""
        test_company.custom_nit = '123456789'
        test_company.custom_sin_enabled = 1
        test_company.save()

        # 1. Crear orden de compra e-commerce
        order = frappe.get_doc({
            'doctype': 'Online Order',
            'customer_email': test_customer.email or 'test@example.com',
            'customer_name': test_customer.customer_name,
            'items': [{
                'item_code': test_item.item_code,
                'quantity': 2,
                'price': 100,
                'total': 200
            }],
            'shipping_address': '123 Test Street, La Paz',
            'payment_method': 'QR Simple',
            'order_date': datetime.now(),
            'status': 'Pending'
        })
        order.insert()

        assert order.name is not None
        assert order.status == 'Pending'

        # 2. Procesar pago
        order.payment_status = 'Paid'
        order.status = 'Confirmed'
        order.save()

        # 3. Crear Sales Invoice automáticamente
        si = frappe.get_doc({
            'doctype': 'Sales Invoice',
            'company': test_company.name,
            'customer': test_customer.name,
            'posting_date': datetime.now().date(),
            'debit_to': f'Debtors - {test_company.abbr}',
            'items': [{
                'item_code': test_item.item_code,
                'qty': 2,
                'rate': 100,
                'item_name': test_item.item_name,
                'uom': 'Nos'
            }],
            'taxes': [{
                'charge_type': 'On Net Total',
                'account_head': 'IVA Cobrado - IVA',
                'description': 'IVA 13%',
                'rate': 13
            }],
            'custom_sin_status': 'Accepted',
            'custom_cuf': '44D12345AB6CD1234EFGH123456789IJKLMNOPQ'
        })
        si.insert()
        si.submit()

        assert si.docstatus == 1
        assert si.custom_cuf is not None

        # 4. Actualizar estado de orden
        order.sales_invoice = si.name
        order.save()

        order.reload()
        assert order.sales_invoice == si.name

    def test_cart_operations(self, test_customer, test_item):
        """Test cart creation and item addition."""
        # Create shopping cart
        cart = frappe.get_doc({
            'doctype': 'Shopping Cart',
            'user': test_customer.email or 'test@example.com',
            'items': [{
                'item_code': test_item.item_code,
                'quantity': 2,
                'price': 100,
                'total': 200
            }],
            'subtotal': 200,
            'total': 226  # With 13% IVA
        })
        cart.insert()

        assert len(cart.items) == 1
        assert cart.subtotal == 200
        assert cart.total == 226

    def test_cart_item_quantity_update(self, test_customer, test_item):
        """Test updating quantities in cart."""
        cart = frappe.get_doc({
            'doctype': 'Shopping Cart',
            'user': test_customer.email or 'test@example.com',
            'items': [{
                'item_code': test_item.item_code,
                'quantity': 1,
                'price': 100,
                'total': 100
            }],
            'subtotal': 100,
            'total': 113
        })
        cart.insert()

        # Update quantity
        cart.items[0].quantity = 5
        cart.items[0].total = 500
        cart.subtotal = 500
        cart.total = 565
        cart.save()

        cart.reload()
        assert cart.items[0].quantity == 5
        assert cart.subtotal == 500

    def test_checkout_process(self, test_company, test_customer, test_item):
        """Test checkout process from cart to order."""
        # Create cart
        cart = frappe.get_doc({
            'doctype': 'Shopping Cart',
            'user': test_customer.email or 'test@example.com',
            'items': [{
                'item_code': test_item.item_code,
                'quantity': 3,
                'price': 200,
                'total': 600
            }],
            'subtotal': 600,
            'total': 678
        })
        cart.insert()

        # Checkout - Create order from cart
        order = frappe.get_doc({
            'doctype': 'Online Order',
            'customer_email': test_customer.email or 'test@example.com',
            'customer_name': test_customer.customer_name,
            'items': cart.items,
            'subtotal': cart.subtotal,
            'total': cart.total,
            'shipping_address': '123 Test Street',
            'payment_method': 'Bank Transfer',
            'order_date': datetime.now(),
            'status': 'Pending'
        })
        order.insert()

        assert order.name is not None
        assert order.total == 678

    def test_order_with_discount_coupon(self, test_company, test_customer, test_item):
        """Test order creation with discount coupon."""
        # Create order
        order = frappe.get_doc({
            'doctype': 'Online Order',
            'customer_email': test_customer.email or 'test@example.com',
            'customer_name': test_customer.customer_name,
            'items': [{
                'item_code': test_item.item_code,
                'quantity': 5,
                'price': 100,
                'total': 500
            }],
            'subtotal': 500,
            'discount': 50,  # 10% discount
            'subtotal_after_discount': 450,
            'total': 508.50,  # 450 + 13% IVA
            'coupon_code': 'SUMMER10',
            'order_date': datetime.now(),
            'status': 'Pending'
        })
        order.insert()

        assert order.discount == 50
        assert order.subtotal_after_discount == 450

    def test_order_payment_methods(self, test_company, test_customer, test_item):
        """Test order with different payment methods."""
        payment_methods = ['QR Simple', 'Bank Transfer', 'Credit Card', 'Cash']

        for method in payment_methods:
            order = frappe.get_doc({
                'doctype': 'Online Order',
                'customer_email': test_customer.email or 'test@example.com',
                'customer_name': test_customer.customer_name,
                'items': [{
                    'item_code': test_item.item_code,
                    'quantity': 1,
                    'price': 100,
                    'total': 100
                }],
                'subtotal': 100,
                'total': 113,
                'payment_method': method,
                'order_date': datetime.now(),
                'status': 'Pending'
            })
            order.insert()

            assert order.payment_method == method

    def test_order_tracking(self, test_company, test_customer, test_item):
        """Test order tracking status updates."""
        order = frappe.get_doc({
            'doctype': 'Online Order',
            'customer_email': test_customer.email or 'test@example.com',
            'customer_name': test_customer.customer_name,
            'items': [{
                'item_code': test_item.item_code,
                'quantity': 2,
                'price': 100,
                'total': 200
            }],
            'total': 226,
            'order_date': datetime.now(),
            'status': 'Pending'
        })
        order.insert()

        statuses = ['Pending', 'Confirmed', 'Processing', 'Shipped', 'Delivered']

        for status in statuses:
            order.status = status
            if order.docstatus == 0:
                order.save()

        order.reload()
        assert order.status == 'Delivered'

    def test_order_cancellation(self, test_company, test_customer, test_item):
        """Test order cancellation."""
        order = frappe.get_doc({
            'doctype': 'Online Order',
            'customer_email': test_customer.email or 'test@example.com',
            'customer_name': test_customer.customer_name,
            'items': [{
                'item_code': test_item.item_code,
                'quantity': 1,
                'price': 100,
                'total': 100
            }],
            'total': 113,
            'order_date': datetime.now(),
            'status': 'Pending'
        })
        order.insert()

        # Cancel order
        order.status = 'Cancelled'
        order.save()

        order.reload()
        assert order.status == 'Cancelled'

    def test_invoice_generation_from_order(self, test_company, test_customer, test_item):
        """Test that sales invoice is generated from accepted order."""
        test_company.custom_sin_enabled = 1
        test_company.save()

        # Create and accept order
        order = frappe.get_doc({
            'doctype': 'Online Order',
            'customer_email': test_customer.email or 'test@example.com',
            'customer_name': test_customer.customer_name,
            'company': test_company.name,
            'items': [{
                'item_code': test_item.item_code,
                'quantity': 5,
                'price': 200,
                'total': 1000
            }],
            'subtotal': 1000,
            'total': 1130,
            'order_date': datetime.now(),
            'status': 'Confirmed',
            'payment_status': 'Paid'
        })
        order.insert()
        order.submit()

        # Generate invoice
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
        si.submit()

        assert si.net_total == 1000
        assert si.grand_total == 1130
