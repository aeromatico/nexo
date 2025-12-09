# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class TenantApp(Document):
    """
    DocType Child para registrar las apps instaladas en un tenant
    """

    def validate(self):
        """Validaciones antes de guardar"""
        self.validate_app_name()

    def validate_app_name(self):
        """Valida que el nombre de la app no esté vacío"""
        if not self.app_name:
            frappe.throw(_("El nombre de la app es obligatorio"))

        self.app_name = self.app_name.strip()
