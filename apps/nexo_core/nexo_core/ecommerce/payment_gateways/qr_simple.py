# Copyright (c) 2025, Aero and contributors
# For license information, please see license.txt

import frappe
import qrcode
from io import BytesIO
import base64
from frappe.utils import cint
import hashlib


class QRSimpleGateway:
	"""QR Simple Payment Gateway for Bolivia"""

	@staticmethod
	def generate_qr(order, amount):
		"""
		Generate QR code for simple QR payment
		Format: BANCO|CUENTA|MONTO|REFERENCIA
		"""
		try:
			# QR Simple format for Bolivia
			qr_data = f"00|{order.name}|{amount}|{order.company}"

			# Generate QR code
			qr = qrcode.QRCode(
				version=1,
				error_correction=qrcode.constants.ERROR_CORRECT_L,
				box_size=10,
				border=4,
			)
			qr.add_data(qr_data)
			qr.make(fit=True)

			img = qr.make_image(fill_color="black", back_color="white")

			# Convert to base64
			buffered = BytesIO()
			img.save(buffered, format="PNG")
			img_str = base64.b64encode(buffered.getvalue()).decode()

			return {
				"status": "success",
				"qr_code": f"data:image/png;base64,{img_str}",
				"qr_data": qr_data,
				"amount": amount,
				"reference": order.name,
			}

		except Exception as e:
			frappe.logger().error(f"Error generating QR: {str(e)}")
			return {
				"status": "error",
				"message": str(e),
			}

	@staticmethod
	def verify_payment(reference, amount=None):
		"""
		Verify if payment was made for QR reference
		This would normally call a bank API or check a payment processor
		"""
		try:
			# In a real implementation, this would check with the payment processor
			# For now, we'll simulate by checking a payment log table
			payment = frappe.db.get_value(
				"QR Payment Log",
				{"reference": reference, "status": "Paid"},
				["name", "amount", "payment_date"]
			)

			if payment:
				return {
					"status": "success",
					"paid": True,
					"amount": payment[1],
				}
			else:
				return {
					"status": "success",
					"paid": False,
					"amount": None,
				}

		except Exception as e:
			frappe.logger().error(f"Error verifying payment: {str(e)}")
			return {
				"status": "error",
				"message": str(e),
			}


def verify_qr_payment(order, payment_data):
	"""Verify QR payment for an order"""
	try:
		gateway = QRSimpleGateway()

		# Verify payment
		result = gateway.verify_payment(order.name, order.total)

		if result.get("status") == "success" and result.get("paid"):
			# Log payment
			log_payment(order.name, "QR Simple", order.total, "Completed", order.name)

			return {
				"status": "success",
				"message": "Payment verified",
				"reference": order.name,
			}
		else:
			return {
				"status": "error",
				"message": "Payment not verified",
			}

	except Exception as e:
		frappe.logger().error(f"Error verifying QR payment: {str(e)}")
		return {
			"status": "error",
			"message": str(e),
		}


def generate_qr_for_order(order):
	"""Generate QR code for order"""
	try:
		gateway = QRSimpleGateway()
		result = gateway.generate_qr(order, order.total)

		if result.get("status") == "success":
			# Save QR data
			order.custom_fields = str({
				"qr_code": result.get("qr_code"),
				"qr_data": result.get("qr_data"),
			})
			order.save()

		return result

	except Exception as e:
		frappe.logger().error(f"Error generating QR for order: {str(e)}")
		return {
			"status": "error",
			"message": str(e),
		}


def handle_webhook(payload):
	"""Handle webhook from QR Simple payment processor"""
	try:
		order_id = payload.get("reference")
		amount = payload.get("amount")
		status = payload.get("status")  # Paid, Failed, Pending

		if not order_id:
			return {
				"status": "error",
				"message": "Missing order ID in webhook",
			}

		# Get order
		order = frappe.get_doc("Online Order", order_id)

		if status == "Paid":
			# Update payment status
			order.update_payment_status("Paid", payload.get("transaction_id", ""))

			# Log payment
			log_payment(order_id, "QR Simple", amount, "Completed", payload.get("transaction_id"))

			frappe.logger().info(f"Payment confirmed for order {order_id}")

		elif status == "Failed":
			order.update_payment_status("Failed", "")
			frappe.logger().warning(f"Payment failed for order {order_id}")

		return {"status": "success"}

	except Exception as e:
		frappe.logger().error(f"Error in QR webhook handler: {str(e)}")
		return {
			"status": "error",
			"message": str(e),
		}


def verify_pending_payments():
	"""
	Scheduled task: Verify pending QR payments
	"""
	try:
		# Get pending orders
		pending_orders = frappe.db.get_list(
			"Online Order",
			filters={
				"payment_status": "Pending",
				"payment_method": "QR Simple",
			},
			fields=["name", "total"],
		)

		verified_count = 0

		for order_data in pending_orders:
			try:
				order = frappe.get_doc("Online Order", order_data["name"])
				gateway = QRSimpleGateway()

				result = gateway.verify_payment(order.name, order.total)

				if result.get("status") == "success" and result.get("paid"):
					order.update_payment_status("Paid", order.name)
					verified_count += 1

			except Exception as e:
				frappe.logger().error(f"Error verifying payment for {order_data['name']}: {str(e)}")

		frappe.logger().info(f"Verified {verified_count} pending QR payments")

	except Exception as e:
		frappe.logger().error(f"Error in verify_pending_payments: {str(e)}")


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
