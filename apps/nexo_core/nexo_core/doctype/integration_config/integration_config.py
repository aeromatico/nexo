# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

import frappe
from frappe import _


class IntegrationConfig(frappe.Document):
    """Configuration for all external integrations"""

    def validate(self):
        """Validación de configuración"""
        pass

    def on_update(self):
        """Al actualizar, limpiar cache"""
        frappe.clear_cache()

    @staticmethod
    def get_config(key):
        """
        Obtiene valor de configuración

        Args:
            key: Nombre de la configuración

        Returns:
            valor de configuración o None
        """
        try:
            config = frappe.get_single('Integration Config')
            return config.get(key)
        except frappe.DoesNotExistError:
            return None
