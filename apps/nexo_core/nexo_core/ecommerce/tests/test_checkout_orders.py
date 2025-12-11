# Copyright (c) 2025, Aero and contributors
# For license information, please see license.txt

import frappe
import unittest
import json
from nexo_core.ecommerce.checkout import create_order
from nexo_core.ecommerce.orders import get_my_orders, get_order_detail, cancel_order


class TestCheckoutAndOrders(unittest.TestCase):
	"""Test checkout and order functionality"""

	def setUp(self):
		"""Setup test data"""
		# Create test item
		if not frappe.db.exists("Item", "TEST-ITEM-CHECKOUT"):
			item = frappe.new_doc("Item")
			item.item_code = "TEST-ITEM-CHECKOUT"
			item.item_name = "Test Item for Checkout"
			item.item_group = "Test"
			item.standard_rate = 100.00
			item.uom = "Nos"
			item.insert(ignore_permissions=True)

		# Create test company if not exists
		if not frappe.db.exists("Company", "Test Company"):
			company = frappe.new_doc("Company")
			company.company_name = "Test Company"
			company.company_code = "TEST"
			company.country = "Bolivia"
			company.insert(ignore_permissions=True)

		# Create ecommerce settings
		if not frappe.db.exists("Ecommerce Settings", "Test Company"):
			settings = frappe.new_doc("Ecommerce Settings")
			settings.company = "Test Company"
			settings.enabled = 1
			settings.store_name = "Test Store"
			settings.default_currency = "BOB"
			settings.insert(ignore_permissions=True)

	def test_create_order(self):
		"""Test creating order"""
		cart_items = [
			{
				"item_code": "TEST-ITEM-CHECKOUT",
				"qty": 2,
				"rate": 100,
			}
		]

		result = create_order(
			company="Test Company",
			cart_items=json.dumps(cart_items),
			shipping_address="123 Test Street",
			payment_method="QR Simple"
		)

		self.assertEqual(result.get("status"), "success")
		self.assertIn("order_id", result)

	def test_create_order_empty_cart(self):
		"""Test creating order with empty cart"""
		result = create_order(
			company="Test Company",
			cart_items=[],
			shipping_address="123 Test Street",
		)

		self.assertEqual(result.get("status"), "error")

	def test_create_order_no_shipping_address(self):
		"""Test creating order without shipping address"""
		cart_items = [
			{
				"item_code": "TEST-ITEM-CHECKOUT",
				"qty": 1,
				"rate": 100,
			}
		]

		result = create_order(
			company="Test Company",
			cart_items=json.dumps(cart_items),
			shipping_address="",
		)

		self.assertEqual(result.get("status"), "error")

	def test_order_calculations(self):
		"""Test order total calculations"""
		cart_items = [
			{
				"item_code": "TEST-ITEM-CHECKOUT",
				"qty": 1,
				"rate": 100,
			}
		]

		result = create_order(
			company="Test Company",
			cart_items=json.dumps(cart_items),
			shipping_address="123 Test Street",
			shipping_cost=10,
		)

		self.assertEqual(result.get("status"), "success")

		order_data = result.get("order_data", {})
		# Subtotal: 100, Tax (13%): 13, Shipping: 10, Total: 123
		self.assertEqual(order_data.get("subtotal"), 100)
		self.assertAlmostEqual(order_data.get("tax_amount"), 13, places=0)
		self.assertEqual(order_data.get("shipping_cost"), 10)
		self.assertAlmostEqual(order_data.get("total"), 123, places=0)


class TestOrderOperations(unittest.TestCase):
	"""Test order operations"""

	def setUp(self):
		"""Setup test data"""
		# Create online order
		if not frappe.db.exists("Online Order", "OO-TEST-001"):
			order = frappe.new_doc("Online Order")
			order.name = "OO-TEST-001"
			order.company = "Test Company"
			order.customer = ""
			order.posting_date = frappe.utils.today()
			order.order_date = frappe.utils.now()
			order.status = "Pending"
			order.payment_status = "Pending"
			order.shipping_address = "123 Test Street"
			order.subtotal = 100
			order.tax_amount = 13
			order.shipping_cost = 0
			order.total = 113

			# Add item
			order.append("items", {
				"item_code": "TEST-ITEM-CHECKOUT",
				"item_name": "Test Item",
				"qty": 1,
				"rate": 100,
				"amount": 100,
			})

			order.insert(ignore_permissions=True)

	def test_cancel_order(self):
		"""Test cancelling order"""
		result = cancel_order("OO-TEST-001", reason="Customer requested")

		self.assertEqual(result.get("status"), "success")


if __name__ == "__main__":
	unittest.main()
