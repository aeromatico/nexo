# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document
from frappe import _


class SubscriptionPlan(Document):
    """
    DocType para planes de suscripción de Nexo ERP

    Funcionalidades:
    - Definición de planes con límites de recursos
    - Configuración de precios (mensual/anual)
    - Definición de características por plan
    - Validación de límites
    """

    def validate(self):
        """Validaciones antes de guardar"""
        self.validate_prices()
        self.validate_limits()
        self.validate_features_json()

    def validate_prices(self):
        """Valida los precios"""
        if self.price_monthly < 0:
            frappe.throw(_("El precio mensual no puede ser negativo"))

        if self.price_annual < 0:
            frappe.throw(_("El precio anual no puede ser negativo"))

        if self.price_monthly == 0 and self.price_annual == 0:
            frappe.msgprint(_("Al menos uno de los precios debe ser mayor a 0"))

    def validate_limits(self):
        """Valida los límites de recursos"""
        if self.max_users <= 0:
            frappe.throw(_("El máximo de usuarios debe ser mayor a 0"))

        if self.max_storage_gb <= 0:
            frappe.throw(_("El almacenamiento máximo debe ser mayor a 0"))

        if self.max_sites <= 0:
            frappe.throw(_("El máximo de sitios debe ser mayor a 0"))

    def validate_features_json(self):
        """Valida que el JSON de features sea válido"""
        if self.features:
            try:
                if isinstance(self.features, str):
                    json.loads(self.features)
            except json.JSONDecodeError:
                frappe.throw(_("El formato JSON de características no es válido"))

    def get_features_dict(self):
        """
        Obtiene las características como diccionario

        Returns:
            dict: Características del plan
        """
        if not self.features:
            return {}

        try:
            if isinstance(self.features, str):
                return json.loads(self.features)
            return self.features
        except json.JSONDecodeError:
            return {}

    def set_default_features(self):
        """Establece características por defecto según el plan"""
        default_features = {
            "Basic": {
                "invoicing": True,
                "inventory": False,
                "payroll": False,
                "accounting": True,
                "custom_apps": False
            },
            "Professional": {
                "invoicing": True,
                "inventory": True,
                "payroll": True,
                "accounting": True,
                "custom_apps": False
            },
            "Enterprise": {
                "invoicing": True,
                "inventory": True,
                "payroll": True,
                "accounting": True,
                "custom_apps": True
            }
        }

        if self.plan_name in default_features and not self.features:
            self.features = json.dumps(default_features[self.plan_name])

    def can_create_tenant(self):
        """
        Verifica si el plan permite crear nuevos tenants

        Returns:
            bool: True si el plan está activo y puede crear tenants
        """
        return self.is_active

    @staticmethod
    def get_active_plans():
        """
        Obtiene todos los planes activos

        Returns:
            list: Lista de planes activos
        """
        return frappe.get_all(
            "Subscription Plan",
            filters={"is_active": 1},
            fields=["name", "plan_name", "max_users", "max_storage_gb", "price_monthly", "price_annual"],
            order_by="price_monthly asc"
        )

    @staticmethod
    def get_plan_comparison():
        """
        Obtiene comparativa de todos los planes

        Returns:
            dict: Comparativa de planes
        """
        plans = frappe.get_all(
            "Subscription Plan",
            fields=["name", "plan_name", "max_users", "max_storage_gb", "max_sites", "price_monthly", "price_annual", "features"]
        )

        return {
            "plans": plans,
            "count": len(plans)
        }
