# Copyright (c) 2025, Aero and contributors
# For license information, please see license.txt

import frappe
import unittest
from nexo_core.ecommerce.payment_gateways.qr_simple import QRSimpleGateway, generate_qr_for_order
from nexo_core.ecommerce.payment_gateways.card_payment import CardPaymentGateway
from nexo_core.ecommerce.payment_gateways.cash_on_delivery import process_cod


class TestQRSimpleGateway(unittest.TestCase):
	"""Test QR Simple payment gateway"""

	def test_generate_qr(self):
		"""Test QR generation"""
		# Create mock order
		class MockOrder:
			name = "OO-TEST-001"
			company = "Test Company"
			total = 113.00

		order = MockOrder()
		gateway = QRSimpleGateway()

		result = gateway.generate_qr(order, 113)

		self.assertEqual(result.get("status"), "success")
		self.assertIn("qr_code", result)
		self.assertIn("qr_data", result)


class TestCardPaymentGateway(unittest.TestCase):
	"""Test card payment gateway"""

	def test_create_payment_intent(self):
		"""Test creating payment intent"""
		class MockOrder:
			name = "OO-TEST-002"

		order = MockOrder()
		gateway = CardPaymentGateway(api_key="test_key", api_secret="test_secret")

		result = gateway.create_payment_intent(order, 100)

		self.assertEqual(result.get("status"), "success")
		self.assertIn("intent_id", result)

	def test_validate_card(self):
		"""Test card validation"""
		gateway = CardPaymentGateway()

		# Valid card
		valid_card = {
			"card_number": "4532015112830366",
			"expiry": "12/25",
			"cvc": "123",
		}
		result = gateway._validate_card(valid_card)
		self.assertTrue(result)

		# Invalid card number
		invalid_card = {
			"card_number": "123",
			"expiry": "12/25",
			"cvc": "123",
		}
		result = gateway._validate_card(invalid_card)
		self.assertFalse(result)

		# Invalid expiry
		invalid_expiry = {
			"card_number": "4532015112830366",
			"expiry": "1225",
			"cvc": "123",
		}
		result = gateway._validate_card(invalid_expiry)
		self.assertFalse(result)


class TestCashOnDelivery(unittest.TestCase):
	"""Test Cash on Delivery gateway"""

	def test_process_cod(self):
		"""Test processing COD order"""
		class MockOrder:
			name = "OO-TEST-003"
			total = 113.00

		order = MockOrder()
		result = process_cod(order)

		self.assertEqual(result.get("status"), "success")
		self.assertEqual(result.get("reference"), "OO-TEST-003")


if __name__ == "__main__":
	unittest.main()
