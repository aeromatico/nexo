# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

"""Tests para Reporte RC-IVA"""

import frappe
import unittest
from datetime import datetime, timedelta


class TestReporteRCIVA(unittest.TestCase):
    """Suite de tests para Reporte RC-IVA"""

    def test_execute_returns_columns_and_data(self):
        """Test: execute() retorna columnas y datos"""
        from nexo_bolivia.reports.reporte_rc_iva.reporte_rc_iva import execute

        company = frappe.db.get_value('Company', {'disabled': 0}, 'name') or 'Default Company'
        today = datetime.now().date()
        from_date = today - timedelta(days=30)

        filters = {
            'company': company,
            'from_date': str(from_date),
            'to_date': str(today)
        }

        columns, data = execute(filters)

        self.assertIsNotNone(columns)
        self.assertIsNotNone(data)

    def test_columns_required(self):
        """Test: Columnas requeridas están presentes"""
        from nexo_bolivia.reports.reporte_rc_iva.reporte_rc_iva import get_columns

        columns = get_columns()
        column_names = [col['fieldname'] for col in columns]

        required = [
            'employee', 'employee_name', 'posting_date', 'salary',
            'other_income', 'dependents', 'deduction', 'taxable_base',
            'rc_iva_rate', 'rc_iva_amount'
        ]

        for col in required:
            self.assertIn(col, column_names)

    def test_get_rc_iva_rate(self):
        """Test: get_rc_iva_rate retorna tasa correcta"""
        from nexo_bolivia.reports.reporte_rc_iva.reporte_rc_iva import get_rc_iva_rate

        # Salario bajo
        rate = get_rc_iva_rate(2000)
        self.assertEqual(rate, 0.0)

        # Salario medio
        rate = get_rc_iva_rate(5500)
        self.assertEqual(rate, 1.0)

        # Salario alto
        rate = get_rc_iva_rate(15000)
        self.assertEqual(rate, 2.0)


if __name__ == '__main__':
    unittest.main()
