# Copyright (c) 2025, Aero and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, now
import json


class OnlineOrder(Document):
	"""Online Order DocType"""

	def validate(self):
		"""Validate online order"""
		if not self.items:
			frappe.throw("Order must have at least one item")

		# Validate item availability
		for item in self.items:
			if not frappe.db.exists("Item", item.item_code):
				frappe.throw(f"Item {item.item_code} does not exist")

		# Calculate totals
		self.calculate_totals()

		# Set dates
		if not self.order_date:
			self.order_date = now()

		if not self.posting_date:
			self.posting_date = nowdate()

	def calculate_totals(self):
		"""Calculate subtotal, tax, and total"""
		self.subtotal = 0
		self.tax_amount = 0

		for item in self.items:
			item.amount = item.qty * item.rate
			self.subtotal += item.amount

		# Apply 13% tax (Bolivia)
		self.tax_amount = self.subtotal * 0.13
		self.total = self.subtotal + self.tax_amount + (self.shipping_cost or 0)

	def before_submit(self):
		"""Before submit"""
		if self.status != "Pending":
			frappe.throw("Can only submit Pending orders")

	def on_submit(self):
		"""After order submission"""
		# Send notification to customer if enabled
		settings = frappe.get_doc("Ecommerce Settings", self.company)
		if settings.notify_customer_on_order and self.customer:
			send_order_confirmation(self)

		# Auto-create invoice if payment is already confirmed
		if settings.auto_create_invoice and self.payment_status == "Paid":
			create_sales_invoice_from_order(self)

	def on_trash(self):
		"""Before deleting"""
		if self.sales_invoice:
			frappe.throw("Cannot delete order that has a linked invoice")

	@frappe.whitelist()
	def cancel_order(self, reason=""):
		"""Cancel the order"""
		if self.status in ["Shipped", "Delivered"]:
			frappe.throw("Cannot cancel a shipped or delivered order")

		self.status = "Cancelled"
		self.save()

		# Log cancellation
		frappe.logger().info(f"Order {self.name} cancelled. Reason: {reason}")

	@frappe.whitelist()
	def update_payment_status(self, payment_status, reference=""):
		"""Update payment status"""
		self.payment_status = payment_status
		if reference:
			self.payment_reference = reference

		if payment_status == "Paid":
			self.status = "Confirmed"

		self.save()

		# Auto-create invoice if enabled
		settings = frappe.get_doc("Ecommerce Settings", self.company)
		if settings.auto_create_invoice and payment_status == "Paid":
			create_sales_invoice_from_order(self)


def create_sales_invoice_from_order(order):
	"""Create Sales Invoice from Online Order"""
	if order.sales_invoice:
		return  # Already created

	try:
		invoice = frappe.new_doc("Sales Invoice")
		invoice.company = order.company
		invoice.customer = order.customer or "Guest Customer"
		invoice.posting_date = order.posting_date
		invoice.due_date = order.posting_date

		# Add items
		for item in order.items:
			invoice.append("items", {
				"item_code": item.item_code,
				"item_name": item.item_name,
				"qty": item.qty,
				"uom": item.uom or "Nos",
				"rate": item.rate,
				"amount": item.amount,
				"description": item.description,
			})

		# Set totals
		invoice.base_total = order.subtotal
		invoice.base_net_total = order.subtotal
		invoice.total_qty = sum(item.qty for item in order.items)

		# Add shipping as separate row if applicable
		if order.shipping_cost:
			invoice.append("items", {
				"item_code": "SHIPPING",
				"item_name": "Shipping Cost",
				"qty": 1,
				"rate": order.shipping_cost,
				"amount": order.shipping_cost,
			})

		invoice.insert()
		invoice.submit()

		# Link invoice to order
		order.sales_invoice = invoice.name
		order.save()

		frappe.logger().info(f"Sales Invoice {invoice.name} created from Online Order {order.name}")

	except Exception as e:
		frappe.logger().error(f"Error creating invoice from order {order.name}: {str(e)}")
		frappe.throw(f"Error creating invoice: {str(e)}")


def send_order_confirmation(order):
	"""Send order confirmation email to customer"""
	try:
		if not order.customer:
			return

		customer_doc = frappe.get_doc("Customer", order.customer)
		if not customer_doc.email:
			return

		# Send email
		frappe.sendmail(
			recipients=[customer_doc.email],
			subject=f"Order Confirmation - {order.name}",
			message=f"Your order {order.name} has been confirmed.\n\nTotal: {order.total}\n\nThank you for your purchase!",
			reference_doctype="Online Order",
			reference_name=order.name,
		)

		frappe.logger().info(f"Order confirmation email sent to {customer_doc.email}")

	except Exception as e:
		frappe.logger().error(f"Error sending confirmation email: {str(e)}")
