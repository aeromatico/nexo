# Copyright (c) 2025, Aero and contributors
# For license information, please see license.txt

import frappe
import unittest
from frappe.test_runner import make_test_objects
from nexo_core.ecommerce.cart import add_to_cart, remove_from_cart, get_cart, update_cart, clear_cart, get_cart_summary


class TestCart(unittest.TestCase):
	"""Test cart functionality"""

	def setUp(self):
		"""Setup test data"""
		# Create test item
		if not frappe.db.exists("Item", "TEST-ITEM-001"):
			item = frappe.new_doc("Item")
			item.item_code = "TEST-ITEM-001"
			item.item_name = "Test Item 1"
			item.item_group = "Test Group"
			item.standard_rate = 100.00
			item.uom = "Nos"
			item.insert(ignore_permissions=True)

	def tearDown(self):
		"""Cleanup"""
		frappe.cache().delete_key("cart:test-session")
		frappe.cache().delete_key("cart:test-user")

	def test_add_to_cart(self):
		"""Test adding item to cart"""
		result = add_to_cart("TEST-ITEM-001", qty=1)

		self.assertEqual(result.get("status"), "success")
		self.assertIn("TEST-ITEM-001", result.get("cart", {}))

	def test_remove_from_cart(self):
		"""Test removing item from cart"""
		# Add item first
		add_to_cart("TEST-ITEM-001", qty=1)

		# Remove item
		result = remove_from_cart("TEST-ITEM-001")

		self.assertEqual(result.get("status"), "success")
		self.assertNotIn("TEST-ITEM-001", result.get("cart", {}))

	def test_update_cart_quantity(self):
		"""Test updating cart quantity"""
		# Add item
		add_to_cart("TEST-ITEM-001", qty=1)

		# Update quantity
		result = update_cart("TEST-ITEM-001", qty=5)

		self.assertEqual(result.get("status"), "success")
		cart = result.get("cart", {})
		self.assertEqual(cart.get("TEST-ITEM-001", {}).get("qty"), 5)

	def test_get_cart(self):
		"""Test getting cart"""
		# Add items
		add_to_cart("TEST-ITEM-001", qty=2)

		result = get_cart()

		self.assertEqual(result.get("status"), "success")
		self.assertIn("TEST-ITEM-001", result.get("cart", {}))

	def test_get_cart_summary(self):
		"""Test cart summary with totals"""
		# Add items
		add_to_cart("TEST-ITEM-001", qty=2)

		result = get_cart_summary()

		self.assertEqual(result.get("status"), "success")
		self.assertEqual(result.get("item_count"), 1)
		self.assertGreater(result.get("subtotal"), 0)
		self.assertGreater(result.get("tax_amount"), 0)
		self.assertGreater(result.get("total"), 0)

	def test_clear_cart(self):
		"""Test clearing cart"""
		# Add items
		add_to_cart("TEST-ITEM-001", qty=1)

		# Clear cart
		result = clear_cart()

		self.assertEqual(result.get("status"), "success")

		# Verify cart is empty
		cart = get_cart().get("cart", {})
		self.assertEqual(len(cart), 0)

	def test_invalid_quantity(self):
		"""Test invalid quantity"""
		result = add_to_cart("TEST-ITEM-001", qty=0)

		self.assertEqual(result.get("status"), "error")

	def test_nonexistent_item(self):
		"""Test adding non-existent item"""
		result = add_to_cart("NONEXISTENT-ITEM", qty=1)

		self.assertEqual(result.get("status"), "error")


if __name__ == "__main__":
	unittest.main()
