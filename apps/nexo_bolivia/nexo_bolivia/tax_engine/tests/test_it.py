# Copyright (c) 2024, Aero and Contributors
# See license.txt

import frappe
import unittest
from frappe.tests.utils import FrappeTestCase
from nexo_bolivia.tax_engine.it import (
    calculate_it,
    calculate_total_with_it,
    IT_RATE
)


class TestIT(FrappeTestCase):
    """Test cases para cálculo de IT"""

    def test_calculate_it(self):
        """Test cálculo básico de IT"""
        # IT del 3% sobre 1000
        it = calculate_it(1000)
        self.assertEqual(it, 30.0)

        # IT del 3% sobre 500
        it = calculate_it(500)
        self.assertEqual(it, 15.0)

    def test_calculate_it_with_custom_rate(self):
        """Test cálculo de IT con tasa personalizada"""
        # IT del 5% sobre 1000
        it = calculate_it(1000, rate=5)
        self.assertEqual(it, 50.0)

    def test_calculate_total_with_it(self):
        """Test cálculo de total con IT incluido"""
        result = calculate_total_with_it(1000)

        self.assertEqual(result['base'], 1000.0)
        self.assertEqual(result['it'], 30.0)
        self.assertEqual(result['total'], 1030.0)
        self.assertEqual(result['rate'], 3.0)

    def test_it_rate_constant(self):
        """Test que la constante IT_RATE sea 3%"""
        self.assertEqual(IT_RATE, 3.0)

    def test_it_rounding(self):
        """Test redondeo de IT"""
        # 3% de 100.5556 = 3.016668, debe redondear a 3.02
        it = calculate_it(100.5556)
        self.assertEqual(it, 3.02)

    def test_it_zero_amount(self):
        """Test IT sobre monto cero"""
        it = calculate_it(0)
        self.assertEqual(it, 0.0)

    def test_it_on_iva_included_amount(self):
        """Test IT se aplica sobre monto con IVA"""
        # Monto base: 1000
        # IVA 13%: 130
        # Total con IVA: 1130
        # IT 3% sobre 1130: 33.90

        from nexo_bolivia.tax_engine.iva import calculate_total_with_iva

        result_iva = calculate_total_with_iva(1000)
        total_with_iva = result_iva['total']

        it = calculate_it(total_with_iva)
        self.assertEqual(it, 33.90)

    def test_multiple_amounts(self):
        """Test IT con múltiples montos"""
        amounts = [100, 500, 1000, 5000, 10000]

        for amount in amounts:
            it = calculate_it(amount)
            expected = amount * 0.03
            self.assertEqual(it, round(expected, 2))


class TestITPeriod(FrappeTestCase):
    """Test cases para cálculo de IT por periodo"""

    def setUp(self):
        """Setup antes de cada test"""
        # Crear empresa de prueba Bolivia
        if not frappe.db.exists('Company', 'Test Company Bolivia IT'):
            company = frappe.get_doc({
                'doctype': 'Company',
                'company_name': 'Test Company Bolivia IT',
                'abbr': 'TCBI',
                'country': 'Bolivia',
                'default_currency': 'BOB'
            }).insert(ignore_permissions=True)

    def tearDown(self):
        """Cleanup después de cada test"""
        frappe.db.rollback()

    def test_calculate_it_for_period(self):
        """Test cálculo de IT para un periodo"""
        from nexo_bolivia.tax_engine.it import calculate_it_for_period
        from datetime import datetime

        today = datetime.today().strftime('%Y-%m-%d')

        result = calculate_it_for_period('Test Company Bolivia IT', today, today)

        self.assertIn('it_sales', result)
        self.assertIn('it_purchases', result)
        self.assertIn('total_it', result)
        self.assertEqual(result['rate'], 3.0)


class TestITCompensation(FrappeTestCase):
    """Test cases para compensación IT con IUE"""

    def test_it_compensable_structure(self):
        """Test estructura de datos de compensación IT"""
        from nexo_bolivia.tax_engine.it import is_it_compensable_with_iue

        # Este test verificará la estructura cuando se implemente
        # Por ahora solo verifica que la función existe
        self.assertTrue(callable(is_it_compensable_with_iue))
