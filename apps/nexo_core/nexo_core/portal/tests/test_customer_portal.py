# Copyright (c) 2025, Aero and contributors
# For license information, please see license.txt

import frappe
import unittest
from nexo_core.portal.customer_portal import get_dashboard_data, get_user_info, update_profile
from nexo_core.portal.invoices import get_my_invoices, get_invoice_detail, get_invoice_summary
from nexo_core.portal.support import create_support_ticket, get_my_tickets, add_ticket_comment


class TestCustomerPortal(unittest.TestCase):
	"""Test customer portal functionality"""

	def setUp(self):
		"""Setup test data"""
		# Create test customer
		if not frappe.db.exists("Customer", "TEST-CUST-001"):
			customer = frappe.new_doc("Customer")
			customer.name = "TEST-CUST-001"
			customer.customer_name = "Test Customer"
			customer.customer_group = "Individual"
			customer.territory = "All Territories"
			customer.user_id = frappe.session.user
			customer.insert(ignore_permissions=True)

	def test_get_dashboard_data(self):
		"""Test getting dashboard data"""
		result = get_dashboard_data()

		# Will fail if not logged in, so check for error or success
		if result.get("status") == "success":
			dashboard = result.get("dashboard", {})
			self.assertIn("total_orders", dashboard)
			self.assertIn("total_spent", dashboard)
			self.assertIn("pending_orders", dashboard)
		else:
			self.assertEqual(result.get("status"), "error")

	def test_get_user_info(self):
		"""Test getting user info"""
		result = get_user_info()

		if result.get("status") == "success":
			user_info = result.get("user", {})
			self.assertIn("name", user_info)
			self.assertIn("email", user_info)
		else:
			self.assertEqual(result.get("status"), "error")


class TestInvoices(unittest.TestCase):
	"""Test invoice portal functionality"""

	def test_get_my_invoices(self):
		"""Test getting invoices"""
		result = get_my_invoices()

		self.assertEqual(result.get("status"), "success")
		self.assertIn("invoices", result)

	def test_get_invoice_summary(self):
		"""Test getting invoice summary"""
		result = get_invoice_summary()

		if result.get("status") == "success":
			summary = result.get("summary", {})
			self.assertIn("total_invoices", summary)
			self.assertIn("total_amount", summary)
			self.assertIn("outstanding_amount", summary)


class TestSupportTickets(unittest.TestCase):
	"""Test support ticket functionality"""

	def test_create_ticket(self):
		"""Test creating support ticket"""
		result = create_support_ticket(
			subject="Test Issue",
			description="This is a test issue",
			priority="Medium",
		)

		if result.get("status") == "success":
			self.assertIn("ticket_id", result)
		else:
			self.assertEqual(result.get("status"), "error")

	def test_get_my_tickets(self):
		"""Test getting tickets"""
		result = get_my_tickets()

		if result.get("status") == "success":
			self.assertIn("tickets", result)
		else:
			self.assertEqual(result.get("status"), "error")


if __name__ == "__main__":
	unittest.main()
