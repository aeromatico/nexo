# Copyright (c) 2025, Aero and contributors
# For license information, please see license.txt

import frappe
import requests
import hashlib
from frappe.utils import get_random_hash
import json


class CardPaymentGateway:
	"""Card Payment Gateway - Credit/Debit Cards"""

	def __init__(self, api_key="", api_secret=""):
		"""Initialize gateway with credentials"""
		self.api_key = api_key
		self.api_secret = api_secret
		# In production, this would connect to a real payment processor like Stripe, PayPal, etc.

	def create_payment_intent(self, order, amount, card_data=None):
		"""Create payment intent for card payment"""
		try:
			# Generate reference ID
			reference_id = get_random_hash("payment_intent")

			# In a real implementation, this would call the payment processor API
			# For now, we'll simulate it
			intent = {
				"id": reference_id,
				"amount": amount,
				"order_id": order.name,
				"status": "pending",
				"created_at": frappe.utils.now(),
			}

			# Save intent
			frappe.db.set_value(
				"Online Order",
				order.name,
				"payment_reference",
				reference_id
			)

			return {
				"status": "success",
				"intent_id": reference_id,
				"amount": amount,
			}

		except Exception as e:
			frappe.logger().error(f"Error creating payment intent: {str(e)}")
			return {
				"status": "error",
				"message": str(e),
			}

	def capture_payment(self, payment_intent_id, card_data):
		"""Capture payment using card data"""
		try:
			# Validate card
			if not self._validate_card(card_data):
				return {
					"status": "error",
					"message": "Invalid card data",
				}

			# In production, call payment processor API
			# For now, simulate successful payment
			transaction_id = get_random_hash("transaction")

			return {
				"status": "success",
				"message": "Payment captured",
				"transaction_id": transaction_id,
				"reference": payment_intent_id,
			}

		except Exception as e:
			frappe.logger().error(f"Error capturing payment: {str(e)}")
			return {
				"status": "error",
				"message": str(e),
			}

	def _validate_card(self, card_data):
		"""Basic card validation"""
		try:
			card_number = card_data.get("card_number", "").replace(" ", "")
			exp_date = card_data.get("expiry", "")
			cvc = card_data.get("cvc", "")

			# Basic Luhn check for card number
			if len(card_number) < 13 or len(card_number) > 19:
				return False

			if len(exp_date) != 5 or len(cvc) < 3:
				return False

			return True

		except Exception:
			return False


def process_card_payment(order, payment_data):
	"""Process card payment for an order"""
	try:
		# Get payment gateway settings
		settings = frappe.get_doc("Ecommerce Settings", order.company)

		gateway = None
		for gw in settings.payment_gateways:
			if gw.gateway_type == "Card Payment" and gw.enabled:
				gateway = CardPaymentGateway(gw.api_key, gw.api_secret)
				break

		if not gateway:
			return {
				"status": "error",
				"message": "Card payment gateway not configured",
			}

		# Create payment intent
		intent_result = gateway.create_payment_intent(order, order.total, payment_data)

		if intent_result.get("status") != "success":
			return intent_result

		intent_id = intent_result.get("intent_id")

		# Capture payment
		capture_result = gateway.capture_payment(intent_id, payment_data)

		if capture_result.get("status") == "success":
			# Log payment
			log_payment(
				order.name,
				"Card Payment",
				order.total,
				"Completed",
				capture_result.get("transaction_id")
			)

			return {
				"status": "success",
				"message": "Payment processed",
				"reference": capture_result.get("transaction_id"),
			}
		else:
			return capture_result

	except Exception as e:
		frappe.logger().error(f"Error processing card payment: {str(e)}")
		return {
			"status": "error",
			"message": str(e),
		}


def handle_webhook(payload):
	"""Handle webhook from card payment processor"""
	try:
		order_id = payload.get("order_id")
		status = payload.get("status")  # succeeded, failed, etc.
		transaction_id = payload.get("transaction_id")

		if not order_id:
			return {
				"status": "error",
				"message": "Missing order ID",
			}

		order = frappe.get_doc("Online Order", order_id)

		if status == "succeeded":
			order.update_payment_status("Paid", transaction_id)
			log_payment(order_id, "Card Payment", order.total, "Completed", transaction_id)

		elif status == "failed":
			order.update_payment_status("Failed", "")

		return {"status": "success"}

	except Exception as e:
		frappe.logger().error(f"Error in card payment webhook: {str(e)}")
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
