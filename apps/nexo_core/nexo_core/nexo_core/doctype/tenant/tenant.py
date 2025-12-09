# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document
from frappe import _
from datetime import datetime, timedelta


class Tenant(Document):
    """
    DocType para gestión de Tenants en la plataforma SaaS Nexo ERP

    Funcionalidades:
    - Creación automática de sites Frappe para tenants
    - Gestión de provisioning
    - Control de estados (Trial, Active, Suspended, Cancelled)
    - Seguimiento de métricas de uso
    - Manejo de planes de suscripción
    """

    def validate(self):
        """Validaciones antes de guardar"""
        self.validate_subdomain()
        self.validate_email()
        self.validate_nit()
        self.set_created_at()
        self.validate_subscription_plan()

    def validate_subdomain(self):
        """Valida el formato del subdominio"""
        if not self.subdomain:
            frappe.throw(_("El subdominio es obligatorio"))

        # Remover espacios
        self.subdomain = self.subdomain.strip().lower()

        # Validar caracteres permitidos (solo letras, números y guiones)
        import re
        if not re.match(r'^[a-z0-9-]+$', self.subdomain):
            frappe.throw(_("El subdominio solo puede contener letras minúsculas, números y guiones"))

        # Validar longitud
        if len(self.subdomain) < 3:
            frappe.throw(_("El subdominio debe tener al menos 3 caracteres"))

        if len(self.subdomain) > 63:
            frappe.throw(_("El subdominio no puede exceder 63 caracteres"))

        # Validar que no sea reservado
        reserved = ['admin', 'api', 'www', 'mail', 'ftp', 'smtp', 'nexo', 'erp']
        if self.subdomain in reserved:
            frappe.throw(_("El subdominio '{0}' está reservado").format(self.subdomain))

        # Verificar disponibilidad si es nuevo
        if not self.is_new():
            # Permitir si es la misma cuenta
            existing = frappe.db.get_value("Tenant", {"subdomain": self.subdomain}, "name")
            if existing and existing != self.name:
                frappe.throw(_("El subdominio '{0}' ya está en uso").format(self.subdomain))

    def validate_email(self):
        """Valida el email del administrador"""
        if not self.admin_email:
            frappe.throw(_("El email del administrador es obligatorio"))

        # Validar formato de email
        import re
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', self.admin_email):
            frappe.throw(_("El email del administrador no es válido"))

    def validate_nit(self):
        """Valida el NIT según normas bolivianas"""
        if not self.nit:
            frappe.throw(_("El NIT es obligatorio"))

        # Remover caracteres especiales
        self.nit = self.nit.replace('-', '').replace(' ', '')

        # Validar que sea numérico
        if not self.nit.isdigit():
            frappe.throw(_("El NIT debe contener solo dígitos"))

        # Validar longitud (NIT Bolivia: 13 dígitos)
        if len(self.nit) != 13:
            frappe.throw(_("El NIT debe tener 13 dígitos"))

    def set_created_at(self):
        """Establece la fecha de creación si es nueva"""
        if self.is_new():
            self.created_at = frappe.utils.now()

    def validate_subscription_plan(self):
        """Valida que el plan de suscripción existe"""
        if not self.subscription_plan:
            frappe.throw(_("El plan de suscripción es obligatorio"))

        if not frappe.db.exists("Subscription Plan", self.subscription_plan):
            frappe.throw(_("El plan de suscripción '{0}' no existe").format(self.subscription_plan))

    def before_insert(self):
        """Antes de insertar"""
        # Generar site_name automáticamente
        self.site_name = f"{self.subdomain}.nexo.bo"

        # Si es trial, establecer fecha de fin
        if self.status == "Trial" and not self.trial_end_date:
            self.trial_end_date = frappe.utils.add_days(frappe.utils.today(), 14)

    def after_insert(self):
        """Después de insertar - Disparar provisioning"""
        self.trigger_provisioning()

    def on_update(self):
        """Después de actualizar"""
        # Manejar cambios de estado
        if self.status == "Active" and not self.activated_at:
            self.activated_at = frappe.utils.now()
            self.db_update()

    def trigger_provisioning(self):
        """
        Dispara el provisioning automático del tenant

        Crea un documento en la cola de tareas para provisionar el tenant
        """
        try:
            # Crear tarea asíncrona de provisioning
            frappe.enqueue(
                "nexo_core.provisioning.site_creator.provision_tenant_site",
                tenant_name=self.name,
                queue="default",
                timeout=3600,
                is_async=True
            )
        except Exception as e:
            frappe.log_error(f"Error al disparar provisioning para tenant {self.name}: {str(e)}", "Tenant Provisioning")

    def suspend(self):
        """
        Suspende el tenant

        Detiene acceso pero mantiene los datos
        """
        self.status = "Suspended"
        self.save()

        frappe.msgprint(_("Tenant {0} ha sido suspendido").format(self.name))

    def activate(self):
        """
        Activa el tenant

        Permite acceso completo
        """
        self.status = "Active"
        self.activated_at = frappe.utils.now()
        self.save()

        frappe.msgprint(_("Tenant {0} ha sido activado").format(self.name))

    def cancel_tenant(self):
        """
        Cancela el tenant

        Dispara proceso de eliminación de datos
        """
        self.status = "Cancelled"
        self.save()

        try:
            frappe.enqueue(
                "nexo_core.provisioning.site_creator.cleanup_tenant_site",
                site_name=self.site_name,
                queue="default",
                is_async=True
            )
        except Exception as e:
            frappe.log_error(f"Error al cancelar tenant {self.name}: {str(e)}", "Tenant Cancellation")

        frappe.msgprint(_("Tenant {0} ha sido cancelado").format(self.name))

    def get_usage_metrics(self):
        """
        Obtiene métricas de uso del tenant

        Returns:
            dict: Métricas de uso
        """
        try:
            latest_usage = frappe.get_last_doc(
                "Tenant Usage",
                filters={"tenant": self.name},
                order_by="date desc"
            )

            if latest_usage:
                return {
                    "active_users": latest_usage.active_users,
                    "storage_used_mb": latest_usage.storage_used_mb,
                    "database_size_mb": latest_usage.database_size_mb,
                    "api_calls": latest_usage.api_calls,
                    "date": latest_usage.date
                }
        except Exception:
            pass

        return {
            "active_users": 0,
            "storage_used_mb": 0,
            "database_size_mb": 0,
            "api_calls": 0
        }

    def get_plan_limits(self):
        """
        Obtiene los límites del plan

        Returns:
            dict: Límites del plan
        """
        plan = frappe.get_doc("Subscription Plan", self.subscription_plan)

        return {
            "max_users": plan.max_users,
            "max_storage_gb": plan.max_storage_gb,
            "max_sites": plan.max_sites,
            "features": json.loads(plan.features) if isinstance(plan.features, str) else plan.features
        }

    def check_quota_exceeded(self):
        """
        Verifica si se han excedido los límites de cuota

        Returns:
            dict: Información de cuota
        """
        metrics = self.get_usage_metrics()
        limits = self.get_plan_limits()

        return {
            "users": {
                "used": metrics["active_users"],
                "limit": limits["max_users"],
                "exceeded": metrics["active_users"] > limits["max_users"]
            },
            "storage": {
                "used": metrics["storage_used_mb"],
                "limit": limits["max_storage_gb"] * 1024,
                "exceeded": metrics["storage_used_mb"] > (limits["max_storage_gb"] * 1024)
            }
        }

    @staticmethod
    def get_active_tenants():
        """
        Obtiene todos los tenants activos

        Returns:
            list: Lista de tenants activos
        """
        return frappe.get_all(
            "Tenant",
            filters={"status": ["in", ["Active", "Trial"]]},
            fields=["name", "tenant_name", "status", "subscription_plan"]
        )

    @staticmethod
    def get_tenant_by_subdomain(subdomain):
        """
        Obtiene un tenant por su subdominio

        Args:
            subdomain: Subdominio del tenant

        Returns:
            Document: Documento del tenant o None
        """
        tenant_name = frappe.db.get_value("Tenant", {"subdomain": subdomain}, "name")
        if tenant_name:
            return frappe.get_doc("Tenant", tenant_name)
        return None

    @staticmethod
    def get_trial_expiring_soon():
        """
        Obtiene tenants en trial que están por vencer

        Returns:
            list: Tenants con trial próximo a vencer
        """
        upcoming = frappe.utils.add_days(frappe.utils.today(), 3)

        return frappe.get_all(
            "Tenant",
            filters={
                "status": "Trial",
                "trial_end_date": ["<=", upcoming]
            },
            fields=["name", "tenant_name", "admin_email", "trial_end_date"]
        )
