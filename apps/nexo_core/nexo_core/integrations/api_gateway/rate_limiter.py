"""
Rate Limiting para APIs

Controla el número de solicitudes por cliente/usuario
"""

import frappe
from frappe import _
import time
from functools import wraps


class RateLimiter:
    """Gestor de rate limiting"""

    def __init__(self, max_requests=100, window_seconds=60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    def is_allowed(self, key):
        """
        Verifica si la solicitud está permitida

        Args:
            key: Identificador único del cliente (API key, IP, etc)

        Returns:
            tuple: (allowed: bool, info: dict)
        """
        cache_key = f"rate_limit:{key}"

        # Obtener contador actual del cache
        current = frappe.cache().get(cache_key)

        if not current:
            current = {
                'count': 0,
                'reset_at': time.time() + self.window_seconds
            }

        # Verificar si window expiró
        if time.time() > current['reset_at']:
            current = {
                'count': 0,
                'reset_at': time.time() + self.window_seconds
            }

        # Incrementar contador
        current['count'] += 1
        frappe.cache().set(cache_key, current, expires_in_sec=self.window_seconds)

        # Verificar si excedió límite
        if current['count'] > self.max_requests:
            return False, {
                'retry_after': int(current['reset_at'] - time.time()),
                'limit': self.max_requests,
                'remaining': 0
            }

        return True, {
            'remaining': self.max_requests - current['count'],
            'reset_at': int(current['reset_at']),
            'limit': self.max_requests
        }


def get_client_identifier():
    """
    Obtiene identificador único del cliente

    Prioridad:
    1. API Key en header X-API-Key
    2. JWT token del usuario
    3. Dirección IP del cliente

    Returns:
        str: Identificador del cliente
    """
    # Intentar obtener API Key
    api_key = frappe.get_request_header('X-API-Key')
    if api_key:
        return f"api_key:{api_key[:20]}"

    # Intentar obtener usuario autenticado
    if frappe.session and frappe.session.user and frappe.session.user != 'Guest':
        return f"user:{frappe.session.user}"

    # Usar dirección IP
    return f"ip:{frappe.local.request_ip}"


def rate_limit(max_requests=100, window_seconds=60):
    """
    Decorator para aplicar rate limiting a una función

    Args:
        max_requests: Máximo número de requests en el window
        window_seconds: Duración del window en segundos

    Example:
        @frappe.whitelist()
        @rate_limit(max_requests=1000, window_seconds=3600)
        def get_data():
            return {"data": []}
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            client_id = get_client_identifier()
            limiter = RateLimiter(max_requests, window_seconds)
            allowed, info = limiter.is_allowed(client_id)

            # Agregar headers de rate limit a respuesta
            frappe.response['X-RateLimit-Limit'] = str(max_requests)
            frappe.response['X-RateLimit-Remaining'] = str(info['remaining'])
            frappe.response['X-RateLimit-Reset'] = str(info['reset_at'])

            if not allowed:
                frappe.response.status_code = 429
                frappe.response['Retry-After'] = str(info['retry_after'])

                frappe.throw(
                    _("Rate limit exceeded. Retry after {0} seconds").format(info['retry_after']),
                    frappe.ToManyRequestsError
                )

            return fn(*args, **kwargs)

        return wrapper
    return decorator


class APIKeyManager:
    """Gestor de API Keys para clientes"""

    @staticmethod
    def create_api_key(user, description=None, rate_limit=1000):
        """
        Crea nueva API key para usuario

        Args:
            user: Usuario del sistema
            description: Descripción de la key
            rate_limit: Límite de requests/hora

        Returns:
            str: API Key generada
        """
        import secrets
        import hashlib

        api_key = secrets.token_urlsafe(32)
        api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()

        frappe.get_doc({
            'doctype': 'API Key',
            'api_key': api_key_hash,
            'user': user,
            'description': description,
            'rate_limit': rate_limit,
            'enabled': 1
        }).insert()

        frappe.db.commit()

        return api_key

    @staticmethod
    def validate_api_key(api_key):
        """
        Valida una API key

        Args:
            api_key: Key a validar

        Returns:
            dict: Información de la key o None
        """
        import hashlib

        api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()

        key_doc = frappe.db.get_value(
            'API Key',
            filters={'api_key': api_key_hash, 'enabled': 1},
            fieldname=['user', 'rate_limit', 'last_used']
        )

        if key_doc:
            user, rate_limit, last_used = key_doc
            return {
                'user': user,
                'rate_limit': rate_limit,
                'last_used': last_used
            }

        return None

    @staticmethod
    def revoke_api_key(api_key):
        """
        Revoca una API key

        Args:
            api_key: Key a revocar

        Returns:
            bool: True si fue revocada
        """
        import hashlib

        api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()

        frappe.db.set_value('API Key', api_key_hash, 'enabled', 0)
        frappe.db.commit()

        return True


@frappe.whitelist()
def create_api_key_for_user(description=None, rate_limit=1000):
    """
    API endpoint: Crea API key para usuario actual

    Args:
        description: Descripción de la key
        rate_limit: Límite de requests/hora

    Returns:
        dict: API key generada
    """
    try:
        user = frappe.session.user

        if user == 'Guest':
            frappe.throw(_("You must be logged in to create an API key"))

        api_key = APIKeyManager.create_api_key(user, description, rate_limit)

        return {
            'success': True,
            'api_key': api_key,
            'message': 'API Key created successfully. Keep it safe!'
        }
    except Exception as e:
        frappe.log_error(str(e), "API Key Creation Error")
        return {'success': False, 'error': str(e)}


@frappe.whitelist()
def list_my_api_keys():
    """
    API endpoint: Lista API keys del usuario actual

    Returns:
        list: API keys del usuario
    """
    try:
        user = frappe.session.user

        if user == 'Guest':
            return []

        keys = frappe.get_all('API Key',
                              filters={'user': user},
                              fields=['name', 'description', 'rate_limit', 'enabled', 'creation'])

        return keys
    except Exception as e:
        frappe.log_error(str(e), "List API Keys Error")
        return []


@frappe.whitelist()
def revoke_api_key(api_key_id):
    """
    API endpoint: Revoca una API key

    Args:
        api_key_id: ID de la key

    Returns:
        dict: Resultado
    """
    try:
        user = frappe.session.user

        # Verificar que la key pertenece al usuario
        key_doc = frappe.get_doc('API Key', api_key_id)

        if key_doc.user != user:
            frappe.throw(_("You can only revoke your own API keys"))

        key_doc.enabled = 0
        key_doc.save()
        frappe.db.commit()

        return {'success': True, 'message': 'API Key revoked'}
    except Exception as e:
        frappe.log_error(str(e), "Revoke API Key Error")
        return {'success': False, 'error': str(e)}
