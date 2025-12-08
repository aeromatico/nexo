# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class PlanCuentasBolivia(Document):
    """
    DocType para el Plan de Cuentas Boliviano

    Implementa la estructura contable según normativa boliviana:
    - Estructura jerárquica de 5 niveles
    - Clasificación por tipo (Activo, Pasivo, Patrimonio, Ingreso, Egreso)
    - Validaciones de formato de número de cuenta
    - Sincronización con ERPNext Account
    """

    def validate(self):
        """Validaciones antes de guardar"""
        self.validate_account_number()
        self.validate_hierarchy()
        self.set_root_type()
        self.validate_parent_is_group()

    def validate_account_number(self):
        """
        Valida el formato del número de cuenta boliviano

        Formato esperado:
        - Nivel 1: 1 dígito (1-5)
        - Nivel 2: 2 dígitos (11-53)
        - Nivel 3: 3 dígitos (111-535)
        - Nivel 4: 4 dígitos (1111-5359)
        - Nivel 5: 5+ dígitos
        """
        if not self.account_number:
            frappe.throw(_("El número de cuenta es obligatorio"))

        # Remover espacios
        self.account_number = self.account_number.strip()

        # Validar que sea numérico
        if not self.account_number.isdigit():
            frappe.throw(_("El número de cuenta debe contener solo dígitos"))

        # Validar longitud mínima
        if len(self.account_number) < 1:
            frappe.throw(_("El número de cuenta debe tener al menos 1 dígito"))

        # Validar primer dígito (1-5)
        first_digit = int(self.account_number[0])
        if first_digit not in [1, 2, 3, 4, 5]:
            frappe.throw(_("El primer dígito debe ser 1 (Activo), 2 (Pasivo), 3 (Patrimonio), 4 (Ingreso) o 5 (Egreso)"))

    def validate_hierarchy(self):
        """Valida la jerarquía de cuentas"""
        if self.parent_account:
            parent = frappe.get_doc("Plan Cuentas Bolivia", self.parent_account)

            # Validar que el padre sea grupo
            if not parent.is_group:
                frappe.throw(_("La cuenta padre debe ser una cuenta de grupo"))

            # Validar que el número de cuenta sea consistente con la jerarquía
            if not self.account_number.startswith(parent.account_number):
                frappe.throw(_("El número de cuenta debe comenzar con el número de la cuenta padre: {0}").format(parent.account_number))

    def set_root_type(self):
        """Establece el tipo raíz basado en el primer dígito"""
        if not self.root_type and self.account_number:
            first_digit = self.account_number[0]
            root_types = {
                '1': 'Activo',
                '2': 'Pasivo',
                '3': 'Patrimonio',
                '4': 'Ingreso',
                '5': 'Egreso'
            }
            self.root_type = root_types.get(first_digit, '')

    def validate_parent_is_group(self):
        """Valida que si tiene hijos, debe ser grupo"""
        if not self.is_group:
            # Verificar si ya tiene cuentas hijas
            has_children = frappe.db.exists("Plan Cuentas Bolivia", {
                "parent_account": self.name,
                "name": ["!=", self.name]
            })

            if has_children:
                frappe.throw(_("Esta cuenta tiene cuentas hijas. Debe ser marcada como 'Es Grupo'"))

    def on_update(self):
        """Después de actualizar"""
        # Sincronizar con ERPNext Account si existe
        self.sync_to_erpnext_account()

    def sync_to_erpnext_account(self):
        """
        Sincroniza el plan de cuentas Bolivia con ERPNext Account

        Crea o actualiza la cuenta correspondiente en ERPNext
        """
        if not self.company:
            return

        try:
            # Buscar cuenta ERPNext existente
            erpnext_account_name = f"{self.account_name} - {frappe.get_cached_value('Company', self.company, 'abbr')}"

            if frappe.db.exists("Account", erpnext_account_name):
                # Actualizar cuenta existente
                account = frappe.get_doc("Account", erpnext_account_name)
            else:
                # Crear nueva cuenta
                account = frappe.new_doc("Account")
                account.account_name = self.account_name
                account.company = self.company

            # Mapear campos
            account.account_number = self.account_number
            account.account_type = self.get_erpnext_account_type()
            account.is_group = self.is_group
            account.root_type = self.root_type
            account.account_currency = self.account_currency or "BOB"
            account.disabled = self.disabled

            # Parent account
            if self.parent_account:
                parent = frappe.get_doc("Plan Cuentas Bolivia", self.parent_account)
                parent_abbr = frappe.get_cached_value('Company', self.company, 'abbr')
                account.parent_account = f"{parent.account_name} - {parent_abbr}"

            account.save(ignore_permissions=True)

        except Exception as e:
            frappe.log_error(f"Error sincronizando cuenta {self.name}: {str(e)}", "Plan Cuentas Bolivia - Sync Error")

    def get_erpnext_account_type(self):
        """
        Mapea el tipo de cuenta Bolivia a tipo ERPNext

        Returns:
            str: Tipo de cuenta ERPNext
        """
        type_mapping = {
            'Activo': 'Asset',
            'Pasivo': 'Liability',
            'Patrimonio': 'Equity',
            'Ingreso': 'Income',
            'Egreso': 'Expense',
            'Costo de Ventas': 'Cost of Goods Sold',
            'Gasto Operacional': 'Expense'
        }

        return type_mapping.get(self.account_type, 'Asset')

    def get_balance(self, from_date=None, to_date=None):
        """
        Obtiene el saldo de la cuenta

        Args:
            from_date: Fecha inicio
            to_date: Fecha fin

        Returns:
            dict: Balance información
        """
        if not self.company:
            return {"balance": 0, "debit": 0, "credit": 0}

        # TODO: Implementar cálculo de balance desde GL Entry
        return {"balance": 0, "debit": 0, "credit": 0}

    @staticmethod
    def get_account_tree(company=None, root_type=None):
        """
        Obtiene el árbol de cuentas

        Args:
            company: Filtrar por empresa
            root_type: Filtrar por tipo raíz

        Returns:
            list: Árbol de cuentas
        """
        filters = {}
        if company:
            filters['company'] = company
        if root_type:
            filters['root_type'] = root_type

        accounts = frappe.get_all(
            "Plan Cuentas Bolivia",
            filters=filters,
            fields=["name", "account_number", "account_name", "parent_account", "is_group", "root_type"],
            order_by="account_number asc"
        )

        return build_tree(accounts)


