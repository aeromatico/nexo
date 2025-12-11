# Copyright (c) 2025, Aero and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class WebsitePage(Document):
	"""Website Page DocType"""

	def validate(self):
		"""Validate website page"""
		if not self.page_name:
			frappe.throw("Page Name is required")

		if not self.route:
			frappe.throw("Route is required")

		# Validate route format
		if not self.route.startswith("/"):
			self.route = "/" + self.route

		# Set SEO title if not provided
		if not self.seo_title:
			self.seo_title = self.title

	def on_update(self):
		"""After update"""
		# Clear cache
		frappe.cache().delete_key(f"website_page:{self.route}")
		frappe.cache().delete_key("website_pages_list")

	def on_trash(self):
		"""Before delete"""
		# Clear cache
		frappe.cache().delete_key(f"website_page:{self.route}")
		frappe.cache().delete_key("website_pages_list")


def get_website_page(route):
	"""Get website page by route (cached)"""
	cache_key = f"website_page:{route}"
	page = frappe.cache().get_value(cache_key)

	if page is None:
		try:
			page = frappe.db.get_value(
				"Website Page",
				{"route": route, "published": 1},
				["name", "title", "content", "seo_title", "seo_description", "template"],
				as_dict=True
			)

			if page:
				frappe.cache().set_value(cache_key, page)
			else:
				frappe.cache().set_value(cache_key, {"not_found": True})
				return None

		except Exception:
			return None

	if page and page.get("not_found"):
		return None

	return page


def get_published_pages():
	"""Get all published pages (cached)"""
	cache_key = "website_pages_list"
	pages = frappe.cache().get_value(cache_key)

	if pages is None:
		pages = frappe.db.get_list(
			"Website Page",
			filters={"published": 1},
			fields=["name", "route", "title", "seo_title"],
			order_by="title asc"
		)

		frappe.cache().set_value(cache_key, pages, expires_in_sec=3600)

	return pages or []
