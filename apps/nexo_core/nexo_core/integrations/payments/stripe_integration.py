"""
Integración con Stripe para pagos internacionales

Soporta tarjetas de crédito y débito internacionales
"""

import frappe
from frappe import _
import requests

try:
    import stripe
except ImportError:
    frappe.msgprint("Instala stripe: pip install stripe")


class StripePaymentGateway:
    """Gateway para procesar pagos con Stripe"""

    def __init__(self):
        self.api_key = self._get_config('stripe_secret_key')
        self.publishable_key = self._get_config('stripe_publishable_key')
        self.webhook_secret = self._get_config('stripe_webhook_secret')

        if not self.api_key:
            frappe.throw(_("Stripe API key not configured"))

        stripe.api_key = self.api_key

    def _get_config(self, key):
        """Obtiene configuración de Integration Config"""
        try:
            config = frappe.get_single('Integration Config')
            return config.get(key)
        except frappe.DoesNotExistError:
            return None

    def create_payment_intent(self, amount, currency='USD', metadata=None, description=None):
        """
        Crea Payment Intent en Stripe

        Args:
            amount: Monto en dólares/euros/etc
            currency: Código de moneda (USD, EUR, etc)
            metadata: Datos adicionales
            description: Descripción del pago

        Returns:
            dict: Client secret y payment intent ID
        """
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Convertir a centavos
                currency=currency.lower(),
                metadata=metadata or {},
                description=description,
                automatic_payment_methods={'enabled': True}
            )

            self._log_transaction('payment_intent_created', intent.id, amount, intent.status)

            return {
                'success': True,
                'client_secret': intent.client_secret,
                'payment_intent_id': intent.id,
                'amount': amount,
                'currency': currency
            }
        except stripe.error.StripeError as e:
            frappe.log_error(f"Stripe Error: {str(e)}", "Stripe Payment Intent Failed")
            return {
                'success': False,
                'error': str(e)
            }

    def confirm_payment(self, payment_intent_id):
        """
        Confirma estado de un payment intent

        Args:
            payment_intent_id: ID del payment intent

        Returns:
            dict: Status del pago
        """
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)

            status_map = {
                'succeeded': 'Paid',
                'processing': 'Processing',
                'requires_payment_method': 'Pending',
                'requires_action': 'Requires Action',
                'canceled': 'Cancelled'
            }

            if intent.status == 'succeeded':
                self._log_transaction('payment_confirmed', payment_intent_id, intent.amount / 100, 'succeeded')

            return {
                'success': True,
                'status': status_map.get(intent.status, intent.status),
                'amount': intent.amount / 100,
                'charges': intent.charges.data[0].id if intent.charges.data else None
            }
        except stripe.error.StripeError as e:
            frappe.log_error(f"Stripe Error: {str(e)}", "Stripe Payment Confirmation Failed")
            return {
                'success': False,
                'error': str(e)
            }

    def create_customer(self, email, name, metadata=None):
        """
        Crea cliente en Stripe para futuras transacciones

        Args:
            email: Email del cliente
            name: Nombre completo
            metadata: Datos adicionales

        Returns:
            str: ID del cliente en Stripe
        """
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata=metadata or {}
            )
            return customer.id
        except stripe.error.StripeError as e:
            frappe.log_error(f"Stripe Error: {str(e)}", "Stripe Customer Creation Failed")
            raise Exception(f"Failed to create Stripe customer: {str(e)}")

    def create_payment_method(self, stripe_customer_id, card_data):
        """
        Crea método de pago para cliente existente

        Args:
            stripe_customer_id: ID del cliente en Stripe
            card_data: Datos de la tarjeta

        Returns:
            dict: ID del método de pago
        """
        try:
            payment_method = stripe.PaymentMethod.create(
                type='card',
                card=card_data,
                billing_details={'email': stripe.Customer.retrieve(stripe_customer_id).email}
            )

            stripe.PaymentMethod.attach(
                payment_method.id,
                customer=stripe_customer_id
            )

            return {
                'success': True,
                'payment_method_id': payment_method.id
            }
        except stripe.error.StripeError as e:
            frappe.log_error(f"Stripe Error: {str(e)}", "Payment Method Creation Failed")
            return {
                'success': False,
                'error': str(e)
            }

    def refund_payment(self, payment_intent_id, amount=None):
        """
        Reembolsa un pago completamente o parcialmente

        Args:
            payment_intent_id: ID del payment intent
            amount: Monto a reembolsar (None = total)

        Returns:
            dict: Resultado del reembolso
        """
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)

            if not intent.charges.data:
                return {'success': False, 'error': 'No charges found'}

            charge_id = intent.charges.data[0].id

            refund_params = {'charge': charge_id}
            if amount:
                refund_params['amount'] = int(amount * 100)

            refund = stripe.Refund.create(**refund_params)

            self._log_transaction('refund_processed', refund.id, refund.amount / 100, 'refunded')

            return {
                'success': True,
                'refund_id': refund.id,
                'amount': refund.amount / 100,
                'status': refund.status
            }
        except stripe.error.StripeError as e:
            frappe.log_error(f"Stripe Error: {str(e)}", "Stripe Refund Failed")
            return {
                'success': False,
                'error': str(e)
            }

    def list_payment_methods(self, stripe_customer_id):
        """
        Lista métodos de pago de un cliente

        Args:
            stripe_customer_id: ID del cliente en Stripe

        Returns:
            list: Métodos de pago disponibles
        """
        try:
            payment_methods = stripe.PaymentMethod.list(customer=stripe_customer_id, type='card')
            return {
                'success': True,
                'payment_methods': [
                    {
                        'id': pm.id,
                        'card': {
                            'brand': pm.card.brand,
                            'last4': pm.card.last4,
                            'exp_month': pm.card.exp_month,
                            'exp_year': pm.card.exp_year
                        }
                    }
                    for pm in payment_methods.data
                ]
            }
        except stripe.error.StripeError as e:
            return {'success': False, 'error': str(e)}

    def _log_transaction(self, status, transaction_id, amount, stripe_status=''):
        """
        Registra transacción en Integration Log

        Args:
            status: Estado de la transacción
            transaction_id: ID de la transacción
            amount: Monto
            stripe_status: Estado en Stripe
        """
        try:
            frappe.get_doc({
                'doctype': 'Integration Log',
                'integration': 'Stripe',
                'status': status,
                'transaction_id': transaction_id,
                'amount': amount,
                'content': f"Stripe Status: {stripe_status}"
            }).insert(ignore_permissions=True)
            frappe.db.commit()
        except Exception as e:
            frappe.log_error(str(e), "Failed to log Stripe transaction")


