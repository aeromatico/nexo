# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

"""Tests para Compliance Checker"""

import frappe
import unittest
from datetime import datetime


class TestComplianceChecker(unittest.TestCase):
    """Suite de tests para Compliance Checker"""

    def test_check_iva_compliance(self):
        """Test: check_iva_compliance funciona"""
        from nexo_bolivia.reports.audit.compliance_checker import check_iva_compliance

        company = frappe.db.get_value('Company', {'disabled': 0}, 'name') or 'Default Company'
        today = datetime.now()

        result = check_iva_compliance(company, today.month, today.year)

        self.assertIn('category', result)
        self.assertEqual(result['category'], 'IVA')
        self.assertIn('status', result)
        self.assertIn('issues', result)

    def test_check_payroll_compliance(self):
        """Test: check_payroll_compliance funciona"""
        from nexo_bolivia.reports.audit.compliance_checker import check_payroll_compliance

        company = frappe.db.get_value('Company', {'disabled': 0}, 'name') or 'Default Company'
        today = datetime.now()

        result = check_payroll_compliance(company, today.month, today.year)

        self.assertIn('category', result)
        self.assertEqual(result['category'], 'Nómina')
        self.assertIn('status', result)

    def test_check_sin_compliance(self):
        """Test: check_sin_compliance funciona"""
        from nexo_bolivia.reports.audit.compliance_checker import check_sin_compliance

        company = frappe.db.get_value('Company', {'disabled': 0}, 'name') or 'Default Company'
        today = datetime.now()

        result = check_sin_compliance(company, today.month, today.year)

        self.assertIn('category', result)
        self.assertEqual(result['category'], 'SIN')
        self.assertIn('status', result)

    def test_generate_compliance_report(self):
        """Test: generate_compliance_report genera reporte completo"""
        from nexo_bolivia.reports.audit.compliance_checker import generate_compliance_report

        company = frappe.db.get_value('Company', {'disabled': 0}, 'name') or 'Default Company'
        today = datetime.now()
        period = f'{today.month:02d}/{today.year}'

        result = generate_compliance_report(company, period)

        self.assertIn('company', result)
        self.assertIn('overall_status', result)
        self.assertIn('total_issues', result)
        self.assertIn('checks', result)
        self.assertIn('recommendations', result)

    def test_compliance_report_structure(self):
        """Test: Reporte de compliance tiene estructura correcta"""
        from nexo_bolivia.reports.audit.compliance_checker import generate_compliance_report

        company = frappe.db.get_value('Company', {'disabled': 0}, 'name') or 'Default Company'
        today = datetime.now()
        period = f'{today.month:02d}/{today.year}'

        result = generate_compliance_report(company, period)

        # Verificar secciones
        self.assertIn('iva', result['checks'])
        self.assertIn('payroll', result['checks'])
        self.assertIn('sin', result['checks'])

    def test_get_compliance_summary(self):
        """Test: get_compliance_summary genera resumen"""
        from nexo_bolivia.reports.audit.compliance_checker import get_compliance_summary

        company = frappe.db.get_value('Company', {'disabled': 0}, 'name') or 'Default Company'
        today = datetime.now()
        period = f'{today.month:02d}/{today.year}'

        result = get_compliance_summary(company, period)

        self.assertIn('company', result)
        self.assertIn('period', result)
        self.assertIn('status', result)
        self.assertIn('is_compliant', result)


if __name__ == '__main__':
    unittest.main()
