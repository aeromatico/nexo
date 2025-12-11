"""
Generador de documentación OpenAPI/Swagger para API REST

Proporciona especificación OpenAPI 3.0 para APIs de Nexo ERP
"""

import frappe
from frappe import _
import json


def generate_openapi_spec():
    """
    Genera especificación OpenAPI 3.0 completa

    Returns:
        dict: Especificación OpenAPI
    """
    spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "Nexo ERP API",
            "description": "REST API para Nexo ERP - Multi-tenant SaaS ERP para Bolivia",
            "version": "2.0.0",
            "contact": {
                "name": "Nexo Support",
                "email": "support@nexo.bo",
                "url": "https://nexo.bo"
            },
            "license": {
                "name": "GNU General Public License (v3)"
            }
        },
        "servers": [
            {
                "url": "https://api.nexo.bo/v2",
                "description": "Production API",
                "variables": {
                    "tenant": {
                        "default": "default",
                        "description": "Tenant ID"
                    }
                }
            },
            {
                "url": "https://staging.nexo.bo/v2",
                "description": "Staging API"
            }
        ],
        "paths": {
            "/customers": generate_customers_paths(),
            "/customers/{customer_id}": generate_customer_detail_paths(),
            "/invoices": generate_invoices_paths(),
            "/orders": generate_orders_paths(),
            "/orders/{order_id}": generate_order_detail_paths(),
            "/products": generate_products_paths(),
            "/payments": generate_payments_paths(),
            "/shipments": generate_shipments_paths(),
            "/webhooks": generate_webhooks_paths(),
            "/analytics/dashboard": generate_analytics_paths()
        },
        "components": {
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                    "description": "JWT access token"
                },
                "apiKey": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "X-API-Key",
                    "description": "API Key for authentication"
                }
            },
            "schemas": {
                "Customer": generate_customer_schema(),
                "Invoice": generate_invoice_schema(),
                "Order": generate_order_schema(),
                "Product": generate_product_schema(),
                "Payment": generate_payment_schema(),
                "Shipment": generate_shipment_schema(),
                "Error": generate_error_schema()
            },
            "responses": {
                "NotFound": {
                    "description": "Resource not found",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/Error"}
                        }
                    }
                },
                "Unauthorized": {
                    "description": "Unauthorized access",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/Error"}
                        }
                    }
                }
            }
        },
        "security": [
            {"bearerAuth": []},
            {"apiKey": []}
        ],
        "tags": [
            {"name": "Customers", "description": "Customer operations"},
            {"name": "Invoices", "description": "Invoice operations"},
            {"name": "Orders", "description": "Order operations"},
            {"name": "Products", "description": "Product operations"},
            {"name": "Payments", "description": "Payment operations"},
            {"name": "Webhooks", "description": "Webhook management"},
            {"name": "Analytics", "description": "Analytics and reporting"}
        ]
    }

    return spec


def generate_customers_paths():
    """Genera paths para customers"""
    return {
        "get": {
            "tags": ["Customers"],
            "summary": "List customers",
            "operationId": "listCustomers",
            "parameters": [
                {
                    "name": "limit",
                    "in": "query",
                    "schema": {"type": "integer", "default": 20}
                },
                {
                    "name": "offset",
                    "in": "query",
                    "schema": {"type": "integer", "default": 0}
                },
                {
                    "name": "search",
                    "in": "query",
                    "schema": {"type": "string"},
                    "description": "Search by name or email"
                }
            ],
            "responses": {
                "200": {
                    "description": "List of customers",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "data": {
                                        "type": "array",
                                        "items": {"$ref": "#/components/schemas/Customer"}
                                    },
                                    "total": {"type": "integer"},
                                    "limit": {"type": "integer"},
                                    "offset": {"type": "integer"}
                                }
                            }
                        }
                    }
                },
                "401": {"$ref": "#/components/responses/Unauthorized"}
            }
        },
        "post": {
            "tags": ["Customers"],
            "summary": "Create customer",
            "operationId": "createCustomer",
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/Customer"}
                    }
                }
            },
            "responses": {
                "201": {
                    "description": "Customer created",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/Customer"}
                        }
                    }
                }
            }
        }
    }


