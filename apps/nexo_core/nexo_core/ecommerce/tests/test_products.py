# Copyright (c) 2025, Aero and contributors
# For license information, please see license.txt

import frappe
import unittest
from nexo_core.ecommerce.products import get_products, get_product_detail, search_products, get_categories, get_featured_products


class TestProducts(unittest.TestCase):
	"""Test product functionality"""

	def setUp(self):
		"""Setup test data"""
		# Create test items
		for i in range(1, 4):
			if not frappe.db.exists("Item", f"TEST-PROD-{i:03d}"):
				item = frappe.new_doc("Item")
				item.item_code = f"TEST-PROD-{i:03d}"
				item.item_name = f"Test Product {i}"
				item.item_group = "Test"
				item.description = f"Test product description {i}"
				item.standard_rate = 100 * i
				item.uom = "Nos"
				item.insert(ignore_permissions=True)

	def test_get_products(self):
		"""Test getting products"""
		result = get_products(limit=10)

		self.assertEqual(result.get("status"), "success")
		self.assertIn("products", result)
		self.assertGreater(len(result.get("products", [])), 0)

	def test_get_product_detail(self):
		"""Test getting product detail"""
		result = get_product_detail("TEST-PROD-001")

		self.assertEqual(result.get("status"), "success")
		product = result.get("product", {})
		self.assertEqual(product.get("code"), "TEST-PROD-001")
		self.assertEqual(product.get("name"), "Test Product 1")

	def test_search_products(self):
		"""Test searching products"""
		result = search_products("Test")

		self.assertEqual(result.get("status"), "success")
		self.assertGreater(result.get("count"), 0)

	def test_search_products_short_query(self):
		"""Test search with short query"""
		result = search_products("t")

		self.assertEqual(result.get("status"), "error")

	def test_get_categories(self):
		"""Test getting categories"""
		result = get_categories()

		self.assertEqual(result.get("status"), "success")
		self.assertIn("categories", result)

	def test_get_featured_products(self):
		"""Test getting featured products"""
		result = get_featured_products(limit=5)

		self.assertEqual(result.get("status"), "success")
		self.assertIn("products", result)

	def test_product_not_found(self):
		"""Test getting non-existent product"""
		result = get_product_detail("NONEXISTENT-PRODUCT")

		self.assertEqual(result.get("status"), "error")


if __name__ == "__main__":
	unittest.main()
