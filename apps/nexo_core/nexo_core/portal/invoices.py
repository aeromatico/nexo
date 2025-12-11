# Copyright (c) 2025, Aero and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import format_date
import json


@frappe.whitelist()
def get_my_invoices(filters=None, limit=10, offset=0):
	"""Get invoices for current user"""
	try:
		user = frappe.session.user

		if user == "Guest":
			return {
				"status": "error",
				"message": "Must be logged in",
			}

		# Get customer
		customer = frappe.db.get_value("Customer", {"user_id": user})

		if not customer:
			return {
				"status": "success",
				"invoices": [],
			}

		# Build filter
		filter_conditions = {
			"customer": customer,
			"docstatus": 1,
		}

		if isinstance(filters, str):
			filters = json.loads(filters)

		if filters:
			if filters.get("status") == "paid":
				filter_conditions["outstanding_amount"] = 0
			elif filters.get("status") == "unpaid":
				filter_conditions["outstanding_amount"] = [">", 0]

		# Get invoices
		invoices = frappe.db.get_list(
			"Sales Invoice",
			filters=filter_conditions,
			fields=[
				"name",
				"posting_date",
				"due_date",
				"total",
				"outstanding_amount",
				"status",
			],
			order_by="posting_date desc",
			limit_page_length=limit,
			limit_start=offset,
		)

		# Format dates
		for inv in invoices:
			inv["posting_date"] = format_date(inv.get("posting_date", ""))
			inv["due_date"] = format_date(inv.get("due_date", ""))
			inv["is_paid"] = inv.get("outstanding_amount", 0) == 0

		return {
			"status": "success",
			"invoices": invoices,
		}

	except Exception as e:
		frappe.logger().error(f"Error getting invoices: {str(e)}")
		return {
			"status": "error",
			"message": str(e),
		}


@frappe.whitelist()
def get_invoice_detail(invoice_id):
	"""Get invoice details"""
	try:
		user = frappe.session.user

		if user == "Guest":
			frappe.throw("Must be logged in")

		# Get customer
		customer = frappe.db.get_value("Customer", {"user_id": user})

		# Get invoice
		invoice = frappe.get_doc("Sales Invoice", invoice_id)

		# Check permissions
		if invoice.customer != customer and user not in ["Administrator", "System Manager"]:
			frappe.throw("You do not have permission to view this invoice")

		return {
			"status": "success",
			"invoice": invoice.as_dict(),
		}

	except Exception as e:
		frappe.logger().error(f"Error getting invoice detail: {str(e)}")
		return {
			"status": "error",
			"message": str(e),
		}


@frappe.whitelist()
def download_invoice_pdf(invoice_id):
	"""Download invoice PDF with SIN QR code"""
	try:
		user = frappe.session.user

		if user == "Guest":
			frappe.throw("Must be logged in")

		# Get customer
		customer = frappe.db.get_value("Customer", {"user_id": user})

		# Get invoice
		invoice = frappe.get_doc("Sales Invoice", invoice_id)

		# Check permissions
		if invoice.customer != customer and user not in ["Administrator", "System Manager"]:
			frappe.throw("You do not have permission to download this invoice")

		# Generate PDF
		from frappe.utils.pdf import get_pdf

		# In a real implementation, this would generate a PDF with QR code
		# For now, we'll use the standard PDF generation
		pdf = frappe.utils.get_pdf("Sales Invoice", invoice_id)

		return {
			"status": "success",
			"pdf": pdf,
		}

	except Exception as e:
		frappe.logger().error(f"Error downloading invoice: {str(e)}")
		return {
			"status": "error",
			"message": str(e),
		}


@frappe.whitelist()
def get_invoice_summary():
	"""Get invoice summary for customer"""
	try:
		user = frappe.session.user

		if user == "Guest":
			return {
				"status": "error",
				"message": "Must be logged in",
			}

		# Get customer
		customer = frappe.db.get_value("Customer", {"user_id": user})

		if not customer:
			return {
				"status": "success",
				"summary": {
					"total_invoices": 0,
					"total_amount": 0,
					"outstanding_amount": 0,
					"paid_amount": 0,
				},
			}

		# Get stats
		total_amount = frappe.db.get_value(
			"Sales Invoice",
			{"customer": customer, "docstatus": 1},
			"SUM(total)"
		) or 0

		outstanding_amount = frappe.db.get_value(
			"Sales Invoice",
			{"customer": customer, "docstatus": 1},
			"SUM(outstanding_amount)"
		) or 0

		paid_amount = total_amount - outstanding_amount

		total_invoices = frappe.db.count(
			"Sales Invoice",
			filters={"customer": customer, "docstatus": 1}
		)

		return {
			"status": "success",
			"summary": {
				"total_invoices": total_invoices,
				"total_amount": float(total_amount),
				"outstanding_amount": float(outstanding_amount),
				"paid_amount": float(paid_amount),
			},
		}

	except Exception as e:
		frappe.logger().error(f"Error getting invoice summary: {str(e)}")
		return {
			"status": "error",
			"message": str(e),
		}
