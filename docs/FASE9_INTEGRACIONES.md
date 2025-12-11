# Fase 9: Integraciones Externas y APIs Avanzadas

**Fecha de Implementación:** 11 de Diciembre, 2024
**Estado:** ✅ Completado
**Versión:** 1.0.0

## Descripción General

Fase 9 implementa un sistema completo de integraciones con servicios externos y APIs avanzadas para Nexo ERP. Incluye:

- WhatsApp Business API para notificaciones
- Payment Gateways locales e internacionales (Stripe, QR Interbank, Tigo Money, PagoFácil)
- Integraciones de envío (Chilexpress, BlueExpress)
- Almacenamiento en la nube (Google Drive, Dropbox, AWS S3)
- Email Marketing (SendGrid, Mailchimp)
- API Gateway con OpenAPI, Rate Limiting y Webhooks personalizables

## Tabla de Contenidos

1. [Integraciones Implementadas](#integraciones-implementadas)
2. [WhatsApp Integration](#whatsapp-integration)
3. [Payment Gateways](#payment-gateways)
4. [Shipping Integration](#shipping-integration)
5. [Cloud Storage](#cloud-storage)
6. [Email Marketing](#email-marketing)
7. [API Gateway](#api-gateway)
8. [DocTypes](#doctypes)
9. [Configuration](#configuration)
10. [API Endpoints](#api-endpoints)
11. [Webhooks](#webhooks)
12. [Testing](#testing)
13. [Troubleshooting](#troubleshooting)

---

## Integraciones Implementadas

### 1. WhatsApp Business API ✅

**Ubicación:** `/home/user/nexo/apps/nexo_core/nexo_core/integrations/whatsapp/`

#### Funcionalidades:
- ✅ Envío de mensajes simples
- ✅ Uso de templates aprobados
- ✅ Notificaciones de facturas
- ✅ Confirmación de pedidos
- ✅ Notificaciones de envío
- ✅ Chatbot básico con intención de usuario
- ✅ Webhook para recibir mensajes

#### Archivos:
- `client.py` - Cliente WhatsApp API
- `notifications.py` - Hooks de notificaciones automáticas
- `templates.py` - Templates de mensajes
- `chatbot.py` - Chatbot básico

#### Configuración Requerida:
```
Integration Config (Single):
- whatsapp_phone_number_id: ID del teléfono registrado
- whatsapp_access_token: Token de acceso (Password)
- whatsapp_test_number: Número para pruebas (591...)
- whatsapp_webhook_token: Token para webhook
```

#### Ejemplo de Uso:

```python
# Enviar mensaje simple
from nexo_core.integrations.whatsapp.client import WhatsAppClient

client = WhatsAppClient()
result = client.send_message('59171234567', 'Hola! Tu pedido fue confirmado')

# Enviar notificación de factura
result = client.send_invoice_notification('INV-2024-001')

# Chatbot
from nexo_core.integrations.whatsapp.chatbot import WhatsAppChatbot
chatbot = WhatsAppChatbot()
response = chatbot.process_message('59171234567', 'Dónde está mi pedido?')
```

### 2. Payment Gateways ✅

**Ubicación:** `/home/user/nexo/apps/nexo_core/nexo_core/integrations/payments/`

#### Stripe Integration

**Soporta:** Tarjetas internacionales (USD, EUR, etc.)

```python
from nexo_core.integrations.payments.stripe_integration import StripePaymentGateway

gateway = StripePaymentGateway()

# Crear payment intent
intent = gateway.create_payment_intent(
    amount=100.00,
    currency='USD',
    metadata={'order_id': 'ORD-001'}
)

# Confirmar pago
result = gateway.confirm_payment(intent['payment_intent_id'])

# Reembolso
refund = gateway.refund_payment(intent['payment_intent_id'])
```

**Webhook Endpoint:** `/api/method/nexo_core.integrations.payments.stripe_integration.stripe_webhook_handler`

#### QR Interbank (Bolivia)

**Soporta:** Pagos QR simples en Bolivia

```python
from nexo_core.integrations.payments.qr_interbank import QRInterbankGateway

gateway = QRInterbankGateway()

# Generar QR de pago
qr = gateway.generate_qr(
    order_id='ORD-001',
    amount=500.00,
    description='Pago de orden ORD-001'
)

# Verificar si fue pagado
status = gateway.verify_payment(qr['qr_id'])

if status['paid']:
    print(f"QR pagado! Transacción: {status['transaction_id']}")
```

#### Tigo Money (Bolivia)

```python
from nexo_core.integrations.payments.tigo_money import TigoMoneyGateway

gateway = TigoMoneyGateway()
result = gateway.create_payment_request(
    order_id='ORD-001',
    amount=500.00,
    phone_number='591XXXXXXX',
    description='Pago de orden'
)
```

#### PagoFácil (Bolivia)

```python
from nexo_core.integrations.payments.pagofacil import PagoFacilGateway

gateway = PagoFacilGateway()
result = gateway.create_transaction(
    order_id='ORD-001',
    amount=500.00,
    card_token='CARD_TOKEN',
    description='Pago de orden'
)
```

### 3. Shipping Integration ✅

**Ubicación:** `/home/user/nexo/apps/nexo_core/nexo_core/integrations/shipping/`

#### Chilexpress

```python
from nexo_core.integrations.shipping.chilexpress import ChilexpressAPI

api = ChilexpressAPI()

# Calcular costo
shipping = api.calculate_shipping(
    origin_city='LP',  # La Paz
    dest_city='CB',     # Cochabamba
    weight_kg=2.5
)

# Crear envío
shipment = api.create_shipment('ORD-001')
print(f"Tracking: {shipment['tracking_number']}")

# Rastrear
tracking = api.track_shipment('CX123456789')
print(f"Status: {tracking['status']}")
```

#### BlueExpress

```python
from nexo_core.integrations.shipping.blueexpress import BlueExpressAPI

api = BlueExpressAPI()

# Crear envío
shipment = api.create_shipment('ORD-001')

# Obtener etiqueta
label = api.generate_label(shipment['tracking_number'])
```

### 4. Cloud Storage ✅

**Ubicación:** `/home/user/nexo/apps/nexo_core/nexo_core/integrations/storage/`

#### Google Drive

```python
from nexo_core.integrations.storage.google_drive import GoogleDriveBackup

backup = GoogleDriveBackup()
result = backup.upload_backup('nexo_backup_20241211.sql.gz', backup_data)
files = backup.list_backups()
```

#### AWS S3

```python
from nexo_core.integrations.storage.aws_s3 import S3Backup

s3 = S3Backup()
result = s3.upload_backup('nexo_backup_20241211.sql.gz', backup_data)
files = s3.list_backups()
```

### 5. Email Marketing ✅

**Ubicación:** `/home/user/nexo/apps/nexo_core/nexo_core/integrations/email/`

#### SendGrid

```python
from nexo_core.integrations.email.sendgrid import SendGridClient

client = SendGridClient()

# Enviar email
result = client.send_email(
    to_email='customer@example.com',
    subject='Tu pedido ha sido enviado',
    html_content='<h1>Pedido enviado!</h1>'
)

# Crear campaña
campaign = client.create_campaign(
    campaign_name='Promoción Navidad',
    subject='¡Descuentos especiales!',
    html_content='<h1>50% OFF</h1>',
    list_id='LIST_ID'
)
```

#### Mailchimp

```python
from nexo_core.integrations.email.mailchimp import MailchimpClient

client = MailchimpClient()

# Suscribir email
result = client.add_subscriber(
    list_id='LIST_ID',
    email='customer@example.com',
    first_name='Juan',
    last_name='Pérez'
)
```

---

## API Gateway

**Ubicación:** `/home/user/nexo/apps/nexo_core/nexo_core/integrations/api_gateway/`

### OpenAPI Specification

Accede a la documentación completa en:

```
GET /api/method/nexo_core.integrations.api_gateway.openapi.get_openapi_spec
```

**Swagger UI:**
```
GET /api/method/nexo_core.integrations.api_gateway.openapi.get_swagger_ui
```

### Rate Limiting

Todos los endpoints están sujetos a rate limiting automático:

```python
@frappe.whitelist()
@rate_limit(max_requests=1000, window_seconds=3600)
def get_products():
    """API con límite de 1000 requests por hora"""
    return frappe.get_all('Item', fields=['name', 'item_name', 'standard_rate'])
```

**Headers de Rate Limit en Respuestas:**
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1702340400
```

### API Keys

Crear una API key:
```
POST /api/method/nexo_core.integrations.api_gateway.rate_limiter.create_api_key_for_user
```

Listar tus API keys:
```
GET /api/method/nexo_core.integrations.api_gateway.rate_limiter.list_my_api_keys
```

---

## DocTypes

### Integration Config (Single)

Almacena todas las credenciales de integraciones externas.

**Campos principales:**
- WhatsApp Business API
- Stripe
- QR Interbank
- Tigo Money
- PagoFácil
- Chilexpress
- BlueExpress
- Google Drive
- Dropbox
- AWS S3
- SendGrid
- Mailchimp

### Webhook Subscription

Permite que usuarios suscriban a eventos del sistema.

**Campos:**
- `webhook_url` (Data): URL del webhook
- `event` (Select): Evento a suscribirse
- `secret` (Password): Secret para firmar payloads
- `enabled` (Check): Activado/Desactivado
- `user` (Link): Usuario propietario
- `last_triggered` (Datetime): Última ejecución

### API Key

Gestión de API keys para clientes REST.

**Campos:**
- `api_key` (Data): Hash de la key
- `user` (Link): Usuario propietario
- `description` (Text): Descripción
- `enabled` (Check): Activa/Inactiva
- `rate_limit` (Int): Límite por hora
- `expires_on` (Date): Fecha de expiración
- `last_used` (Datetime): Último uso

### Integration Log

Registra todas las transacciones de integraciones.

**Campos:**
- `integration` (Select): Tipo de integración
- `status` (Select): Estado (success, failed, pending, etc.)
- `transaction_id` (Data): ID de transacción
- `reference` (Data): Referencia (orden, factura, etc.)
- `amount` (Currency): Monto
- `content` (Long Text): Contenido/Mensaje
- `error` (Text): Mensaje de error
- `response_time` (Int): Tiempo en ms

---

## Configuration

### Configurar Integration Config

1. **En Frappe Desk:** Ir a `Integration Config`
2. **Completar credenciales** de servicios que usarás:

```
WhatsApp Business API:
- Obtener desde: https://developers.facebook.com/
- phone_number_id: Tu número registrado
- access_token: Token de la app
- webhook_token: Cualquier string aleatorio

Stripe:
- Obtener desde: https://stripe.com/
- secret_key: sk_live_...
- publishable_key: pk_live_...
- webhook_secret: whsec_...

QR Interbank:
- Contactar: soporte@qrbolivia.com
- merchant_id: Tu ID comerciante
- api_key: Tu API key
```

3. **Guardar** la configuración

### Configurar Webhooks

**Para recibir webhooks de Stripe:**

1. Ir a Dashboard de Stripe
2. Settings > Webhooks
3. Agregar endpoint: `https://tudominio.com/api/method/nexo_core.integrations.payments.stripe_integration.stripe_webhook_handler`
4. Seleccionar eventos: `payment_intent.succeeded`, `charge.refunded`
5. Obtener webhook secret y configurar en Integration Config

**Para WhatsApp:**

1. Ir a Facebook Developer Dashboard
2. App Settings > Webhooks
3. Configurar callback URL: `https://tudominio.com/api/method/nexo_core.integrations.whatsapp.chatbot.handle_whatsapp_message`
4. Configurar verify token en Integration Config

---

## API Endpoints

### WhatsApp

```bash
# Enviar factura por WhatsApp
POST /api/method/nexo_core.integrations.whatsapp.client.send_whatsapp_invoice
{
  "invoice_name": "SAI-2024-001"
}

# Confirmar pedido por WhatsApp
POST /api/method/nexo_core.integrations.whatsapp.client.send_whatsapp_order_confirmation
{
  "order_id": "ORD-2024-001"
}

# Prueba de conexión
POST /api/method/nexo_core.integrations.whatsapp.client.test_whatsapp_connection
```

### Payments

```bash
# Crear payment intent Stripe
POST /api/method/nexo_core.integrations.payments.stripe_integration.create_payment_intent
{
  "order_id": "ORD-2024-001",
  "currency": "USD"
}

# Generar QR Interbank
POST /api/method/nexo_core.integrations.payments.qr_interbank.generate_payment_qr
{
  "order_id": "ORD-2024-001",
  "expiration_minutes": 60
}

# Verificar QR pagado
GET /api/method/nexo_core.integrations.payments.qr_interbank.verify_qr_payment?qr_id=QR123456
```

### Shipping

```bash
# Calcular costo de envío
POST /api/method/nexo_core.integrations.shipping.chilexpress.calculate_shipping_cost
{
  "order_id": "ORD-2024-001"
}

# Crear envío Chilexpress
POST /api/method/nexo_core.integrations.shipping.chilexpress.create_chilexpress_shipment
{
  "order_id": "ORD-2024-001"
}

# Rastrear envío
GET /api/method/nexo_core.integrations.shipping.chilexpress.track_chilexpress_shipment?tracking_number=CX123456789
```

### Webhooks

```bash
# Suscribirse a un evento
POST /api/method/nexo_core.integrations.api_gateway.webhook_manager.subscribe_webhook
{
  "url": "https://miapp.com/webhooks/orders",
  "event": "order.created",
  "secret": "mi_secret_key"
}

# Listar webhooks del usuario
GET /api/method/nexo_core.integrations.api_gateway.webhook_manager.list_webhooks

# Desuscribirse
POST /api/method/nexo_core.integrations.api_gateway.webhook_manager.unsubscribe_webhook
{
  "webhook_id": "WH-2024-001"
}

# Obtener eventos disponibles
GET /api/method/nexo_core.integrations.api_gateway.webhook_manager.get_available_events
```

### API Keys

```bash
# Crear nueva API key
POST /api/method/nexo_core.integrations.api_gateway.rate_limiter.create_api_key_for_user
{
  "description": "Mobile App Integration",
  "rate_limit": 5000
}

# Listar mis API keys
GET /api/method/nexo_core.integrations.api_gateway.rate_limiter.list_my_api_keys

# Revocar API key
POST /api/method/nexo_core.integrations.api_gateway.rate_limiter.revoke_api_key
{
  "api_key_id": "KEY-2024-001"
}
```

---

## Webhooks

### Eventos Disponibles

```
invoice.created - Factura creada
invoice.paid - Factura pagada
invoice.cancelled - Factura cancelada
order.created - Orden creada
order.confirmed - Orden confirmada
order.shipped - Orden enviada
order.delivered - Orden entregada
order.cancelled - Orden cancelada
payment.received - Pago recibido
payment.failed - Pago fallido
customer.created - Cliente creado
customer.updated - Cliente actualizado
product.created - Producto creado
product.updated - Producto actualizado
product.deleted - Producto eliminado
```

### Ejemplo de Webhook

Suscribirse:
```bash
curl -X POST https://nexo.bo/api/method/nexo_core.integrations.api_gateway.webhook_manager.subscribe_webhook \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://tuapp.com/webhooks/orders",
    "event": "order.created",
    "secret": "tu_secret_clave"
  }'
```

Webhook recibido en tu servidor:
```json
POST /webhooks/orders

Headers:
X-Webhook-Signature: sha256_hash_del_payload
X-Webhook-Signature-Algorithm: sha256
X-Webhook-Timestamp: 2024-12-11T19:50:00Z

Body:
{
  "order_id": "ORD-2024-001",
  "customer": "CUST-001",
  "total": 500.00,
  "status": "Confirmed",
  "date": "2024-12-11T19:50:00Z",
  "event": "order.created",
  "timestamp": "2024-12-11T19:50:00Z"
}
```

Validar firma:
```python
import hmac
import hashlib

signature = request.headers.get('X-Webhook-Signature')
payload = request.get_data(as_text=True)
secret = 'tu_secret_clave'

expected_signature = hmac.new(
    secret.encode(),
    payload.encode(),
    hashlib.sha256
).hexdigest()

if hmac.compare_digest(signature, expected_signature):
    # Webhook válido
    pass
```

---

## Testing

### Tests Implementados

Ubicación: `/home/user/nexo/apps/nexo_core/nexo_core/integrations/tests/`

```bash
# Ejecutar todos los tests de integraciones
frappe exec bench --app nexo_core run-tests

# Ejecutar tests específicos
frappe exec bench --app nexo_core run-tests --module integrations.whatsapp
frappe exec bench --app nexo_core run-tests --module integrations.payments
```

### Ejemplos de Tests

```python
# Test WhatsApp
def test_send_whatsapp_message():
    from nexo_core.integrations.whatsapp.client import WhatsAppClient

    client = WhatsAppClient()
    result = client.send_message('59171234567', 'Test')
    assert result is not None

# Test Stripe
def test_create_payment_intent():
    from nexo_core.integrations.payments.stripe_integration import StripePaymentGateway

    gateway = StripePaymentGateway()
    result = gateway.create_payment_intent(100.00, 'USD')
    assert result['success'] == True
    assert 'client_secret' in result

# Test Webhooks
def test_trigger_webhook():
    from nexo_core.integrations.api_gateway.webhook_manager import trigger_webhooks

    trigger_webhooks('order.created', {
        'order_id': 'ORD-001',
        'total': 500.00
    })
    # Verificar que se creó log
    assert frappe.get_list('Integration Log', {'status': 'success'})
```

---

## Troubleshooting

### WhatsApp

**Problema:** "WhatsApp configuration not found"
```
Solución:
1. Ir a Integration Config
2. Completar phone_number_id y access_token
3. Guardar
```

**Problema:** "Failed to send WhatsApp message"
```
Solución:
1. Verificar que el token sea válido
2. Verificar que el número esté en formato correcto (591XXXXXXXX)
3. Verificar logs en Integration Log
```

### Stripe

**Problema:** "Stripe API key not configured"
```
Solución:
1. Obtener keys de https://stripe.com/dashboard
2. Configurar en Integration Config
3. Guardar
```

**Problema:** "Failed to confirm payment"
```
Solución:
1. Verificar que payment_intent_id sea válido
2. Revisar Payment Entry para el status
3. Consultar logs de Stripe webhook
```

### QR Interbank

**Problema:** "QR generation failed"
```
Solución:
1. Verificar que merchant_id y api_key sean correctos
2. Verificar que amount sea válido
3. Contactar soporte de QR Interbank
```

### Webhooks

**Problema:** "Webhook not delivering"
```
Solución:
1. Verificar URL es pública y accesible
2. Revisar Integration Log para detalles del error
3. Probar endpoint manualmente con curl
4. Verificar firewall/CORS
```

**Problema:** "Invalid webhook signature"
```
Solución:
1. Verificar que secret coincida
2. Usar payload raw (no procesado)
3. Revisar algoritmo (debe ser SHA256)
```

---

## Resumen de Cambios

### Archivos Creados: 30+
- WhatsApp: 4 archivos
- Payments: 5 archivos
- Shipping: 3 archivos
- Storage: 4 archivos
- Email: 3 archivos
- API Gateway: 3 archivos
- DocTypes: 8 archivos (JSON + Python)

### DocTypes Creados: 4
- Integration Config
- Webhook Subscription
- API Key
- Integration Log

### Hooks Actualizados: 5+
- Sales Invoice (on_submit)
- Payment Entry (on_submit)
- Online Order (on_submit, on_update)
- Customer (on_submit)

### Endpoints API: 20+
- WhatsApp: 3 endpoints
- Payments: 6 endpoints
- Shipping: 3 endpoints
- Webhooks: 5 endpoints
- API Keys: 3 endpoints

### Eventos de Webhook: 15
- invoice.* (3)
- order.* (5)
- payment.* (2)
- customer.* (2)
- product.* (3)

---

## Próximos Pasos

### Mejoras Futuras:
1. Integración con Google Analytics
2. Facebook Pixel tracking
3. Sentry error tracking
4. Datadog monitoring
5. GraphQL endpoint
6. Documentación OpenAPI mejorada
7. Test coverage 100%
8. Dashboard de estadísticas de integraciones

### Para Producción:
1. Implementar encriptación de credenciales
2. Agregar audit logging
3. Rate limiting más sofisticado
4. Monitoreo de health checks
5. Retry logic con backoff exponencial
6. Cache de respuestas de integraciones

---

## Contacto y Soporte

**Email:** support@nexo.bo
**Documentación:** https://nexo.bo/docs
**GitHub:** https://github.com/nexo-erp/integrations

---

**Versión:** 1.0.0
**Última actualización:** 11 de Diciembre, 2024
**Autor:** Aero
**Licencia:** GNU General Public License (v3)
