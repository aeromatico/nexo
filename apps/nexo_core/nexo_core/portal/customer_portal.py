# Copyright (c) 2025, Aero and contributors
# For license information, please see license.txt

import frappe


@frappe.whitelist()
def get_dashboard_data():
	"""
	Get customer portal dashboard data:
	- Total orders, total spent
	- Pending orders
	- Recent transactions
	- Account information
	"""
	try:
		user = frappe.session.user

		if user == "Guest":
			return {
				"status": "error",
				"message": "Must be logged in",
			}

		# Get customer linked to user
		customer = frappe.db.get_value("Customer", {"user_id": user})

		if not customer:
			return {
				"status": "success",
				"dashboard": {
					"total_orders": 0,
					"total_spent": 0,
					"pending_orders": 0,
					"pending_invoices": 0,
					"recent_orders": [],
					"recent_invoices": [],
				},
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

		pending_invoices = frappe.db.count(
			"Sales Invoice",
			filters={
				"customer": customer,
				"docstatus": 1,
				"outstanding_amount": [">", 0],
			}
		)

		# Get recent orders
		recent_orders = frappe.db.get_list(
			"Online Order",
			filters={"customer": customer},
			fields=["name", "order_date", "status", "total"],
			order_by="order_date desc",
			limit_page_length=5,
		)

		# Get recent invoices
		recent_invoices = frappe.db.get_list(
			"Sales Invoice",
			filters={"customer": customer, "docstatus": 1},
			fields=["name", "posting_date", "outstanding_amount", "total"],
			order_by="posting_date desc",
			limit_page_length=5,
		)

		return {
			"status": "success",
			"dashboard": {
				"customer": customer,
				"total_orders": total_orders,
				"total_spent": float(total_spent),
				"pending_orders": pending_orders,
				"pending_invoices": pending_invoices,
				"recent_orders": recent_orders,
				"recent_invoices": recent_invoices,
			},
		}

	except Exception as e:
		frappe.logger().error(f"Error getting dashboard data: {str(e)}")
		return {
			"status": "error",
			"message": str(e),
		}


@frappe.whitelist()
def update_profile(first_name="", last_name="", phone="", address="", city="", country=""):
	"""Update customer profile"""
	try:
		user = frappe.session.user

		if user == "Guest":
			frappe.throw("Must be logged in")

		# Get customer
		customer = frappe.db.get_value("Customer", {"user_id": user})

		if not customer:
			frappe.throw("Customer not found")

		# Update customer
		customer_doc = frappe.get_doc("Customer", customer)

		if first_name or last_name:
			customer_doc.customer_name = f"{first_name} {last_name}".strip()

		if phone:
			customer_doc.mobile_no = phone

		if address or city or country:
			# Update billing address
			if customer_doc.customer_primary_address:
				addr_doc = frappe.get_doc("Address", customer_doc.customer_primary_address)
				if address:
					addr_doc.address_line1 = address
				if city:
					addr_doc.city = city
				if country:
					addr_doc.country = country
				addr_doc.save()

		customer_doc.save()

		return {
			"status": "success",
			"message": "Profile updated successfully",
		}

	except Exception as e:
		frappe.logger().error(f"Error updating profile: {str(e)}")
		return {
			"status": "error",
			"message": str(e),
		}


@frappe.whitelist()
def get_user_info():
	"""Get current user information"""
	try:
		user = frappe.session.user

		if user == "Guest":
			return {
				"status": "error",
				"message": "Not logged in",
			}

		user_doc = frappe.get_doc("User", user)
		customer = frappe.db.get_value("Customer", {"user_id": user})

		return {
			"status": "success",
			"user": {
				"name": user,
				"email": user_doc.email,
				"full_name": user_doc.full_name,
				"customer": customer,
			},
		}

	except Exception as e:
		frappe.logger().error(f"Error getting user info: {str(e)}")
		return {
			"status": "error",
			"message": str(e),
		}