@frappe.whitelist()
def create_payment_intent(order_id, currency='USD'):
    """
    API endpoint: Crea payment intent para orden

    Args:
        order_id: ID de la orden
        currency: Moneda (USD, EUR, etc)

    Returns:
        dict: Client secret para frontend
    """
    try:
        order = frappe.get_doc('Online Order', order_id)

        gateway = StripePaymentGateway()
        result = gateway.create_payment_intent(
            amount=float(order.total),
            currency=currency,
            metadata={
                'order_id': order.name,
                'customer': order.customer
            },
            description=f"Order {order.name}"
        )

        return result
    except Exception as e:
        frappe.log_error(str(e), "Create Payment Intent Error")
        return {'success': False, 'error': str(e)}


@frappe.whitelist()
def confirm_stripe_payment(payment_intent_id, order_id=None):
    """
    API endpoint: Confirma pago en Stripe

    Args:
        payment_intent_id: ID del payment intent
        order_id: ID de la orden (opcional)

    Returns:
        dict: Estado del pago
    """
    try:
        gateway = StripePaymentGateway()
        result = gateway.confirm_payment(payment_intent_id)

        # Actualizar orden si fue pagada
        if result['success'] and result['status'] == 'Paid' and order_id:
            order = frappe.get_doc('Online Order', order_id)
            order.payment_status = 'Paid'
            order.stripe_payment_id = payment_intent_id
            order.save()
            frappe.db.commit()

        return result
    except Exception as e:
        frappe.log_error(str(e), "Confirm Payment Error")
        return {'success': False, 'error': str(e)}


@frappe.whitelist(allow_guest=True)
def stripe_webhook_handler():
    """
    Webhook handler para eventos de Stripe

    Debe configurarse en el dashboard de Stripe
    """
    import json

    payload = frappe.request.get_data()
    sig_header = frappe.get_request_header('Stripe-Signature')
    webhook_secret = frappe.get_single('Integration Config').stripe_webhook_secret

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)

        # Procesar evento
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            order_id = payment_intent.get('metadata', {}).get('order_id')

            if order_id:
                order = frappe.get_doc('Online Order', order_id)
                order.payment_status = 'Paid'
                order.stripe_payment_id = payment_intent['id']
                order.save()
                frappe.db.commit()

                # Triggear webhooks personalizados
                from nexo_core.integrations.api_gateway.webhook_manager import trigger_webhooks
                trigger_webhooks('payment.received', {
                    'payment_id': payment_intent['id'],
                    'order_id': order_id,
                    'amount': payment_intent['amount'] / 100,
                    'currency': payment_intent['currency'],
                    'timestamp': payment_intent['created']
                })

        elif event['type'] == 'charge.refunded':
            charge = event['data']['object']
            # Procesar reembolso
            frappe.log_error(f"Refund processed: {charge['id']}", "Stripe Refund Webhook")

        return {'success': True}

    except ValueError as e:
        frappe.log_error(str(e), "Stripe Webhook Invalid Payload")
        return {'success': False, 'error': 'Invalid payload'}
    except stripe.error.SignatureVerificationError as e:
        frappe.log_error(str(e), "Stripe Webhook Signature Error")
        return {'success': False, 'error': 'Invalid signature'}
    except Exception as e:
        frappe.log_error(str(e), "Stripe Webhook Error")
        return {'success': False, 'error': str(e)}
