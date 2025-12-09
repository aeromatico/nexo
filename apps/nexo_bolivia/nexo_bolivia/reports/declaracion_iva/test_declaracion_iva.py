# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

"""Tests para Declaración Jurada IVA"""

import frappe
import unittest
from datetime import datetime


class TestDeclaracionIVA(unittest.TestCase):
    """Suite de tests para Declaración Jurada IVA"""

    def test_execute_returns_columns_and_data(self):
        """Test: execute() retorna Form 200"""
        from nexo_bolivia.reports.declaracion_iva.declaracion_iva import execute

        company = frappe.db.get_value('Company', {'disabled': 0}, 'name') or 'Default Company'
        today = datetime.now()

        filters = {
            'company': company,
            'month': today.month,
            'year': today.year
        }

        columns, data = execute(filters)

        self.assertIsNotNone(columns)
        self.assertIsNotNone(data)

    def test_generate_form_200_structure(self):
        """Test: Form 200 tiene estructura correcta"""
        from nexo_bolivia.reports.declaracion_iva.declaracion_iva import generate_form_200

        company = frappe.db.get_value('Company', {'disabled': 0}, 'name') or 'Default Company'
        today = datetime.now()

        form_200 = generate_form_200(company, today.month, today.year)

        # Validar secciones
        self.assertIn('i_sales', form_200)
        self.assertIn('ii_purchases', form_200)
        self.assertIn('iii_determination', form_200)

    def test_form_200_sales_section(self):
        """Test: Sección de ventas tiene datos correctos"""
        from nexo_bolivia.reports.declaracion_iva.declaracion_iva import generate_form_200

        company = frappe.db.get_value('Company', {'disabled': 0}, 'name') or 'Default Company'
        today = datetime.now()

        form_200 = generate_form_200(company, today.month, today.year)

        sales = form_200['i_sales']
        self.assertIn('total_sales', sales)
        self.assertIn('total_debit_fiscal', sales)

    def test_form_200_purchases_section(self):
        """Test: Sección de compras tiene datos correctos"""
        from nexo_bolivia.reports.declaracion_iva.declaracion_iva import generate_form_200

        company = frappe.db.get_value('Company', {'disabled': 0}, 'name') or 'Default Company'
        today = datetime.now()

        form_200 = generate_form_200(company, today.month, today.year)

        purchases = form_200['ii_purchases']
        self.assertIn('total_purchases', purchases)
        self.assertIn('total_credit_fiscal', purchases)

    def test_form_200_determination_balance(self):
        """Test: Determinación calcula balance correctamente"""
        from nexo_bolivia.reports.declaracion_iva.declaracion_iva import generate_form_200

        company = frappe.db.get_value('Company', {'disabled': 0}, 'name') or 'Default Company'
        today = datetime.now()

        form_200 = generate_form_200(company, today.month, today.year)

        determination = form_200['iii_determination']
        balance = determination['debit_fiscal'] - determination['credit_fiscal']

        self.assertEqual(determination['balance'], balance)

    def test_calculate_iva_declaration_api(self):
        """Test: API calculate_iva_declaration funciona"""
        from nexo_bolivia.reports.declaracion_iva.declaracion_iva import calculate_iva_declaration

        company = frappe.db.get_value('Company', {'disabled': 0}, 'name') or 'Default Company'
        today = datetime.now()

        result = calculate_iva_declaration(company, today.month, today.year)

        self.assertIsNotNone(result)
        self.assertIn('iii_determination', result)

    def test_get_form_200_summary(self):
        """Test: Resumen de Form 200 funciona"""
        from nexo_bolivia.reports.declaracion_iva.declaracion_iva import get_form_200_summary

        company = frappe.db.get_value('Company', {'disabled': 0}, 'name') or 'Default Company'
        today = datetime.now()

        summary = get_form_200_summary(company, today.month, today.year)

        self.assertIn('period', summary)
        self.assertIn('total_to_pay', summary)


if __name__ == '__main__':
    unittest.main()
