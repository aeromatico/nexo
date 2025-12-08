"""
Nexo Bolivia - Utility Functions
Funciones utilitarias para Bolivia
"""

import frappe
import re


def format_nit(nit):
    """
    Formatea un NIT boliviano al formato estándar

    Args:
        nit: Número de NIT sin formato

    Returns:
        str: NIT formateado (ej: 1234567890-1)
    """
    if not nit:
        return ""

    # Remover caracteres no numéricos
    nit_clean = re.sub(r"\D", "", str(nit))

    # Formato: XXXXXXXXXX-X (10 dígitos + verificador)
    if len(nit_clean) >= 10:
        return f"{nit_clean[:-1]}-{nit_clean[-1]}"

    return nit_clean


def validate_nit(nit):
    """
    Valida un NIT boliviano

    Args:
        nit: Número de NIT a validar

    Returns:
        bool: True si es válido
    """
    if not nit:
        return False

    nit_clean = re.sub(r"\D", "", str(nit))

    # NIT debe tener al menos 10 dígitos
    if len(nit_clean) < 10:
        return False

    # TODO: Implementar algoritmo de validación de dígito verificador del SIN
    return True


def format_bolivian_currency(amount):
    """
    Formatea una cantidad en bolivianos

    Args:
        amount: Cantidad numérica

    Returns:
        str: Cantidad formateada (ej: Bs 1.234,56)
    """
    if not amount:
        return "Bs 0,00"

    # Formato boliviano: punto para miles, coma para decimales
    formatted = f"{amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    return f"Bs {formatted}"


def get_departamentos():
    """
    Obtiene la lista de departamentos de Bolivia

    Returns:
        list: Lista de departamentos
    """
    return [
        "La Paz",
        "Cochabamba",
        "Santa Cruz",
        "Oruro",
        "Potosí",
        "Chuquisaca",
        "Tarija",
        "Beni",
        "Pando",
    ]


def calculate_iva(amount, rate=13):
    """
    Calcula el IVA boliviano

    Args:
        amount: Monto base
        rate: Tasa de IVA (default: 13%)

    Returns:
        float: Monto del IVA
    """
    return round(amount * (rate / 100), 2)


def calculate_it(amount, rate=3):
    """
    Calcula el IT (Impuesto a las Transacciones)

    Args:
        amount: Monto de la transacción
        rate: Tasa de IT (default: 3%)

    Returns:
        float: Monto del IT
    """
    return round(amount * (rate / 100), 2)


def get_sin_activity_codes():
    """
    Obtiene los códigos de actividad económica del SIN

    Returns:
        dict: Códigos de actividad
    """
    # TODO: Cargar desde la base de datos o API del SIN
    return {
        "620100": "Actividades de programación informática",
        "620200": "Actividades de consultoría de informática",
        "631100": "Procesamiento de datos, hospedaje y actividades conexas",
        # Agregar más códigos según necesidad
    }


def number_to_words_spanish(number):
    """
    Convierte un número a palabras en español (para facturas)

    Args:
        number: Número a convertir

    Returns:
        str: Número en palabras
    """
    # TODO: Implementar conversión completa
    # Por ahora retorna un placeholder
    return f"{number} 00/100 Bolivianos"
