# Copyright (c) 2025, Aero and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import add_days, nowdate
from nexo_core.doctype.online_order.online_order import create_sales_invoice_from_order


@frappe.whitelist()
def get_my_orders(limit=10, offset=0):
	"""Get orders for current user"""
	try:
		user = frappe.session.user

		if user == "Guest":
			return {
				"status": "error",
				"message": "Must be logged in to view orders",
			}

		# Get customer linked to user
		customer = frappe.db.get_value("Customer", {"user_id": user})

		if not customer:
			return {
				"status": "success",
				"orders": [],
			}

		# Get orders
		orders = frappe.db.get_list(
			"Online Order",
			filters={"customer": customer},
			fields=["name", "order_date", "status", "payment_status", "total"],
			order_by="order_date desc",
			limit_page_length=limit,
			limit_start=offset,
		)

		return {
			"status": "success",
			"orders": orders,
		}

	except Exception as e:
		frappe.logger().error(f"Error getting orders: {str(e)}")
		return {
			"status": "error",
			"message": str(e),
		}


@frappe.whitelist()
def get_order_detail(order_id):
	"""Get order details"""
	try:
		order = frappe.get_doc("Online Order", order_id)

		# Check permissions
		user = frappe.session.user
		customer = frappe.db.get_value("Customer", {"user_id": user})

		if order.customer != customer and user not in ["Administrator", "System Manager"]:
			frappe.throw("You do not have permission to view this order")

		return {
			"status": "success",
			"order": order.as_dict(),
		}

	except Exception as e:
		frappe.logger().error(f"Error getting order detail: {str(e)}")
		return {
			"status": "error",
			"message": str(e),
		}


@frappe.whitelist()
def cancel_order(order_id, reason=""):
	"""Cancel order if in Pending status"""
	try:
		order = frappe.get_doc("Online Order", order_id)

		# Check permissions
		user = frappe.session.user
		customer = frappe.db.get_value("Customer", {"user_id": user})

		if order.customer != customer and user not in ["Administrator", "System Manager"]:
			frappe.throw("You do not have permission to cancel this order")

		# Cancel order
		order.cancel_order(reason)

		return {
			"status": "success",
			"message": "Order cancelled successfully",
		}

	except Exception as e:
		frappe.logger().error(f"Error cancelling order: {str(e)}")
		return {
			"status": "error",
			"message": str(e),
		}


@frappe.whitelist()
def check_pending_orders():
	"""
	Scheduled task: Auto-cancel orders pending for more than 24 hours
	"""
	try:
		# Get orders pending for more than 24 hours
		cutoff_date = add_days(nowdate(), -1)

		pending_orders = frappe.db.get_list(
			"Online Order",
			filters={
				"status": "Pending",
				"payment_status": "Pending",
				"order_date": ["<", cutoff_date],
			},
			fields=["name"],
		)

		count = 0
		for order_data in pending_orders:
			try:
				order = frappe.get_doc("Online Order", order_data["name"])
				order.cancel_order("Auto-cancelled due to timeout")
				count += 1
			except Exception as e:
				frappe.logger().error(f"Error auto-cancelling order {order_data['name']}: {str(e)}")

		frappe.logger().info(f"Auto-cancelled {count} pending orders")

		return {
			"status": "success",
			"cancelled_count": count,
		}

	except Exception as e:
		frappe.logger().error(f"Error in check_pending_orders: {str(e)}")


def create_sales_invoice_from_order_hook(doc, method=None):
	"""
	Doc event: Create Sales Invoice when Online Order is submitted
	"""
	try:
		if doc.docstatus == 1:  # Submit
			create_sales_invoice_from_order(doc)
	except Exception as e:
		frappe.logger().error(f"Error in create_sales_invoice_from_order_hook: {str(e)}")


@frappe.whitelist()
def get_order_stats():
	"""Get order statistics for dashboard"""
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
				"total_orders": 0,
				"total_spent": 0,
				"pending_orders": 0,
			}

		# Get stats
		total_orders = frappe.db.count("Online Order", filters={"customer": customer})
		total_spent = frappe.db.get_value(
			"Online Order",
			{"customer": customer},
			"SUM(total)"
		) or 0

		pending_orders = frappe.db.count(
			"Online Order",
			filters={"customer": customer, "status": "Pending"}
		)

		return {
			"status": "success",
			"total_orders": total_orders,
			"total_spent": float(total_spent),
			"pending_orders": pending_orders,
		}

	except Exception as e:
		frappe.logger().error(f"Error getting order stats: {str(e)}")
		return {
			"status": "error",
			"message": str(e),
		}
