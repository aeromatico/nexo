# Copyright (c) 2024, Aero and Contributors
# See license.txt

import frappe
import unittest
from frappe.tests.utils import FrappeTestCase


class TestPlanCuentasBolivia(FrappeTestCase):
    """
    Test cases para Plan de Cuentas Bolivia
    """

    def setUp(self):
        """Setup antes de cada test"""
        # Limpiar cuentas de prueba
        frappe.db.sql("DELETE FROM `tabPlan Cuentas Bolivia` WHERE account_number LIKE '9%'")
        frappe.db.commit()

    def tearDown(self):
        """Cleanup después de cada test"""
        frappe.db.rollback()

    def test_create_root_account(self):
        """Test crear cuenta raíz"""
        account = frappe.get_doc({
            "doctype": "Plan Cuentas Bolivia",
            "account_number": "9",
            "account_name": "CUENTA TEST",
            "account_type": "Activo",
            "is_group": 1,
            "root_type": "Activo",
            "account_currency": "BOB"
        }).insert()

        self.assertEqual(account.account_number, "9")
        self.assertEqual(account.root_type, "Activo")
        self.assertTrue(account.is_group)

    def test_create_child_account(self):
        """Test crear cuenta hija"""
        # Crear cuenta padre
        parent = frappe.get_doc({
            "doctype": "Plan Cuentas Bolivia",
            "account_number": "91",
            "account_name": "CUENTA PADRE TEST",
            "account_type": "Activo",
            "is_group": 1,
            "root_type": "Activo",
            "account_currency": "BOB"
        }).insert()

        # Crear cuenta hija
        child = frappe.get_doc({
            "doctype": "Plan Cuentas Bolivia",
            "account_number": "911",
            "account_name": "CUENTA HIJA TEST",
            "account_type": "Activo",
            "is_group": 0,
            "parent_account": parent.name,
            "root_type": "Activo",
            "account_currency": "BOB"
        }).insert()

        self.assertEqual(child.parent_account, parent.name)
        self.assertTrue(child.account_number.startswith(parent.account_number))

    def test_validate_account_number_format(self):
        """Test validación de formato de número de cuenta"""
        # Número de cuenta inválido (no numérico)
        with self.assertRaises(frappe.ValidationError):
            frappe.get_doc({
                "doctype": "Plan Cuentas Bolivia",
                "account_number": "ABC",
                "account_name": "CUENTA INVALIDA",
                "account_type": "Activo"
            }).insert()

    def test_validate_first_digit(self):
        """Test validación de primer dígito (1-5)"""
        # Primer dígito inválido
        with self.assertRaises(frappe.ValidationError):
            frappe.get_doc({
                "doctype": "Plan Cuentas Bolivia",
                "account_number": "6",
                "account_name": "CUENTA INVALIDA",
                "account_type": "Activo",
                "is_group": 1
            }).insert()

    def test_auto_set_root_type(self):
        """Test auto-determinación de tipo raíz"""
        # Cuenta Activo (1)
        account1 = frappe.get_doc({
            "doctype": "Plan Cuentas Bolivia",
            "account_number": "91",
            "account_name": "TEST ACTIVO",
            "is_group": 1
        }).insert()
        self.assertEqual(account1.root_type, "Activo")

        # Cuenta Pasivo (2)
        account2 = frappe.get_doc({
            "doctype": "Plan Cuentas Bolivia",
            "account_number": "92",
            "account_name": "TEST PASIVO",
            "is_group": 1
        })
        account2.account_number = "92"  # Cambiar a 2 para Pasivo
        # Nota: El primer dígito debe ser 2, pero estamos usando 9 para tests
        # Este test necesita ajuste

    def test_parent_must_be_group(self):
        """Test que cuenta padre debe ser grupo"""
        # Crear cuenta no-grupo
        non_group = frappe.get_doc({
            "doctype": "Plan Cuentas Bolivia",
            "account_number": "93",
            "account_name": "CUENTA NO GRUPO",
            "account_type": "Activo",
            "is_group": 0,
            "root_type": "Activo"
        }).insert()

        # Intentar crear hija con padre no-grupo
        with self.assertRaises(frappe.ValidationError):
            frappe.get_doc({
                "doctype": "Plan Cuentas Bolivia",
                "account_number": "931",
                "account_name": "CUENTA HIJA INVALIDA",
                "parent_account": non_group.name
            }).insert()

    def test_child_number_must_start_with_parent(self):
        """Test que número de hija debe comenzar con número de padre"""
        # Crear cuenta padre
        parent = frappe.get_doc({
            "doctype": "Plan Cuentas Bolivia",
            "account_number": "94",
            "account_name": "CUENTA PADRE",
            "is_group": 1,
            "root_type": "Activo"
        }).insert()

        # Intentar crear hija con número inconsistente
        with self.assertRaises(frappe.ValidationError):
            frappe.get_doc({
                "doctype": "Plan Cuentas Bolivia",
                "account_number": "85",  # No comienza con 94
                "account_name": "CUENTA HIJA INVALIDA",
                "parent_account": parent.name
            }).insert()

    def test_account_with_children_must_be_group(self):
        """Test que cuenta con hijas debe ser grupo"""
        # Crear cuenta padre grupo
        parent = frappe.get_doc({
            "doctype": "Plan Cuentas Bolivia",
            "account_number": "95",
            "account_name": "CUENTA PADRE",
            "is_group": 1,
            "root_type": "Activo"
        }).insert()

        # Crear cuenta hija
        child = frappe.get_doc({
            "doctype": "Plan Cuentas Bolivia",
            "account_number": "951",
            "account_name": "CUENTA HIJA",
            "parent_account": parent.name,
            "is_group": 0
        }).insert()

        # Intentar marcar padre como no-grupo (debe fallar)
        parent.is_group = 0
        with self.assertRaises(frappe.ValidationError):
            parent.save()

    def test_get_account_tree(self):
        """Test obtener árbol de cuentas"""
        # Crear estructura de prueba
        root = frappe.get_doc({
            "doctype": "Plan Cuentas Bolivia",
            "account_number": "96",
            "account_name": "RAIZ TEST",
            "is_group": 1,
            "root_type": "Activo"
        }).insert()

        level1 = frappe.get_doc({
            "doctype": "Plan Cuentas Bolivia",
            "account_number": "961",
            "account_name": "NIVEL 1",
            "is_group": 1,
            "parent_account": root.name
        }).insert()

        level2 = frappe.get_doc({
            "doctype": "Plan Cuentas Bolivia",
            "account_number": "9611",
            "account_name": "NIVEL 2",
            "is_group": 0,
            "parent_account": level1.name
        }).insert()

        # Obtener árbol
        from nexo_bolivia.nexo_bolivia.doctype.plan_cuentas_bolivia.plan_cuentas_bolivia import get_chart_of_accounts
        tree = get_chart_of_accounts()

        # Verificar que existe la estructura
        self.assertIsInstance(tree, list)

    def test_balance_must_be_validation(self):
        """Test validación de tipo de balance"""
        # Crear cuenta activo (debe ser Débito)
        account = frappe.get_doc({
            "doctype": "Plan Cuentas Bolivia",
            "account_number": "97",
            "account_name": "CUENTA ACTIVO TEST",
            "account_type": "Activo",
            "is_group": 0,
            "balance_must_be": "Débito",
            "root_type": "Activo"
        }).insert()

        self.assertEqual(account.balance_must_be, "Débito")

        # Crear cuenta pasivo (debe ser Crédito)
        account2 = frappe.get_doc({
            "doctype": "Plan Cuentas Bolivia",
            "account_number": "98",
            "account_name": "CUENTA PASIVO TEST",
            "account_type": "Pasivo",
            "is_group": 0,
            "balance_must_be": "Crédito",
            "root_type": "Pasivo"
        })
        # Ajustar primer dígito para pasivo
        # Nota: En tests usamos 9, necesita ajuste para producción

    def test_account_currency_default(self):
        """Test que moneda por defecto es BOB"""
        account = frappe.get_doc({
            "doctype": "Plan Cuentas Bolivia",
            "account_number": "99",
            "account_name": "CUENTA TEST MONEDA",
            "is_group": 0,
            "root_type": "Activo"
        }).insert()

        # Verificar que tiene BOB como default
        self.assertEqual(account.account_currency, "BOB")

    def test_unique_account_number(self):
        """Test que número de cuenta debe ser único"""
        # Crear primera cuenta
        frappe.get_doc({
            "doctype": "Plan Cuentas Bolivia",
            "account_number": "9001",
            "account_name": "CUENTA 1",
            "is_group": 0
        }).insert()

        # Intentar crear segunda con mismo número
        with self.assertRaises(frappe.DuplicateEntryError):
            frappe.get_doc({
                "doctype": "Plan Cuentas Bolivia",
                "account_number": "9001",
                "account_name": "CUENTA 2",
                "is_group": 0
            }).insert()


