# Copyright (c) 2025, Aero and contributors
# For license information, please see license.txt

import frappe


@frappe.whitelist(allow_guest=True)
def get_products(filters=None, limit=20, offset=0):
	"""Get published products with pagination"""
	try:
		if isinstance(filters, str):
			import json
			filters = json.loads(filters)
		else:
			filters = filters or {}

		# Build filter conditions
		conditions = {"disabled": 0}

		# Filter by category if provided
		if filters.get("category"):
			conditions["item_group"] = filters["category"]

		# Get products
		products = frappe.db.get_list(
			"Item",
			filters=conditions,
			fields=[
				"name",
				"item_name",
				"item_group",
				"description",
				"image",
				"standard_rate",
				"uom",
				"weight_per_unit",
			],
			order_by="modified desc",
			limit_page_length=limit,
			limit_start=offset,
		)

		# Enhance with additional data
		for product in products:
			product["rate"] = get_item_rate(product["name"])
			product["stock"] = get_item_stock(product["name"])
			product["in_stock"] = product["stock"] > 0

		return {
			"status": "success",
			"products": products,
			"limit": limit,
			"offset": offset,
		}

	except Exception as e:
		frappe.logger().error(f"Error getting products: {str(e)}")
		return {
			"status": "error",
			"message": str(e),
		}


@frappe.whitelist(allow_guest=True)
def get_product_detail(item_code):
	"""Get detailed product information"""
	try:
		# Get item
		item = frappe.get_cached_doc("Item", item_code)

		if item.disabled:
			frappe.throw("Item is not available")

		# Get price
		rate = get_item_rate(item_code)

		# Get stock
		stock = get_item_stock(item_code)

		# Get variants if available
		variants = frappe.db.get_list(
			"Item",
			filters={
				"variant_of": item_code,
				"disabled": 0,
			},
			fields=[
				"name",
				"item_name",
				"attribute_values",
				"standard_rate",
				"image",
			],
		)

		# Get images (attachments)
		images = frappe.db.get_list(
			"File",
			filters={
				"attached_to_doctype": "Item",
				"attached_to_name": item_code,
				"is_private": 0,
			},
			fields=["name", "file_url"],
		)

		return {
			"status": "success",
			"product": {
				"code": item.name,
				"name": item.item_name,
				"description": item.description,
				"long_description": item.item_details,
				"category": item.item_group,
				"rate": rate,
				"standard_rate": item.standard_rate,
				"image": item.image,
				"images": images,
				"stock": stock,
				"in_stock": stock > 0,
				"uom": item.uom,
				"weight": item.weight_per_unit,
				"brand": item.brand,
				"variants": variants,
				"hsn_code": item.gst_hsn_code,
			},
		}

	except frappe.DoesNotExistError:
		return {
			"status": "error",
			"message": f"Product {item_code} not found",
		}
	except Exception as e:
		frappe.logger().error(f"Error getting product detail: {str(e)}")
		return {
			"status": "error",
			"message": str(e),
		}


@frappe.whitelist(allow_guest=True)
def search_products(query, limit=10):
	"""Search products by name or description"""
	try:
		if not query or len(query) < 2:
			return {
				"status": "error",
				"message": "Search query must be at least 2 characters",
			}

		# Search in Item name and description
		products = frappe.db.get_list(
			"Item",
			filters={
				"disabled": 0,
			},
			fields=[
				"name",
				"item_name",
				"description",
				"image",
				"standard_rate",
			],
			or_filters=[
				["item_name", "like", f"%{query}%"],
				["description", "like", f"%{query}%"],
			],
			limit_page_length=limit,
		)

		# Enhance with rates
		for product in products:
			product["rate"] = get_item_rate(product["name"])
			product["stock"] = get_item_stock(product["name"])

		return {
			"status": "success",
			"products": products,
			"count": len(products),
		}

	except Exception as e:
		frappe.logger().error(f"Error searching products: {str(e)}")
		return {
			"status": "error",
			"message": str(e),
		}


@frappe.whitelist(allow_guest=True)
def get_categories():
	"""Get all product categories"""
	try:
		categories = frappe.db.get_list(
			"Item Group",
			filters={"disabled": 0},
			fields=["name", "item_group_name", "description"],
			order_by="name asc",
		)

		return {
			"status": "success",
			"categories": categories,
		}

	except Exception as e:
		frappe.logger().error(f"Error getting categories: {str(e)}")
		return {
			"status": "error",
			"message": str(e),
		}


@frappe.whitelist(allow_guest=True)
def get_featured_products(limit=5):
	"""Get featured products (highest rated or best selling)"""
	try:
		products = frappe.db.get_list(
			"Item",
			filters={
				"disabled": 0,
				"item_group": "Featured",  # Optional: could use a custom field
			},
			fields=[
				"name",
				"item_name",
				"description",
				"image",
				"standard_rate",
			],
			limit_page_length=limit,
		)

		for product in products:
			product["rate"] = get_item_rate(product["name"])
			product["stock"] = get_item_stock(product["name"])

		return {
			"status": "success",
			"products": products,
		}

	except Exception as e:
		frappe.logger().error(f"Error getting featured products: {str(e)}")
		return {
			"status": "success",
			"products": [],
		}


def get_item_rate(item_code):
	"""Get current item rate"""
	try:
		price = frappe.db.get_value(
			"Item Price",
			{
				"item_code": item_code,
				"selling": 1,
			},
			"price_list_rate"
		)

		if price:
			return float(price)

		# Fallback to standard rate
		item = frappe.get_cached_doc("Item", item_code)
		return float(item.standard_rate or 0)

	except Exception:
		return 0


def get_item_stock(item_code, warehouse=None):
	"""Get item stock quantity"""
	try:
		if not warehouse:
			# Get default warehouse
			warehouse = frappe.db.get_value(
				"Warehouse",
				{"disabled": 0},
				"name"
			) or "Store"

		stock = frappe.db.get_value(
			"Bin",
			{
				"item_code": item_code,
				"warehouse": warehouse,
			},
			"actual_qty"
		) or 0

		return float(stock)

	except Exception:
		return 0
