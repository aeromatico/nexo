# Copyright (c) 2025, Aero and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.utils import now, nowdate
from nexo_core.ecommerce.cart import get_cart_storage_key
from nexo_core.doctype.ecommerce_settings.ecommerce_settings import get_ecommerce_settings


@frappe.whitelist()
def create_order(company, cart_items, shipping_address, billing_address="", payment_method="QR Simple", **kwargs):
	"""
	Create Online Order from cart
	1. Validates stock
	2. Creates Online Order (status: Pending)
	3. Returns order_id and payment_url
	"""
	try:
		# Validate inputs
		if not company:
			frappe.throw("Company is required")

		if not cart_items:
			frappe.throw("Cart is empty")

		if not shipping_address:
			frappe.throw("Shipping address is required")

		# Parse cart items if string
		if isinstance(cart_items, str):
			cart_items = json.loads(cart_items)

		# Get current user (can be guest)
		user = frappe.session.user
		customer = kwargs.get("customer", None)

		# Get e-commerce settings
		settings = get_ecommerce_settings(company)
		if not settings or not settings.enabled:
			frappe.throw("E-commerce is not enabled for this company")

		# Validate items and check stock
		items_list = []
		subtotal = 0

		for item in cart_items:
			item_code = item.get("item_code")
			qty = float(item.get("qty", 1))

			if not item_code:
				frappe.throw("Item code is required")

			# Validate item exists
			item_doc = frappe.get_cached_doc("Item", item_code)
			if not item_doc:
				frappe.throw(f"Item {item_code} does not exist")

			# Check stock if inventory tracking enabled
			if settings.inventory_tracking:
				available_qty = frappe.db.get_value(
					"Bin",
					{"item_code": item_code, "warehouse": get_default_warehouse(company)},
					"actual_qty"
				) or 0

				if available_qty < qty:
					frappe.throw(f"Item {item_code} has insufficient stock. Available: {available_qty}")

			# Get item rate
			rate = float(item.get("rate", item_doc.standard_rate or 0))
			amount = qty * rate
			subtotal += amount

			items_list.append({
				"item_code": item_code,
				"item_name": item_doc.item_name,
				"qty": qty,
				"uom": item_doc.uom or "Nos",
				"rate": rate,
				"amount": amount,
				"image": item_doc.image,
			})

		# Calculate tax and total
		tax_amount = subtotal * 0.13  # 13% tax
		shipping_cost = float(kwargs.get("shipping_cost", 0))
		total = subtotal + tax_amount + shipping_cost

		# Create Online Order
		order = frappe.new_doc("Online Order")
		order.company = company
		order.posting_date = nowdate()
		order.order_date = now()
		order.status = "Pending"
		order.payment_status = "Pending"
		order.payment_method = payment_method
		order.shipping_address = shipping_address
		order.billing_address = billing_address or shipping_address

		# Add items
		for item in items_list:
			order.append("items", item)

		# Set totals
		order.subtotal = subtotal
		order.tax_amount = tax_amount
		order.shipping_cost = shipping_cost
		order.total = total

		# Set customer if provided or user is logged in
		if customer:
			order.customer = customer
		elif user != "Guest":
			# Link to customer if exists
			customer_doc = frappe.db.get_value("Customer", {"user_id": user})
			if customer_doc:
				order.customer = customer_doc

		order.insert()

		# Clear cart
		cart_key = get_cart_storage_key()
		frappe.cache().delete_key(cart_key)

		return {
			"status": "success",
			"message": "Order created successfully",
			"order_id": order.name,
			"order_data": order.as_dict(),
			"payment_url": f"/api/resource/Online Order/{order.name}/process-payment",
		}

	except Exception as e:
		frappe.logger().error(f"Error creating order: {str(e)}")
		return {
			"status": "error",
			"message": str(e),
		}


@frappe.whitelist()
def process_payment(order_id, payment_method="", payment_data=None):
	"""
	Process payment for order
	"""
	try:
		# Get order
		order = frappe.get_doc("Online Order", order_id)

		if order.payment_status == "Paid":
			return {
				"status": "error",
				"message": "Order is already paid",
			}

		if isinstance(payment_data, str):
			payment_data = json.loads(payment_data)
		else:
			payment_data = payment_data or {}

		# Process payment based on method
		payment_method = payment_method or order.payment_method

		if payment_method == "QR Simple":
			from nexo_core.ecommerce.payment_gateways.qr_simple import verify_qr_payment
			result = verify_qr_payment(order, payment_data)

		elif payment_method == "Card Payment":
			from nexo_core.ecommerce.payment_gateways.card_payment import process_card_payment
			result = process_card_payment(order, payment_data)

		elif payment_method == "Cash on Delivery":
			from nexo_core.ecommerce.payment_gateways.cash_on_delivery import process_cod
			result = process_cod(order)

		else:
			frappe.throw(f"Unknown payment method: {payment_method}")

		if result.get("status") == "success":
			# Update order payment status
			order.update_payment_status("Paid", result.get("reference", ""))

			return {
				"status": "success",
				"message": "Payment processed successfully",
				"order_id": order.name,
				"payment_status": order.payment_status,
			}
		else:
			order.update_payment_status("Failed", "")

			return {
				"status": "error",
				"message": result.get("message", "Payment failed"),
			}

	except Exception as e:
		frappe.logger().error(f"Error processing payment: {str(e)}")
		return {
			"status": "error",
			"message": str(e),
		}


@frappe.whitelist(allow_guest=True)
def payment_webhook(gateway, payload=None):
	"""
	Handle payment webhook from payment gateways
	"""
	try:
		if isinstance(payload, str):
			payload = json.loads(payload)
		else:
			payload = payload or {}

		# Route to appropriate gateway handler
		if gateway == "qr_simple":
			from nexo_core.ecommerce.payment_gateways.qr_simple import handle_webhook
			result = handle_webhook(payload)

		elif gateway == "card_payment":
			from nexo_core.ecommerce.payment_gateways.card_payment import handle_webhook
			result = handle_webhook(payload)

		else:
			frappe.logger().warning(f"Unknown gateway in webhook: {gateway}")
			return {"status": "error", "message": "Unknown gateway"}

		frappe.logger().info(f"Webhook processed for {gateway}")
		return {"status": "success"}

	except Exception as e:
		frappe.logger().error(f"Error processing webhook: {str(e)}")
		return {"status": "error", "message": str(e)}


def get_default_warehouse(company):
	"""Get default warehouse for company"""
	warehouse = frappe.db.get_value(
		"Warehouse",
		{"company": company, "disabled": 0},
		"name"
	)

	return warehouse or "Store"