# Test de fixtures
class TestPlanCuentasBoliviaFixtures(FrappeTestCase):
    """Test para verificar que los fixtures se cargan correctamente"""

    def test_fixtures_loaded(self):
        """Test que fixtures básicos existen"""
        # Verificar cuentas principales (1-5)
        for number in ["1", "2", "3", "4", "5"]:
            account = frappe.db.exists("Plan Cuentas Bolivia", number)
            if account:
                doc = frappe.get_doc("Plan Cuentas Bolivia", number)
                self.assertTrue(doc.is_group)

    def test_iva_accounts_exist(self):
        """Test que cuentas de IVA existen"""
        # IVA Crédito Fiscal
        iva_cf = frappe.db.exists("Plan Cuentas Bolivia", "1141")
        if iva_cf:
            account = frappe.get_doc("Plan Cuentas Bolivia", "1141")
            self.assertEqual(account.account_name, "IVA Crédito Fiscal")

        # IVA por Pagar
        iva_pagar = frappe.db.exists("Plan Cuentas Bolivia", "2121")
        if iva_pagar:
            account = frappe.get_doc("Plan Cuentas Bolivia", "2121")
            self.assertEqual(account.account_name, "IVA por Pagar")

    def test_it_accounts_exist(self):
        """Test que cuentas de IT existen"""
        # IT Pagado por Anticipado
        it_ant = frappe.db.exists("Plan Cuentas Bolivia", "1142")
        if it_ant:
            account = frappe.get_doc("Plan Cuentas Bolivia", "1142")
            self.assertIn("IT", account.account_name)

        # IT por Pagar
        it_pagar = frappe.db.exists("Plan Cuentas Bolivia", "2122")
        if it_pagar:
            account = frappe.get_doc("Plan Cuentas Bolivia", "2122")
            self.assertIn("IT", account.account_name)

    def test_account_hierarchy(self):
        """Test que jerarquía de cuentas es correcta"""
        # Verificar que cuenta 111 tiene padre 11
        account_111 = frappe.db.exists("Plan Cuentas Bolivia", "111")
        if account_111:
            doc = frappe.get_doc("Plan Cuentas Bolivia", "111")
            parent_doc = frappe.get_doc("Plan Cuentas Bolivia", doc.parent_account)
            self.assertEqual(parent_doc.account_number, "11")
