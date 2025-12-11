# Copyright (c) 2025, Aero and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class EcommerceSettings(Document):
	"""E-commerce Settings DocType"""

	def validate(self):
		"""Validate settings"""
		if self.enabled and not self.store_name:
			frappe.throw("Store Name is required when E-commerce is enabled")

		if self.enabled and not self.default_currency:
			frappe.throw("Default Currency is required when E-commerce is enabled")

		# Set store URL
		if self.store_domain:
			self.store_url = f"https://{self.store_domain}"

	def on_update(self):
		"""Update store configuration"""
		# Clear cache
		frappe.cache().delete_key(f"ecommerce_settings:{self.company}")
		frappe.cache().delete_key(f"payment_gateways:{self.company}")
		frappe.cache().delete_key(f"shipping_methods:{self.company}")


def get_ecommerce_settings(company):
	"""Get e-commerce settings for company (cached)"""
	cache_key = f"ecommerce_settings:{company}"
	settings = frappe.cache().get_value(cache_key)

	if not settings:
		try:
			settings = frappe.get_doc("Ecommerce Settings", company)
		except frappe.DoesNotExistError:
			return None

		frappe.cache().set_value(cache_key, settings)

	return settings


def get_payment_gateways(company, enabled_only=True):
	"""Get payment gateways for company"""
	settings = get_ecommerce_settings(company)

	if not settings or not settings.payment_gateways:
		return []

	gateways = []
	for row in settings.payment_gateways:
		if enabled_only and not row.enabled:
			continue

		gateway = {
			"name": row.gateway_name,
			"type": row.gateway_type,
			"enabled": row.enabled,
			"api_key": row.api_key,
			"api_secret": row.api_secret,
			"webhook_url": row.webhook_url,
		}

		if row.settings_json:
			import json
			gateway["settings"] = json.loads(row.settings_json)

		gateways.append(gateway)

	return gateways


def get_shipping_methods(company, enabled_only=True):
	"""Get shipping methods for company"""
	settings = get_ecommerce_settings(company)

	if not settings or not settings.shipping_methods:
		return []

	methods = []
	for row in settings.shipping_methods:
		if enabled_only and not row.enabled:
			continue

		method = {
			"name": row.method_name,
			"enabled": row.enabled,
			"base_cost": row.base_cost or 0,
			"cost_per_kg": row.cost_per_kg or 0,
			"estimated_days": row.estimated_days or 0,
			"description": row.description,
		}

		methods.append(method)

	return methods