def generate_customer_detail_paths():
    """Genera paths para customer detalle"""
    return {
        "get": {
            "tags": ["Customers"],
            "summary": "Get customer details",
            "parameters": [
                {
                    "name": "customer_id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string"}
                }
            ],
            "responses": {
                "200": {
                    "description": "Customer details",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/Customer"}
                        }
                    }
                },
                "404": {"$ref": "#/components/responses/NotFound"}
            }
        },
        "put": {
            "tags": ["Customers"],
            "summary": "Update customer",
            "parameters": [
                {
                    "name": "customer_id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string"}
                }
            ],
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/Customer"}
                    }
                }
            },
            "responses": {
                "200": {
                    "description": "Customer updated",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/Customer"}
                        }
                    }
                }
            }
        }
    }


def generate_invoices_paths():
    """Genera paths para invoices"""
    return {
        "get": {
            "tags": ["Invoices"],
            "summary": "List invoices",
            "parameters": [
                {"name": "limit", "in": "query", "schema": {"type": "integer"}},
                {"name": "offset", "in": "query", "schema": {"type": "integer"}},
                {"name": "status", "in": "query", "schema": {"type": "string"}}
            ],
            "responses": {
                "200": {
                    "description": "List of invoices",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "data": {
                                        "type": "array",
                                        "items": {"$ref": "#/components/schemas/Invoice"}
                                    },
                                    "total": {"type": "integer"}
                                }
                            }
                        }
                    }
                }
            }
        }
    }


def generate_orders_paths():
    """Genera paths para orders"""
    return {
        "get": {
            "tags": ["Orders"],
            "summary": "List orders",
            "responses": {
                "200": {
                    "description": "List of orders",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "data": {
                                        "type": "array",
                                        "items": {"$ref": "#/components/schemas/Order"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "post": {
            "tags": ["Orders"],
            "summary": "Create order",
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/Order"}
                    }
                }
            },
            "responses": {
                "201": {
                    "description": "Order created",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/Order"}
                        }
                    }
                }
            }
        }
    }


def generate_order_detail_paths():
    """Genera paths para order detalle"""
    return {
        "get": {
            "tags": ["Orders"],
            "summary": "Get order details",
            "parameters": [
                {"name": "order_id", "in": "path", "required": True, "schema": {"type": "string"}}
            ],
            "responses": {
                "200": {
                    "description": "Order details",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/Order"}
                        }
                    }
                }
            }
        }
    }


