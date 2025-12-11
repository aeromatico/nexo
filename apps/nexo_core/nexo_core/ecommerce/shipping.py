# Copyright (c) 2025, Aero and contributors
# For license information, please see license.txt

import frappe
from nexo_core.doctype.ecommerce_settings.ecommerce_settings import get_shipping_methods


@frappe.whitelist()
def get_shipping_options(company, weight=0):
	"""Get available shipping methods for company"""
	try:
		methods = get_shipping_methods(company, enabled_only=True)

		# Calculate shipping cost based on weight
		shipping_options = []
		for method in methods:
			cost = method.get("base_cost", 0)

			# Add weight-based cost if applicable
			if weight and method.get("cost_per_kg"):
				cost += weight * method.get("cost_per_kg")

			shipping_options.append({
				"name": method.get("name"),
				"description": method.get("description"),
				"cost": cost,
				"estimated_days": method.get("estimated_days"),
			})

		return {
			"status": "success",
			"shipping_options": shipping_options,
		}

	except Exception as e:
		frappe.logger().error(f"Error getting shipping options: {str(e)}")
		return {
			"status": "error",
			"message": str(e),
		}


@frappe.whitelist()
def calculate_shipping(company, weight=0, shipping_method=None):
	"""Calculate shipping cost"""
	try:
		methods = get_shipping_methods(company, enabled_only=True)

		if not methods:
			return {
				"status": "success",
				"shipping_cost": 0,
				"estimated_days": 0,
			}

		# Find method
		selected_method = None
		for method in methods:
			if method.get("name") == shipping_method:
				selected_method = method
				break

		if not selected_method:
			selected_method = methods[0]  # Use first method as default

		cost = selected_method.get("base_cost", 0)

		if weight and selected_method.get("cost_per_kg"):
			cost += weight * selected_method.get("cost_per_kg")

		return {
			"status": "success",
			"shipping_cost": cost,
			"estimated_days": selected_method.get("estimated_days"),
			"method": selected_method.get("name"),
		}

	except Exception as e:
		frappe.logger().error(f"Error calculating shipping: {str(e)}")
		return {
			"status": "error",
			"message": str(e),
		}


@frappe.whitelist()
def update_tracking(order_id, tracking_number, status="Processing"):
	"""Update order tracking information"""
	try:
		order = frappe.get_doc("Online Order", order_id)

		order.tracking_number = tracking_number
		order.status = status

		order.save()

		return {
			"status": "success",
			"message": "Tracking information updated",
		}

	except Exception as e:
		frappe.logger().error(f"Error updating tracking: {str(e)}")
		return {
			"status": "error",
			"message": str(e),
		}


@frappe.whitelist()
def get_tracking(order_id):
	"""Get order tracking information"""
	try:
		order = frappe.get_doc("Online Order", order_id)

		return {
			"status": "success",
			"tracking": {
				"order_id": order.name,
				"status": order.status,
				"tracking_number": order.tracking_number,
				"order_date": order.order_date,
				"estimated_delivery": None,  # Can be calculated from shipping method
			},
		}

	except Exception as e:
		frappe.logger().error(f"Error getting tracking: {str(e)}")
		return {
			"status": "error",
			"message": str(e),
		}
