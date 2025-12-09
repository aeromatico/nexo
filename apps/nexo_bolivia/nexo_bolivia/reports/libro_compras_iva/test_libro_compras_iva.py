# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

"""Tests para Libro de Compras IVA"""

import frappe
import unittest
from datetime import datetime, timedelta


class TestLibroComprasIVA(unittest.TestCase):
    """Suite de tests para Libro de Compras IVA"""

    def test_execute_returns_columns_and_data(self):
        """Test: execute() retorna columnas y datos"""
        from nexo_bolivia.reports.libro_compras_iva.libro_compras_iva import execute

        today = datetime.now().date()
        from_date = today - timedelta(days=30)
        to_date = today

        company = frappe.db.get_value('Company', {'disabled': 0}, 'name') or 'Default Company'

        filters = {
            'company': company,
            'from_date': str(from_date),
            'to_date': str(to_date)
        }

        columns, data = execute(filters)

        self.assertIsNotNone(columns)
        self.assertIsNotNone(data)
        self.assertIsInstance(columns, list)
        self.assertIsInstance(data, list)

    def test_columns_required(self):
        """Test: Columnas requeridas están presentes"""
        from nexo_bolivia.reports.libro_compras_iva.libro_compras_iva import get_columns

        columns = get_columns()
        column_names = [col['fieldname'] for col in columns]

        required = [
            'nro', 'posting_date', 'name', 'dui', 'supplier_nit',
            'supplier_name', 'total_amount', 'ice_amount',
            'non_credit_amount', 'credit_amount', 'credit_fiscal', 'control_code'
        ]

        for col in required:
            self.assertIn(col, column_names)

    def test_execute_requires_company(self):
        """Test: execute() requiere empresa"""
        from nexo_bolivia.reports.libro_compras_iva.libro_compras_iva import execute

        today = datetime.now().date()
        from_date = today - timedelta(days=30)

        filters = {
            'from_date': str(from_date),
            'to_date': str(today)
        }

        with self.assertRaises(frappe.ValidationError):
            execute(filters)

    def test_calculate_totals_adds_total_row(self):
        """Test: calculate_totals() agrega fila de totales"""
        from nexo_bolivia.reports.libro_compras_iva.libro_compras_iva import calculate_totals

        data = [
            {
                'nro': 1,
                'name': 'PI-001',
                'total_amount': 1000,
                'credit_amount': 1000,
                'credit_fiscal': 130
            }
        ]

        result = calculate_totals(data)

        self.assertGreater(len(result), len(data))
        last_row = result[-1]
        self.assertEqual(last_row['supplier_name'], 'TOTAL DEL PERÍODO')

    def test_calculate_totals_sums_correctly(self):
        """Test: calculate_totals() suma correctamente"""
        from nexo_bolivia.reports.libro_compras_iva.libro_compras_iva import calculate_totals

        data = [
            {
                'nro': 1,
                'name': 'PI-001',
                'total_amount': 1000,
                'credit_amount': 1000,
                'credit_fiscal': 130,
                'ice_amount': 0,
                'non_credit_amount': 0
            },
            {
                'nro': 2,
                'name': 'PI-002',
                'total_amount': 2000,
                'credit_amount': 2000,
                'credit_fiscal': 260,
                'ice_amount': 0,
                'non_credit_amount': 0
            }
        ]

        result = calculate_totals(data)
        totals = result[-1]

        self.assertEqual(totals['total_amount'], 3000)
        self.assertEqual(totals['credit_amount'], 3000)
        self.assertEqual(totals['credit_fiscal'], 390)

    def test_validate_data_with_valid_data(self):
        """Test: validate_data() con datos válidos"""
        from nexo_bolivia.reports.libro_compras_iva.libro_compras_iva import validate_data

        data = [
            {
                'name': 'PI-001',
                'status': 'Válida',
                'supplier_nit': '9876543210',
                'credit_amount': 1000,
                'credit_fiscal': 130
            }
        ]

        result = validate_data(data)
        self.assertTrue(result)

    def test_validate_data_empty_list(self):
        """Test: validate_data() con lista vacía"""
        from nexo_bolivia.reports.libro_compras_iva.libro_compras_iva import validate_data

        result = validate_data([])
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
