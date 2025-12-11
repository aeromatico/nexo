# Copyright (c) 2025, Aero and contributors
# For license information, please see license.txt

import frappe


def process_cod(order):
	"""
	Process Cash on Delivery order
	No payment is processed immediately, order is marked as pending payment
	"""
	try:
		# For COD, we don't process payment immediately
		# The order status remains Pending and payment_status remains Pending
		# Payment will be collected when order is delivered

		# Log the COD transaction
		log_payment(
			order.name,
			"Cash on Delivery",
			order.total,
			"Pending",
			order.name
		)

		return {
			"status": "success",
			"message": "Cash on Delivery order created successfully",
			"reference": order.name,
		}

	except Exception as e:
		frappe.logger().error(f"Error processing COD: {str(e)}")
		return {
			"status": "error",
			"message": str(e),
		}


def log_payment(order_id, gateway, amount, status, reference):
	"""Log payment transaction"""
	try:
		log = frappe.new_doc("Payment Log")
		log.order_id = order_id
		log.gateway = gateway
		log.amount = amount
		log.status = status
		log.reference = reference

		log.insert(ignore_permissions=True)

	except Exception as e:
		frappe.logger().error(f"Error logging payment: {str(e)}")
