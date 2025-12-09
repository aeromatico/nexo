# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

"""Tests para Reporte IUE"""

import frappe
import unittest
from datetime import datetime


class TestReporteIUE(unittest.TestCase):
    """Suite de tests para Reporte IUE"""

    def test_execute_returns_columns_and_data(self):
        """Test: execute() retorna columnas y datos"""
        from nexo_bolivia.reports.reporte_iue.reporte_iue import execute

        company = frappe.db.get_value('Company', {'disabled': 0}, 'name') or 'Default Company'

        filters = {'company': company}

        columns, data = execute(filters)

        self.assertIsNotNone(columns)
        self.assertIsNotNone(data)

    def test_columns_required(self):
        """Test: Columnas requeridas están presentes"""
        from nexo_bolivia.reports.reporte_iue.reporte_iue import get_columns

        columns = get_columns()
        column_names = [col['fieldname'] for col in columns]

        self.assertIn('description', column_names)
        self.assertIn('amount', column_names)

    def test_iue_rate_25_percent(self):
        """Test: IUE se calcula al 25%"""
        from nexo_bolivia.reports.reporte_iue.reporte_iue import IUE_RATE

        self.assertEqual(IUE_RATE, 25.0)

    def test_calculate_iue_annual(self):
        """Test: calculate_iue_annual funciona"""
        from nexo_bolivia.reports.reporte_iue.reporte_iue import calculate_iue_annual

        company = frappe.db.get_value('Company', {'disabled': 0}, 'name') or 'Default Company'

        result = calculate_iue_annual(company)

        self.assertIn('utilidad_neta', result)
        self.assertIn('base_imponible', result)
        self.assertIn('iue_calculado', result)

    def test_generate_declaracion_iue(self):
        """Test: generate_declaracion_iue genera Form 500"""
        from nexo_bolivia.reports.reporte_iue.reporte_iue import generate_declaracion_iue

        company = frappe.db.get_value('Company', {'disabled': 0}, 'name') or 'Default Company'

        form_500 = generate_declaracion_iue(company)

        self.assertEqual(form_500['form_type'], 'Form 500')
        self.assertIn('data', form_500)

    def test_iue_calculation_correct(self):
        """Test: Cálculo de IUE es correcto"""
        from nexo_bolivia.reports.reporte_iue.reporte_iue import calculate_iue_annual

        company = frappe.db.get_value('Company', {'disabled': 0}, 'name') or 'Default Company'

        result = calculate_iue_annual(company)

        # IUE debe ser 25% de base imponible
        if result['base_imponible'] > 0:
            expected_iue = round(result['base_imponible'] * 0.25, 2)
            self.assertEqual(result['iue_calculado'], expected_iue)


if __name__ == '__main__':
    unittest.main()