def generate_products_paths():
    """Genera paths para products"""
    return {
        "get": {
            "tags": ["Products"],
            "summary": "List products",
            "parameters": [
                {"name": "limit", "in": "query", "schema": {"type": "integer"}},
                {"name": "search", "in": "query", "schema": {"type": "string"}}
            ],
            "responses": {
                "200": {
                    "description": "List of products",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "data": {
                                        "type": "array",
                                        "items": {"$ref": "#/components/schemas/Product"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }


def generate_payments_paths():
    """Genera paths para payments"""
    return {
        "get": {
            "tags": ["Payments"],
            "summary": "List payments",
            "responses": {
                "200": {
                    "description": "List of payments",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "data": {
                                        "type": "array",
                                        "items": {"$ref": "#/components/schemas/Payment"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "post": {
            "tags": ["Payments"],
            "summary": "Create payment",
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/Payment"}
                    }
                }
            },
            "responses": {
                "201": {
                    "description": "Payment created",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/Payment"}
                        }
                    }
                }
            }
        }
    }


def generate_shipments_paths():
    """Genera paths para shipments"""
    return {
        "get": {
            "tags": ["Shipments"],
            "summary": "List shipments",
            "responses": {
                "200": {
                    "description": "List of shipments",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "data": {
                                        "type": "array",
                                        "items": {"$ref": "#/components/schemas/Shipment"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }


def generate_webhooks_paths():
    """Genera paths para webhooks"""
    return {
        "get": {
            "tags": ["Webhooks"],
            "summary": "List webhook subscriptions",
            "responses": {
                "200": {
                    "description": "List of webhooks"
                }
            }
        },
        "post": {
            "tags": ["Webhooks"],
            "summary": "Subscribe to webhook",
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "url": {"type": "string"},
                                "event": {"type": "string"},
                                "secret": {"type": "string"}
                            }
                        }
                    }
                }
            },
            "responses": {
                "201": {"description": "Webhook created"}
            }
        }
    }


def generate_analytics_paths():
    """Genera paths para analytics"""
    return {
        "get": {
            "tags": ["Analytics"],
            "summary": "Get dashboard analytics",
            "responses": {
                "200": {"description": "Dashboard data"}
            }
        }
    }


# Schemas
def generate_customer_schema():
    return {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Customer ID"},
            "customer_name": {"type": "string"},
            "customer_type": {"type": "string", "enum": ["Company", "Individual"]},
            "customer_group": {"type": "string"},
            "tax_id": {"type": "string", "description": "NIT"},
            "email_id": {"type": "string", "format": "email"},
            "mobile_no": {"type": "string"},
            "phone": {"type": "string"},
            "address": {"type": "string"},
            "city": {"type": "string"},
            "creation": {"type": "string", "format": "date-time"}
        },
        "required": ["customer_name", "customer_type"]
    }


def generate_invoice_schema():
    return {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "customer": {"type": "string"},
            "posting_date": {"type": "string", "format": "date"},
            "due_date": {"type": "string", "format": "date"},
            "total": {"type": "number"},
            "grand_total": {"type": "number"},
            "status": {"type": "string"}
        }
    }


def generate_order_schema():
    return {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "customer": {"type": "string"},
            "total": {"type": "number"},
            "status": {"type": "string"},
            "payment_status": {"type": "string"}
        }
    }


def generate_product_schema():
    return {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "item_name": {"type": "string"},
            "description": {"type": "string"},
            "price": {"type": "number"},
            "stock": {"type": "integer"}
        }
    }


def generate_payment_schema():
    return {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "amount": {"type": "number"},
            "status": {"type": "string"},
            "method": {"type": "string"}
        }
    }


def generate_shipment_schema():
    return {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "order": {"type": "string"},
            "tracking_number": {"type": "string"},
            "status": {"type": "string"},
            "carrier": {"type": "string"}
        }
    }


def generate_error_schema():
    return {
        "type": "object",
        "properties": {
            "error": {"type": "string"},
            "message": {"type": "string"},
            "status_code": {"type": "integer"}
        }
    }


@frappe.whitelist(allow_guest=True)
def get_openapi_spec():
    """
    API endpoint para obtener especificación OpenAPI

    Returns:
        dict: Especificación OpenAPI 3.0
    """
    return generate_openapi_spec()


@frappe.whitelist(allow_guest=True)
def get_swagger_ui():
    """
    Servir interfaz Swagger UI

    Returns:
        HTML: Página Swagger UI
    """
    import frappe.utils
    spec_url = f"{frappe.utils.get_url()}/api/method/nexo_core.integrations.api_gateway.openapi.get_openapi_spec"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Nexo ERP API - Swagger UI</title>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/4.15.5/swagger-ui.min.css">
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/4.15.5/swagger-ui.min.js"></script>
        <script>
            SwaggerUIBundle({{
                url: "{spec_url}",
                dom_id: '#swagger-ui',
                presets: [SwaggerUIBundle.presets.apis, SwaggerUIBundle.SwaggerUIStandalonePreset],
                layout: "BaseLayout"
            }})
        </script>
    </body>
    </html>
    """

    frappe.response['type'] = 'page'
    frappe.response['page_content'] = html

    return html
