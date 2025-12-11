# Copyright (c) 2025, Aero and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import now


@frappe.whitelist()
def create_support_ticket(subject, description, priority="Medium", category="General"):
	"""Create support ticket"""
	try:
		user = frappe.session.user

		if user == "Guest":
			frappe.throw("Must be logged in to create support ticket")

		# Get customer
		customer = frappe.db.get_value("Customer", {"user_id": user})

		# Create ticket using Issue DocType (built-in in ERPNext)
		ticket = frappe.new_doc("Issue")
		ticket.subject = subject
		ticket.description = description
		ticket.priority = priority
		ticket.customer = customer
		ticket.status = "Open"
		ticket.raised_by = user

		# Optional: Link to customer
		if customer:
			ticket.customer_name = frappe.db.get_value("Customer", customer, "customer_name")

		ticket.insert()

		return {
			"status": "success",
			"message": "Support ticket created",
			"ticket_id": ticket.name,
		}

	except Exception as e:
		frappe.logger().error(f"Error creating support ticket: {str(e)}")
		return {
			"status": "error",
			"message": str(e),
		}


@frappe.whitelist()
def get_my_tickets(limit=10, offset=0):
	"""Get support tickets for current user"""
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
				"tickets": [],
			}

		# Get tickets
		tickets = frappe.db.get_list(
			"Issue",
			filters={"customer": customer},
			fields=["name", "subject", "status", "priority", "creation"],
			order_by="creation desc",
			limit_page_length=limit,
			limit_start=offset,
		)

		return {
			"status": "success",
			"tickets": tickets,
		}

	except Exception as e:
		frappe.logger().error(f"Error getting tickets: {str(e)}")
		return {
			"status": "error",
			"message": str(e),
		}


@frappe.whitelist()
def get_ticket_detail(ticket_id):
	"""Get ticket details with comments"""
	try:
		user = frappe.session.user

		if user == "Guest":
			frappe.throw("Must be logged in")

		# Get customer
		customer = frappe.db.get_value("Customer", {"user_id": user})

		# Get ticket
		ticket = frappe.get_doc("Issue", ticket_id)

		# Check permissions
		if ticket.customer != customer and user not in ["Administrator", "System Manager"]:
			frappe.throw("You do not have permission to view this ticket")

		# Get comments
		comments = frappe.db.get_list(
			"Comment",
			filters={
				"comment_type": "comment",
				"reference_doctype": "Issue",
				"reference_name": ticket_id,
			},
			fields=["name", "content", "creation", "owner"],
			order_by="creation asc",
		)

		return {
			"status": "success",
			"ticket": ticket.as_dict(),
			"comments": comments,
		}

	except Exception as e:
		frappe.logger().error(f"Error getting ticket detail: {str(e)}")
		return {
			"status": "error",
			"message": str(e),
		}


@frappe.whitelist()
def add_ticket_comment(ticket_id, comment):
	"""Add comment to ticket"""
	try:
		user = frappe.session.user

		if user == "Guest":
			frappe.throw("Must be logged in")

		# Get customer
		customer = frappe.db.get_value("Customer", {"user_id": user})

		# Get ticket
		ticket = frappe.get_doc("Issue", ticket_id)

		# Check permissions
		if ticket.customer != customer and user not in ["Administrator", "System Manager"]:
			frappe.throw("You do not have permission to comment on this ticket")

		# Create comment
		comment_doc = frappe.new_doc("Comment")
		comment_doc.comment_type = "comment"
		comment_doc.reference_doctype = "Issue"
		comment_doc.reference_name = ticket_id
		comment_doc.content = comment

		comment_doc.insert()

		return {
			"status": "success",
			"message": "Comment added",
			"comment_id": comment_doc.name,
		}

	except Exception as e:
		frappe.logger().error(f"Error adding comment: {str(e)}")
		return {
			"status": "error",
			"message": str(e),
		}


@frappe.whitelist()
def close_ticket(ticket_id, resolution=""):
	"""Close support ticket"""
	try:
		user = frappe.session.user

		if user == "Guest":
			frappe.throw("Must be logged in")

		# Get customer
		customer = frappe.db.get_value("Customer", {"user_id": user})

		# Get ticket
		ticket = frappe.get_doc("Issue", ticket_id)

		# Check permissions (only customer or support staff can close)
		if ticket.customer != customer and user not in ["Administrator", "System Manager", "Support Team"]:
			frappe.throw("You do not have permission to close this ticket")

		ticket.status = "Closed"
		if resolution:
			ticket.resolution_details = resolution

		ticket.save()

		return {
			"status": "success",
			"message": "Ticket closed",
		}

	except Exception as e:
		frappe.logger().error(f"Error closing ticket: {str(e)}")
		return {
			"status": "error",
			"message": str(e),
		}
