# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class TenantUsage(Document):
    """
    DocType para métricas de uso de tenants

    Funcionalidades:
    - Recolección de métricas de uso diarias
    - Validación de límites de cuota
    - Alertas cuando se alcanza límites
    - Histórico de uso para análisis
    """

    def validate(self):
        """Validaciones antes de guardar"""
        self.validate_tenant_exists()
        self.validate_metrics()

    def validate_tenant_exists(self):
        """Valida que el tenant existe"""
        if not frappe.db.exists("Tenant", self.tenant):
            frappe.throw(_("El tenant '{0}' no existe").format(self.tenant))

    def validate_metrics(self):
        """Valida que las métricas sean válidas"""
        if self.active_users < 0:
            frappe.throw(_("El número de usuarios activos no puede ser negativo"))

        if self.storage_used_mb < 0:
            frappe.throw(_("El almacenamiento usado no puede ser negativo"))

        if self.database_size_mb < 0:
            frappe.throw(_("El tamaño de la base de datos no puede ser negativo"))

        if self.api_calls < 0:
            frappe.throw(_("El número de llamadas API no puede ser negativo"))

        if self.email_sent < 0:
            frappe.throw(_("El número de emails enviados no puede ser negativo"))

        if self.invoices_generated < 0:
            frappe.throw(_("El número de facturas generadas no puede ser negativo"))

    def after_insert(self):
        """Después de insertar - Verificar límites"""
        self.check_quota_limits()

    def check_quota_limits(self):
        """
        Verifica si se han excedido los límites de cuota del plan

        Envía alertas si es necesario
        """
        tenant = frappe.get_doc("Tenant", self.tenant)
        limits = tenant.get_plan_limits()

        quota_info = {
            "users": {
                "used": self.active_users,
                "limit": limits["max_users"],
                "percentage": (self.active_users / limits["max_users"] * 100) if limits["max_users"] > 0 else 0
            },
            "storage": {
                "used": self.storage_used_mb,
                "limit": limits["max_storage_gb"] * 1024,
                "percentage": (self.storage_used_mb / (limits["max_storage_gb"] * 1024) * 100) if limits["max_storage_gb"] > 0 else 0
            }
        }

        # Verificar si se excedieron límites
        if self.active_users > limits["max_users"]:
            self.send_quota_alert(
                tenant,
                "Límite de Usuarios Excedido",
                f"El tenant {self.tenant} ha excedido el límite de usuarios ({self.active_users}/{limits['max_users']})"
            )

        if self.storage_used_mb > (limits["max_storage_gb"] * 1024):
            self.send_quota_alert(
                tenant,
                "Límite de Almacenamiento Excedido",
                f"El tenant {self.tenant} ha excedido el límite de almacenamiento ({self.storage_used_mb}MB/{limits['max_storage_gb']*1024}MB)"
            )

        # Alertar si está cerca del límite (90%)
        if quota_info["users"]["percentage"] >= 90:
            self.send_quota_alert(
                tenant,
                "Límite de Usuarios Próximo",
                f"El tenant {self.tenant} está usando el {quota_info['users']['percentage']:.0f}% del límite de usuarios"
            )

        if quota_info["storage"]["percentage"] >= 90:
            self.send_quota_alert(
                tenant,
                "Límite de Almacenamiento Próximo",
                f"El tenant {self.tenant} está usando el {quota_info['storage']['percentage']:.0f}% del límite de almacenamiento"
            )

    def send_quota_alert(self, tenant, subject, message):
        """
        Envía una alerta de cuota al administrador del tenant

        Args:
            tenant: Documento del tenant
            subject: Asunto de la alerta
            message: Mensaje de la alerta
        """
        try:
            # Crear documento de log
            frappe.get_doc({
                "doctype": "Tenant Quota Alert",
                "tenant": tenant.name,
                "subject": subject,
                "message": message,
                "severity": "Warning"
            }).insert(ignore_permissions=True)

            # Enviar email al administrador
            frappe.sendmail(
                recipients=[tenant.admin_email],
                subject=f"[Nexo] {subject}",
                message=message
            )
        except Exception as e:
            frappe.log_error(f"Error enviando alerta de cuota para {tenant.name}: {str(e)}", "Tenant Usage Alert")

    @staticmethod
    def collect_metrics():
        """
        Recolecta métricas de todos los tenants activos

        Esta función debe ejecutarse diariamente via scheduler
        """
        active_tenants = frappe.get_all(
            "Tenant",
            filters={"status": ["in", ["Active", "Trial"]]},
            fields=["name"]
        )

        for tenant in active_tenants:
            try:
                TenantUsage.collect_tenant_metrics(tenant["name"])
            except Exception as e:
                frappe.log_error(f"Error recolectando métricas para {tenant['name']}: {str(e)}", "Tenant Usage Collection")

    @staticmethod
    def collect_tenant_metrics(tenant_name):
        """
        Recolecta métricas para un tenant específico

        Args:
            tenant_name: Nombre del tenant
        """
        tenant = frappe.get_doc("Tenant", tenant_name)

        # TODO: Implementar recolección de métricas reales desde el site del tenant
        # Por ahora, creamos un registro con valores por defecto

        usage = frappe.new_doc("Tenant Usage")
        usage.tenant = tenant_name
        usage.date = frappe.utils.today()
        usage.active_users = 0  # TODO: Obtener de site real
        usage.storage_used_mb = 0  # TODO: Calcular del site
        usage.database_size_mb = 0  # TODO: Obtener del site
        usage.api_calls = 0  # TODO: Obtener de logs
        usage.email_sent = 0  # TODO: Contar emails enviados
        usage.invoices_generated = 0  # TODO: Contar facturas

        usage.insert(ignore_permissions=True)

    @staticmethod
    def get_tenant_usage_report(tenant_name, from_date, to_date):
        """
        Obtiene reporte de uso de un tenant en un período

        Args:
            tenant_name: Nombre del tenant
            from_date: Fecha inicio
            to_date: Fecha fin

        Returns:
            dict: Reporte de uso
        """
        usages = frappe.get_all(
            "Tenant Usage",
            filters={
                "tenant": tenant_name,
                "date": ["between", [from_date, to_date]]
            },
            order_by="date asc"
        )

        if not usages:
            return {
                "tenant": tenant_name,
                "period": f"{from_date} to {to_date}",
                "usage_data": [],
                "summary": {}
            }

        # Calcular resumen
        total_storage = sum(u.storage_used_mb for u in usages)
        avg_users = sum(u.active_users for u in usages) / len(usages)
        total_api_calls = sum(u.api_calls for u in usages)
        total_emails = sum(u.email_sent for u in usages)
        total_invoices = sum(u.invoices_generated for u in usages)

        return {
            "tenant": tenant_name,
            "period": f"{from_date} to {to_date}",
            "usage_data": usages,
            "summary": {
                "max_storage_mb": max((u.storage_used_mb for u in usages), default=0),
                "avg_users": avg_users,
                "total_api_calls": total_api_calls,
                "total_emails": total_emails,
                "total_invoices": total_invoices
            }
        }