def build_tree(accounts, parent=None):
    """
    Construye árbol jerárquico de cuentas

    Args:
        accounts: Lista de cuentas
        parent: Cuenta padre

    Returns:
        list: Árbol jerárquico
    """
    tree = []
    for account in accounts:
        if account.get('parent_account') == parent:
            children = build_tree(accounts, account['name'])
            if children:
                account['children'] = children
            tree.append(account)
    return tree


@frappe.whitelist()
def get_chart_of_accounts(company=None):
    """
    API para obtener el plan de cuentas

    Args:
        company: Empresa

    Returns:
        dict: Plan de cuentas organizado
    """
    return PlanCuentasBolivia.get_account_tree(company=company)


@frappe.whitelist()
def import_from_erpnext(company):
    """
    Importa cuentas desde ERPNext Account

    Args:
        company: Empresa a importar

    Returns:
        dict: Resultado de la importación
    """
    if not company:
        frappe.throw(_("Debe especificar una empresa"))

    accounts = frappe.get_all(
        "Account",
        filters={"company": company},
        fields=["name", "account_name", "account_number", "account_type", "is_group", "parent_account", "root_type"]
    )

    created = 0
    updated = 0
    errors = []

    for account_data in accounts:
        try:
            if account_data.get('account_number'):
                # Verificar si existe
                if frappe.db.exists("Plan Cuentas Bolivia", account_data['account_number']):
                    doc = frappe.get_doc("Plan Cuentas Bolivia", account_data['account_number'])
                    updated += 1
                else:
                    doc = frappe.new_doc("Plan Cuentas Bolivia")
                    created += 1

                doc.account_number = account_data['account_number']
                doc.account_name = account_data['account_name']
                doc.is_group = account_data['is_group']
                doc.root_type = account_data['root_type']
                doc.company = company

                doc.save(ignore_permissions=True)
        except Exception as e:
            errors.append(f"Error en cuenta {account_data.get('account_name')}: {str(e)}")

    return {
        "success": True,
        "created": created,
        "updated": updated,
        "errors": errors
    }
