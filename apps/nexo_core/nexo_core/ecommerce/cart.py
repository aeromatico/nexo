# Copyright (c) 2025, Aero and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.utils import cint


def get_session_id():
	"""Get or create session ID for guest users"""
	sid = frappe.session.sid
	return sid


def get_cart_storage_key():
	"""Get cart storage key (session-based for guests, user-based for logged in)"""
	if frappe.session.user == "Guest":
		return f"cart:{get_session_id()}"
	else:
		return f"cart:{frappe.session.user}"


@frappe.whitelist(allow_guest=True)
def add_to_cart(item_code, qty=1, **kwargs):
	"""Add item to cart"""
	try:
		qty = cint(qty)

		if qty <= 0:
			frappe.throw("Quantity must be greater than 0")

		# Validate item exists and is available for sale
		item = frappe.get_cached_doc("Item", item_code)

		if not item:
			frappe.throw(f"Item {item_code} does not exist")

		if item.disabled:
			frappe.throw(f"Item {item_code} is disabled")

		# Get current cart
		cart_key = get_cart_storage_key()
		cart = frappe.cache().get_value(cart_key) or {}

		# Add or update item
		if item_code in cart:
			cart[item_code]["qty"] += qty
		else:
			cart[item_code] = {
				"item_code": item_code,
				"item_name": item.item_name,
				"qty": qty,
				"rate": get_item_rate(item_code),
				"image": item.image,
				"description": item.description or "",
			}

		# Save cart
		frappe.cache().set_value(cart_key, cart, expires_in_sec=604800)  # 7 days

		return {
			"status": "success",
			"message": f"{item.item_name} added to cart",
			"cart": cart,
		}

	except Exception as e:
		frappe.logger().error(f"Error adding to cart: {str(e)}")
		return {
			"status": "error",
			"message": str(e),
		}


@frappe.whitelist(allow_guest=True)
def remove_from_cart(item_code):
	"""Remove item from cart"""
	try:
		cart_key = get_cart_storage_key()
		cart = frappe.cache().get_value(cart_key) or {}

		if item_code in cart:
			del cart[item_code]
			frappe.cache().set_value(cart_key, cart, expires_in_sec=604800)

			return {
				"status": "success",
				"message": "Item removed from cart",
				"cart": cart,
			}
		else:
			return {
				"status": "error",
				"message": "Item not in cart",
			}

	except Exception as e:
		frappe.logger().error(f"Error removing from cart: {str(e)}")
		return {
			"status": "error",
			"message": str(e),
		}


@frappe.whitelist(allow_guest=True)
def update_cart(item_code, qty):
	"""Update item quantity in cart"""
	try:
		qty = cint(qty)

		if qty <= 0:
			return remove_from_cart(item_code)

		cart_key = get_cart_storage_key()
		cart = frappe.cache().get_value(cart_key) or {}

		if item_code in cart:
			cart[item_code]["qty"] = qty
			frappe.cache().set_value(cart_key, cart, expires_in_sec=604800)

			return {
				"status": "success",
				"message": "Cart updated",
				"cart": cart,
			}
		else:
			return {
				"status": "error",
				"message": "Item not in cart",
			}

	except Exception as e:
		frappe.logger().error(f"Error updating cart: {str(e)}")
		return {
			"status": "error",
			"message": str(e),
		}


@frappe.whitelist(allow_guest=True)
def get_cart():
	"""Get current cart"""
	try:
		cart_key = get_cart_storage_key()
		cart = frappe.cache().get_value(cart_key) or {}

		return {
			"status": "success",
			"cart": cart,
		}

	except Exception as e:
		frappe.logger().error(f"Error getting cart: {str(e)}")
		return {
			"status": "error",
			"message": str(e),
		}


@frappe.whitelist(allow_guest=True)
def get_cart_summary():
	"""Get cart summary with totals"""
	try:
		cart_key = get_cart_storage_key()
		cart = frappe.cache().get_value(cart_key) or {}

		if not cart:
			return {
				"status": "success",
				"subtotal": 0,
				"tax_amount": 0,
				"total": 0,
				"item_count": 0,
				"items": [],
			}

		subtotal = 0
		items_list = []

		for item_code, item_data in cart.items():
			amount = item_data["qty"] * item_data["rate"]
			subtotal += amount

			items_list.append({
				"item_code": item_code,
				"item_name": item_data["item_name"],
				"qty": item_data["qty"],
				"rate": item_data["rate"],
				"amount": amount,
			})

		# Calculate 13% tax (Bolivia)
		tax_amount = subtotal * 0.13
		total = subtotal + tax_amount

		return {
			"status": "success",
			"items": items_list,
			"item_count": len(cart),
			"subtotal": round(subtotal, 2),
			"tax_amount": round(tax_amount, 2),
			"total": round(total, 2),
		}

	except Exception as e:
		frappe.logger().error(f"Error getting cart summary: {str(e)}")
		return {
			"status": "error",
			"message": str(e),
		}


@frappe.whitelist(allow_guest=True)
def clear_cart():
	"""Clear entire cart"""
	try:
		cart_key = get_cart_storage_key()
		frappe.cache().delete_key(cart_key)

		return {
			"status": "success",
			"message": "Cart cleared",
		}

	except Exception as e:
		frappe.logger().error(f"Error clearing cart: {str(e)}")
		return {
			"status": "error",
			"message": str(e),
		}


def get_item_rate(item_code):
	"""Get current item rate"""
	try:
		item = frappe.get_cached_doc("Item", item_code)
		# Get standard selling rate
		price = frappe.db.get_value(
			"Item Price",
			{"item_code": item_code, "selling": 1},
			"price_list_rate"
		)

		return price or item.standard_rate or 0

	except Exception:
		return 0
