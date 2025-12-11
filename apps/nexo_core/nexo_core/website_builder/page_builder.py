# Copyright (c) 2025, Aero and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.utils import now


@frappe.whitelist()
def create_page(page_name, route, title, content, template="Custom", **kwargs):
	"""Create website page"""
	try:
		# Validate input
		if not page_name:
			frappe.throw("Page name is required")

		if not route:
			frappe.throw("Route is required")

		if not title:
			frappe.throw("Title is required")

		if not content:
			frappe.throw("Content is required")

		# Ensure route starts with /
		if not route.startswith("/"):
			route = "/" + route

		# Check for duplicate route
		existing = frappe.db.exists("Website Page", {"route": route})
		if existing:
			frappe.throw(f"Route {route} already exists")

		# Create page
		page = frappe.new_doc("Website Page")
		page.page_name = page_name
		page.route = route
		page.title = title
		page.content = content
		page.template = template
		page.seo_title = kwargs.get("seo_title", title)
		page.seo_description = kwargs.get("seo_description", "")
		page.seo_keywords = kwargs.get("seo_keywords", "")
		page.published = 0

		page.insert()

		return {
			"status": "success",
			"message": "Page created",
			"page_id": page.name,
			"page": page.as_dict(),
		}

	except Exception as e:
		frappe.logger().error(f"Error creating page: {str(e)}")
		return {
			"status": "error",
			"message": str(e),
		}


@frappe.whitelist()
def update_page(page_name, content=None, title=None, seo_title=None, seo_description=None, seo_keywords=None):
	"""Update page content"""
	try:
		# Get page
		page = frappe.get_doc("Website Page", page_name)

		if content:
			page.content = content

		if title:
			page.title = title

		if seo_title:
			page.seo_title = seo_title

		if seo_description:
			page.seo_description = seo_description

		if seo_keywords:
			page.seo_keywords = seo_keywords

		page.save()

		return {
			"status": "success",
			"message": "Page updated",
			"page": page.as_dict(),
		}

	except Exception as e:
		frappe.logger().error(f"Error updating page: {str(e)}")
		return {
			"status": "error",
			"message": str(e),
		}


@frappe.whitelist()
def publish_page(page_name):
	"""Publish page"""
	try:
		page = frappe.get_doc("Website Page", page_name)

		page.published = 1
		page.publish_date = now()
		page.save()

		# Clear cache
		frappe.cache().delete_key(f"website_page:{page.route}")
		frappe.cache().delete_key("website_pages_list")

		return {
			"status": "success",
			"message": "Page published",
		}

	except Exception as e:
		frappe.logger().error(f"Error publishing page: {str(e)}")
		return {
			"status": "error",
			"message": str(e),
		}


@frappe.whitelist()
def unpublish_page(page_name):
	"""Unpublish page"""
	try:
		page = frappe.get_doc("Website Page", page_name)

		page.published = 0
		page.save()

		# Clear cache
		frappe.cache().delete_key(f"website_page:{page.route}")
		frappe.cache().delete_key("website_pages_list")

		return {
			"status": "success",
			"message": "Page unpublished",
		}

	except Exception as e:
		frappe.logger().error(f"Error unpublishing page: {str(e)}")
		return {
			"status": "error",
			"message": str(e),
		}


@frappe.whitelist()
def delete_page(page_name):
	"""Delete page"""
	try:
		page = frappe.get_doc("Website Page", page_name)

		# Clear cache before deleting
		frappe.cache().delete_key(f"website_page:{page.route}")
		frappe.cache().delete_key("website_pages_list")

		page.delete()

		return {
			"status": "success",
			"message": "Page deleted",
		}

	except Exception as e:
		frappe.logger().error(f"Error deleting page: {str(e)}")
		return {
			"status": "error",
			"message": str(e),
		}


@frappe.whitelist(allow_guest=True)
def render_page(route):
	"""Render page by route (public)"""
	try:
		# Get page
		from nexo_core.doctype.website_page.website_page import get_website_page

		page = get_website_page(route)

		if not page:
			return {
				"status": "error",
				"message": "Page not found",
				"code": 404,
			}

		return {
			"status": "success",
			"page": page,
		}

	except Exception as e:
		frappe.logger().error(f"Error rendering page: {str(e)}")
		return {
			"status": "error",
			"message": str(e),
		}


@frappe.whitelist()
def get_pages(limit=20, offset=0):
	"""Get all pages"""
	try:
		pages = frappe.db.get_list(
			"Website Page",
			fields=["name", "page_name", "route", "title", "published", "modified"],
			order_by="modified desc",
			limit_page_length=limit,
			limit_start=offset,
		)

		return {
			"status": "success",
			"pages": pages,
		}

	except Exception as e:
		frappe.logger().error(f"Error getting pages: {str(e)}")
		return {
			"status": "error",
			"message": str(e),
		}
