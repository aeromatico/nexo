# API Reference - Nexo ERP v1.0.0

Documentación completa de todas las APIs REST disponibles en Nexo ERP.

**Total de APIs documentadas**: 150+ endpoints

---

## Tabla de Contenidos

1. [Autenticación](#autenticación)
2. [Multi-tenant SaaS (nexo_core)](#multi-tenant-saas)
3. [Localización Bolivia (nexo_bolivia)](#localización-bolivia)
4. [E-commerce](#e-commerce)
5. [Analytics y BI](#analytics-y-bi)
6. [Integraciones Externas](#integraciones-externas)
7. [Webhooks](#webhooks)
8. [Rate Limiting](#rate-limiting)
9. [Códigos de Error](#códigos-de-error)
10. [Ejemplos de Uso](#ejemplos-de-uso)

---

## Autenticación

### Token Authentication (Recomendado)

```bash
# Obtener token
curl -X POST https://api.nexo.bo/api/method/frappe.auth.get_logged_in_user \
  -H "Content-Type: application/json" \
  -d '{"username": "user@example.com", "password": "password"}'

# Usar token en requests
curl https://api.nexo.bo/api/method/nexo_core.api.get_tenants \
  -H "Authorization: token YOUR_API_TOKEN:YOUR_API_SECRET"
```

### OAuth2

```bash
# Autorización
GET https://api.nexo.bo/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&redirect_uri=YOUR_CALLBACK

# Token
POST https://api.nexo.bo/api/oauth2/token \
  -d "grant_type=authorization_code&code=AUTH_CODE&client_id=CLIENT_ID&client_secret=SECRET"
```

### JWT Token

```bash
# Crear token JWT
POST https://api.nexo.bo/api/method/nexo_core.api.create_jwt_token
{
  "username": "user@example.com",
  "expiry_days": 30
}

# Usar en header
Authorization: Bearer YOUR_JWT_TOKEN
```

---

## Multi-tenant SaaS

### Gestión de Tenants

#### Listar todos los tenants
```
GET /api/method/nexo_core.api.get_tenants
```

**Parámetros:**
- `limit` (int, optional): Límite de resultados (default: 50)
- `offset` (int, optional): Offset para paginación (default: 0)
- `filter` (str, optional): Filtro por nombre o estado

**Response:**
```json
{
  "message": [
    {
      "name": "empresa1",
      "company_name": "Empresa 1 SRL",
      "domain": "empresa1.nexo.bo",
      "plan": "professional",
      "status": "active",
      "users": 5,
      "created_at": "2024-11-01T10:00:00"
    }
  ]
}
```

#### Crear nuevo tenant
```
POST /api/method/nexo_core.api.create_tenant
```

**Body:**
```json
{
  "subdomain": "miempresa",
  "company_name": "Mi Empresa SRL",
  "admin_email": "admin@miempresa.bo",
  "admin_password": "secure_password",
  "plan": "starter",
  "country_code": "BO",
  "nit": "1234567890"
}
```

**Response:**
```json
{
  "message": {
    "tenant_id": "empresa1",
    "site_name": "empresa1.nexo.bo",
    "admin_url": "https://empresa1.nexo.bo/app/home",
    "api_key": "YOUR_API_KEY",
    "api_secret": "YOUR_API_SECRET"
  }
}
```

#### Obtener detalles de tenant
```
GET /api/method/nexo_core.api.get_tenant?tenant_id=TENANT_ID
```

#### Actualizar tenant
```
PUT /api/method/nexo_core.api.update_tenant
```

**Body:**
```json
{
  "tenant_id": "empresa1",
  "company_name": "Mi Empresa SRL Actualizada",
  "plan": "enterprise",
  "settings": {
    "invoice_prefix": "INV-",
    "fiscal_year": "2024"
  }
}
```

#### Eliminar tenant
```
DELETE /api/method/nexo_core.api.delete_tenant?tenant_id=TENANT_ID
```

---

## Localización Bolivia

### Plan Contable

#### Obtener plan contable
```
GET /api/method/nexo_bolivia.accounting.get_chart_of_accounts
```

**Parámetros:**
- `company` (str, required): Nombre de la empresa

**Response:**
```json
{
  "message": [
    {
      "account_code": "1000",
      "account_name": "ACTIVOS",
      "account_type": "Root",
      "is_group": true,
      "balance": 150000.00,
      "currency": "BOB"
    },
    {
      "account_code": "1100",
      "account_name": "Bancos",
      "account_type": "Asset",
      "parent_account": "1000",
      "balance": 85000.00
    }
  ]
}
```

### Impuestos

#### Calcular IVA
```
POST /api/method/nexo_bolivia.tax_engine.iva.calculate_iva
```

**Body:**
```json
{
  "amount": 1000.00,
  "tax_rate": 13,
  "include_tax": false
}
```

**Response:**
```json
{
  "message": {
    "base_amount": 1000.00,
    "tax_rate": 13,
    "tax_amount": 130.00,
    "total_amount": 1130.00
  }
}
```

#### Calcular IT (Impuesto a Transacciones)
```
POST /api/method/nexo_bolivia.tax_engine.it.calculate_it
```

**Body:**
```json
{
  "amount": 5000.00,
  "tax_rate": 3
}
```

#### Calcular IUE (Impuesto a Utilidades)
```
POST /api/method/nexo_bolivia.tax_engine.iue.calculate_iue
```

**Body:**
```json
{
  "revenue": 500000.00,
  "expenses": 300000.00,
  "it_paid": 5000.00,
  "fiscal_year": 2024
}
```

### Facturación SIN

#### Obtener CUFD (Código Único de Facturación)
```
GET /api/method/nexo_bolivia.sin_integration.get_cufd
```

**Response:**
```json
{
  "message": {
    "cufd": "12345678901234567890123456789012345678901234",
    "valid_until": "2024-12-13T00:00:00",
    "status": "valid"
  }
}
```

#### Generar CUF para factura
```
POST /api/method/nexo_bolivia.sin_integration.generate_cuf
```

**Body:**
```json
{
  "nit": "1234567890",
  "invoice_number": 1,
  "amount": 1130.00,
  "date": "2024-12-12"
}
```

**Response:**
```json
{
  "message": {
    "cuf": "ABC123DEF456GHI789JKL012MNO345PQR678STU",
    "qr_code": "BASE64_ENCODED_IMAGE"
  }
}
```

#### Enviar factura a SIAT
```
POST /api/method/nexo_bolivia.sin_integration.send_invoice_to_siat
```

**Body:**
```json
{
  "sales_invoice": "INV-2024-001"
}
```

### Nómina

#### Calcular salario
```
POST /api/method/nexo_bolivia.payroll.salary.calculate_salary
```

**Body:**
```json
{
  "employee": "EMP-001",
  "basic_salary": 3500.00,
  "start_date": "2024-12-01",
  "end_date": "2024-12-31",
  "month": 12,
  "year": 2024
}
```

**Response:**
```json
{
  "message": {
    "basic_salary": 3500.00,
    "seniority_bonus": 350.00,
    "gross_salary": 3850.00,
    "afp_deduction": 489.54,
    "net_salary": 3360.46
  }
}
```

#### Calcular AFP
```
POST /api/method/nexo_bolivia.payroll.afp.calculate_afp
```

**Body:**
```json
{
  "gross_salary": 3850.00,
  "afp_rate": 12.71
}
```

#### Calcular aguinaldo
```
POST /api/method/nexo_bolivia.payroll.aguinaldo.calculate_aguinaldo
```

**Body:**
```json
{
  "employee": "EMP-001",
  "fiscal_year": 2024,
  "type": "simple"  // simple o double
}
```

---

## E-commerce

### Carrito de Compras

#### Obtener carrito del usuario
```
GET /api/method/nexo_core.ecommerce.cart.get_cart
```

**Response:**
```json
{
  "message": {
    "items": [
      {
        "item_code": "PROD-001",
        "quantity": 2,
        "price": 500.00,
        "total": 1000.00
      }
    ],
    "subtotal": 1000.00,
    "tax": 130.00,
    "shipping": 50.00,
    "total": 1180.00
  }
}
```

#### Agregar al carrito
```
POST /api/method/nexo_core.ecommerce.cart.add_to_cart
```

**Body:**
```json
{
  "item_code": "PROD-001",
  "quantity": 2,
  "price": 500.00
}
```

#### Actualizar carrito
```
PUT /api/method/nexo_core.ecommerce.cart.update_cart
```

**Body:**
```json
{
  "items": [
    {
      "item_code": "PROD-001",
      "quantity": 3
    }
  ]
}
```

#### Limpiar carrito
```
POST /api/method/nexo_core.ecommerce.cart.clear_cart
```

### Productos

#### Listar productos
```
GET /api/method/nexo_core.ecommerce.products.get_products?page=1&limit=20
```

**Response:**
```json
{
  "message": [
    {
      "item_code": "PROD-001",
      "name": "Producto 1",
      "description": "Descripción",
      "price": 500.00,
      "currency": "BOB",
      "image": "https://...",
      "stock": 50,
      "category": "Electronics"
    }
  ],
  "total": 100
}
```

#### Obtener detalle de producto
```
GET /api/method/nexo_core.ecommerce.products.get_product_detail?item_code=PROD-001
```

#### Buscar productos
```
GET /api/method/nexo_core.ecommerce.products.search_products?q=laptop&category=Electronics
```

### Checkout y Órdenes

#### Crear orden
```
POST /api/method/nexo_core.ecommerce.checkout.create_order
```

**Body:**
```json
{
  "customer": "CUST-001",
  "items": [
    {
      "item_code": "PROD-001",
      "quantity": 2,
      "price": 500.00
    }
  ],
  "shipping_address": {
    "address_line1": "Av. Principal 123",
    "city": "La Paz",
    "state": "La Paz",
    "postal_code": "2000",
    "country": "Bolivia"
  },
  "payment_gateway": "stripe",
  "total": 1180.00
}
```

**Response:**
```json
{
  "message": {
    "order_id": "ORD-2024-001",
    "status": "pending",
    "payment_intent_id": "pi_1234567890",
    "payment_url": "https://checkout.stripe.com/..."
  }
}
```

#### Procesar pago
```
POST /api/method/nexo_core.ecommerce.checkout.process_payment
```

**Body:**
```json
{
  "order_id": "ORD-2024-001",
  "payment_method": "card",
  "token": "PAYMENT_TOKEN"
}
```

### Integraciones de Pago

#### Stripe: Crear payment intent
```
POST /api/method/nexo_core.ecommerce.payment_gateways.stripe.create_payment_intent
```

**Body:**
```json
{
  "amount": 1180.00,
  "currency": "USD",
  "metadata": {
    "order_id": "ORD-2024-001"
  }
}
```

#### QR Simple: Generar QR
```
POST /api/method/nexo_core.ecommerce.payment_gateways.qr_simple.generate_qr
```

**Body:**
```json
{
  "order_id": "ORD-2024-001",
  "amount": 500.00,
  "description": "Pago de orden"
}
```

#### QR Simple: Verificar pago
```
GET /api/method/nexo_core.ecommerce.payment_gateways.qr_simple.verify_payment?qr_id=QR_ID
```

---

## Analytics y BI

### KPIs

#### Obtener KPI
```
GET /api/method/nexo_core.analytics.kpi_engine.get_kpi?kpi_code=REVENUE_TOTAL
```

**Response:**
```json
{
  "message": {
    "kpi_code": "REVENUE_TOTAL",
    "kpi_name": "Revenue Total",
    "value": 250000.00,
    "unit": "BOB",
    "period": "2024-12",
    "trend": "up",
    "change_percentage": 5.5
  }
}
```

#### Calcular KPI personalizado
```
POST /api/method/nexo_core.analytics.kpi_engine.calculate_custom_kpi
```

**Body:**
```json
{
  "name": "My KPI",
  "calculation_method": "sum",
  "doctype": "Sales Invoice",
  "field": "grand_total",
  "filters": {
    "status": "Submitted",
    "date": {
      "start": "2024-01-01",
      "end": "2024-12-31"
    }
  }
}
```

### Dashboards

#### Obtener dashboard financiero
```
GET /api/method/nexo_core.dashboards.financial.get_financial_dashboard?company=My%20Company
```

**Response:**
```json
{
  "message": {
    "revenue": 250000.00,
    "expenses": 150000.00,
    "profit": 100000.00,
    "charts": {
      "revenue_trend": { "labels": [...], "data": [...] },
      "cash_flow": { "labels": [...], "data": [...] }
    }
  }
}
```

### Reportes

#### Ejecutar reporte
```
POST /api/method/nexo_core.reports.report_builder.execute_report
```

**Body:**
```json
{
  "report_code": "sales_by_customer",
  "filters": {
    "date_start": "2024-01-01",
    "date_end": "2024-12-31",
    "customer": "CUST-001"
  },
  "export_format": "excel"
}
```

#### Listar reportes disponibles
```
GET /api/method/nexo_core.reports.report_builder.list_reports
```

---

## Integraciones Externas

### WhatsApp

#### Enviar mensaje
```
POST /api/method/nexo_core.integrations.whatsapp.client.send_message
```

**Body:**
```json
{
  "phone_number": "59171234567",
  "message": "Hola! Tu pedido fue confirmado"
}
```

#### Enviar notificación de factura
```
POST /api/method/nexo_core.integrations.whatsapp.notifications.send_invoice_notification
```

**Body:**
```json
{
  "sales_invoice": "INV-2024-001"
}
```

### Payment Gateways

#### Stripe: Reembolso
```
POST /api/method/nexo_core.integrations.payments.stripe_integration.refund_payment
```

**Body:**
```json
{
  "payment_intent_id": "pi_1234567890",
  "amount": 1180.00
}
```

#### Tigo Money: Crear solicitud de pago
```
POST /api/method/nexo_core.integrations.payments.tigo_money.create_payment_request
```

**Body:**
```json
{
  "phone_number": "591XXXXXXX",
  "amount": 500.00,
  "description": "Pago de orden ORD-001"
}
```

### Cloud Storage

#### Subir archivo
```
POST /api/method/nexo_core.integrations.cloud_storage.upload_file
```

**Body:**
```
form-data:
  file: <binary>
  storage_provider: "google_drive"
  folder: "invoices"
```

#### Descargar archivo
```
GET /api/method/nexo_core.integrations.cloud_storage.download_file?file_id=FILE_ID&provider=google_drive
```

---

## Webhooks

### Crear webhook
```
POST /api/method/nexo_core.integrations.webhook_manager.create_webhook
```

**Body:**
```json
{
  "webhook_name": "Invoice Created",
  "event_type": "sales_invoice.created",
  "target_url": "https://your-server.com/webhooks/invoice",
  "active": true,
  "events": ["Sales Invoice.after_insert"]
}
```

### Listar webhooks
```
GET /api/method/nexo_core.integrations.webhook_manager.list_webhooks
```

### Probar webhook
```
POST /api/method/nexo_core.integrations.webhook_manager.test_webhook?webhook_id=WEBHOOK_ID
```

### Eventos disponibles
- `sales_invoice.created`
- `sales_invoice.submitted`
- `online_order.created`
- `online_order.submitted`
- `payment_entry.submitted`
- `customer.updated`
- `item.updated`
- Y muchos más...

---

## Rate Limiting

Las APIs de Nexo ERP incluyen rate limiting para evitar abuso:

### Límites Predeterminados
- **Por usuario**: 1000 requests/hora
- **Por IP**: 5000 requests/hora
- **Por endpoint**: 100 requests/minuto

### Headers de Rate Limiting
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1702411200
```

### Incrementar límites
Contacta a soporte para planes enterprise con límites personalizados.

---

## Códigos de Error

### Errores Comunes

| Código | Status | Descripción |
|--------|--------|-------------|
| 400 | Bad Request | Parámetros inválidos |
| 401 | Unauthorized | No autenticado o token inválido |
| 403 | Forbidden | Acceso denegado |
| 404 | Not Found | Recurso no encontrado |
| 409 | Conflict | Conflicto de datos |
| 429 | Too Many Requests | Rate limit excedido |
| 500 | Server Error | Error interno del servidor |

### Respuesta de Error
```json
{
  "exc": "frappe.exceptions.ValidationError",
  "exc_type": "ValidationError",
  "message": "Email is mandatory",
  "_server_messages": "[\"\\\"Email\\\" is mandatory\"]"
}
```

---

## Ejemplos de Uso

### Crear tenant y obtener credenciales
```bash
#!/bin/bash

# 1. Crear tenant
RESPONSE=$(curl -X POST https://api.nexo.bo/api/method/nexo_core.api.create_tenant \
  -H "Authorization: token ADMIN_TOKEN:SECRET" \
  -H "Content-Type: application/json" \
  -d '{
    "subdomain": "cliente1",
    "company_name": "Cliente 1 SRL",
    "admin_email": "admin@cliente1.bo",
    "admin_password": "SecurePass123!",
    "plan": "professional",
    "country_code": "BO",
    "nit": "9999999999"
  }')

# 2. Extraer credenciales
API_KEY=$(echo $RESPONSE | jq -r '.message.api_key')
API_SECRET=$(echo $RESPONSE | jq -r '.message.api_secret')

echo "Credenciales de API:"
echo "API Key: $API_KEY"
echo "API Secret: $API_SECRET"
```

### E-commerce: De carrito a pedido completado
```python
import requests
import json

API_URL = "https://api.nexo.bo/api/method"
HEADERS = {
    "Authorization": "token YOUR_TOKEN:YOUR_SECRET",
    "Content-Type": "application/json"
}

# 1. Agregar al carrito
add_cart = requests.post(
    f"{API_URL}/nexo_core.ecommerce.cart.add_to_cart",
    headers=HEADERS,
    json={
        "item_code": "LAPTOP-001",
        "quantity": 1,
        "price": 5000.00
    }
)

# 2. Obtener carrito actualizado
cart = requests.get(
    f"{API_URL}/nexo_core.ecommerce.cart.get_cart",
    headers=HEADERS
)

# 3. Crear orden
order = requests.post(
    f"{API_URL}/nexo_core.ecommerce.checkout.create_order",
    headers=HEADERS,
    json={
        "items": cart.json()["message"]["items"],
        "shipping_address": {
            "address_line1": "Av. Principal 123",
            "city": "La Paz"
        },
        "payment_gateway": "stripe"
    }
)

print(f"Orden creada: {order.json()['message']['order_id']}")
```

---

## Soporte

Para preguntas sobre la API:
- Email: api-support@nexo.bo
- Documentación: https://docs.nexo.bo
- GitHub Issues: https://github.com/aeromatico/nexo/issues

---

**Última actualización**: 12 de Diciembre, 2024
**API Version**: v1.0.0
**Base URL**: https://api.nexo.bo/api/method/
