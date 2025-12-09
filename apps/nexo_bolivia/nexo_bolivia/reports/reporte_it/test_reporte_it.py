# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

"""Tests para Reporte IT"""

import frappe
import unittest
from datetime import datetime


class TestReporteIT(unittest.TestCase):
    """Suite de tests para Reporte IT"""

    def test_execute_returns_columns_and_data(self):
        """Test: execute() retorna columnas y datos"""
        from nexo_bolivia.reports.reporte_it.reporte_it import execute

        company = frappe.db.get_value('Company', {'disabled': 0}, 'name') or 'Default Company'

        filters = {'company': company}

        columns, data = execute(filters)

        self.assertIsNotNone(columns)
        self.assertIsNotNone(data)
        self.assertIsInstance(data, list)

    def test_columns_required(self):
        """Test: Columnas requeridas están presentes"""
        from nexo_bolivia.reports.reporte_it.reporte_it import get_columns

        columns = get_columns()
        column_names = [col['fieldname'] for col in columns]

        self.assertIn('description', column_names)
        self.assertIn('amount', column_names)

    def test_calculate_it_for_period(self):
        """Test: calculate_it_for_period funciona"""
        from nexo_bolivia.reports.reporte_it.reporte_it import calculate_it_for_period

        company = frappe.db.get_value('Company', {'disabled': 0}, 'name') or 'Default Company'

        result = calculate_it_for_period(company)

        self.assertIn('ingresos_totales', result)
        self.assertIn('base_imponible', result)
        self.assertIn('it_generado', result)
        self.assertIn('saldo_pagar', result)

    def test_it_rate_3_percent(self):
        """Test: IT se calcula al 3%"""
        from nexo_bolivia.reports.reporte_it.reporte_it import IT_RATE

        self.assertEqual(IT_RATE, 3.0)

    def test_it_calculation_correct(self):
        """Test: Cálculo de IT es correcto"""
        from nexo_bolivia.reports.reporte_it.reporte_it import calculate_it_for_period

        company = frappe.db.get_value('Company', {'disabled': 0}, 'name') or 'Default Company'

        result = calculate_it_for_period(company)

        # IT debe ser 3% de base imponible
        expected_it = round(result['base_imponible'] * 0.03, 2)
        self.assertEqual(result['it_generado'], expected_it)


if __name__ == '__main__':
    unittest.main()
