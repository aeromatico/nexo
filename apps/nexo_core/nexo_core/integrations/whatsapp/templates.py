"""
Templates para WhatsApp Business API

Define los templates de mensajes aprobados en WhatsApp
"""

import frappe

# Templates disponibles
WHATSAPP_TEMPLATES = {
    'invoice_notification': {
        'name': 'invoice_notification',
        'description': 'Notificación de factura emitida',
        'language': 'es',
        'category': 'ACCOUNT_UPDATE',
        'parameters': [
            {'name': 'customer_name', 'type': 'text'},
            {'name': 'invoice_number', 'type': 'text'},
            {'name': 'total_amount', 'type': 'text'},
            {'name': 'invoice_date', 'type': 'text'}
        ],
        'template': 'Hola {{1}},\n\nSu factura {{2}} por Bs. {{3}} ha sido emitida.\n\nFecha: {{4}}\n\n¡Gracias por su compra!'
    },
    'order_confirmation': {
        'name': 'order_confirmation',
        'description': 'Confirmación de pedido en línea',
        'language': 'es',
        'category': 'ORDER_UPDATE',
        'parameters': [
            {'name': 'customer_name', 'type': 'text'},
            {'name': 'order_number', 'type': 'text'},
            {'name': 'order_total', 'type': 'text'},
            {'name': 'order_date', 'type': 'text'}
        ],
        'template': 'Hola {{1}},\n\nGracias por tu pedido #{{2}} por Bs. {{3}}.\n\nFecha: {{4}}\n\nTe notificaremos cuando sea enviado.'
    },
    'shipment_notification': {
        'name': 'shipment_notification',
        'description': 'Notificación de envío',
        'language': 'es',
        'category': 'ORDER_UPDATE',
        'parameters': [
            {'name': 'customer_name', 'type': 'text'},
            {'name': 'order_number', 'type': 'text'},
            {'name': 'tracking_number', 'type': 'text'},
            {'name': 'carrier_name', 'type': 'text'}
        ],
        'template': 'Hola {{1}},\n\nTu pedido #{{2}} ha sido enviado.\n\nTracking: {{3}}\nCarrier: {{4}}\n\n¡Rastra tu pedido en línea!'
    },
    'payment_confirmation': {
        'name': 'payment_confirmation',
        'description': 'Confirmación de pago recibido',
        'language': 'es',
        'category': 'ACCOUNT_UPDATE',
        'parameters': [
            {'name': 'customer_name', 'type': 'text'},
            {'name': 'amount', 'type': 'text'},
            {'name': 'payment_date', 'type': 'text'},
            {'name': 'reference', 'type': 'text'}
        ],
        'template': 'Hola {{1}},\n\nConfirmamos la recepción de tu pago de Bs. {{2}}.\n\nFecha: {{3}}\nReferencia: {{4}}\n\n¡Gracias!'
    },
    'support_ticket': {
        'name': 'support_ticket',
        'description': 'Creación de ticket de soporte',
        'language': 'es',
        'category': 'CUSTOMER_CARE',
        'parameters': [
            {'name': 'customer_name', 'type': 'text'},
            {'name': 'ticket_number', 'type': 'text'},
            {'name': 'issue_description', 'type': 'text'},
            {'name': 'support_contact', 'type': 'text'}
        ],
        'template': 'Hola {{1}},\n\nHemos recibido tu solicitud de soporte.\n\nTicket: {{2}}\nAsunto: {{3}}\n\nNos comunicaremos pronto. Contacto: {{4}}'
    },
    'promotion_announcement': {
        'name': 'promotion_announcement',
        'description': 'Anuncio de promoción especial',
        'language': 'es',
        'category': 'MARKETING',
        'parameters': [
            {'name': 'customer_name', 'type': 'text'},
            {'name': 'promotion_title', 'type': 'text'},
            {'name': 'discount_percentage', 'type': 'text'},
            {'name': 'end_date', 'type': 'text'}
        ],
        'template': 'Hola {{1}},\n\n¡Tenemos una sorpresa para ti!\n\n{{2}}\nDescuento: {{3}}%\nVigencia hasta: {{4}}\n\n¡Aprovecha hoy!'
    }
}


def get_template(template_name):
    """
    Obtiene información de un template

    Args:
        template_name: Nombre del template

    Returns:
        dict: Información del template
    """
    return WHATSAPP_TEMPLATES.get(template_name)


def list_templates():
    """
    Lista todos los templates disponibles

    Returns:
        list: Lista de templates
    """
    return list(WHATSAPP_TEMPLATES.values())


@frappe.whitelist()
def get_available_templates():
    """
    API endpoint para obtener templates disponibles

    Returns:
        list: Lista de templates con sus parámetros
    """
    templates = []
    for name, template in WHATSAPP_TEMPLATES.items():
        templates.append({
            'name': template['name'],
            'description': template['description'],
            'parameters': template['parameters'],
            'category': template['category']
        })
    return templates


@frappe.whitelist()
def validate_template_parameters(template_name, parameters):
    """
    Valida que los parámetros coincidan con el template

    Args:
        template_name: Nombre del template
        parameters: Lista de parámetros

    Returns:
        dict: Validación resultado
    """
    template = get_template(template_name)

    if not template:
        return {
            'valid': False,
            'error': f"Template '{template_name}' not found"
        }

    expected_count = len(template['parameters'])
    actual_count = len(parameters) if isinstance(parameters, list) else 0

    if actual_count != expected_count:
        return {
            'valid': False,
            'error': f"Expected {expected_count} parameters, got {actual_count}"
        }

    return {
        'valid': True,
        'message': 'Parameters are valid',
        'template': template['name']
    }


def create_custom_template(name, description, category, parameters, template_text):
    """
    Crea un template personalizado

    Args:
        name: Nombre del template (debe ser lowercase con underscores)
        description: Descripción
        category: Categoría (MARKETING, ACCOUNT_UPDATE, ORDER_UPDATE, CUSTOMER_CARE)
        parameters: Lista de parámetros
        template_text: Texto del template

    Returns:
        dict: Template creado
    """
    if name in WHATSAPP_TEMPLATES:
        frappe.throw(f"Template '{name}' already exists")

    template = {
        'name': name,
        'description': description,
        'language': 'es',
        'category': category,
        'parameters': parameters,
        'template': template_text
    }

    # Guardar en BD para persistencia
    frappe.get_doc({
        'doctype': 'Whatsapp Template',
        'template_name': name,
        'description': description,
        'category': category,
        'template_text': template_text,
        'parameters': str(parameters)
    }).insert()

    WHATSAPP_TEMPLATES[name] = template

    return template
