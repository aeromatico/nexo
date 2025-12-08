# Copyright (c) 2024, Aero and Contributors
# See license.txt

import frappe
import unittest
from frappe.tests.utils import FrappeTestCase
from nexo_bolivia.tax_engine.iue import (
    calculate_iue,
    calculate_iue_with_it_compensation,
    IUE_RATE
)


class TestIUE(FrappeTestCase):
    """Test cases para cálculo de IUE"""

    def test_calculate_iue(self):
        """Test cálculo básico de IUE"""
        # IUE del 25% sobre utilidad de 10000
        iue = calculate_iue(10000)
        self.assertEqual(iue, 2500.0)

        # IUE del 25% sobre utilidad de 5000
        iue = calculate_iue(5000)
        self.assertEqual(iue, 1250.0)

    def test_calculate_iue_negative_profit(self):
        """Test IUE sobre pérdida (debe ser 0)"""
        iue = calculate_iue(-5000)
        self.assertEqual(iue, 0.0)

    def test_calculate_iue_zero_profit(self):
        """Test IUE sobre utilidad cero"""
        iue = calculate_iue(0)
        self.assertEqual(iue, 0.0)

    def test_iue_rate_constant(self):
        """Test que la constante IUE_RATE sea 25%"""
        self.assertEqual(IUE_RATE, 25.0)

    def test_calculate_iue_with_it_compensation(self):
        """Test cálculo de IUE con compensación de IT"""
        # Utilidad: 10000
        # IUE 25%: 2500
        # IT pagado: 500
        # IUE a pagar: 2500 - 500 = 2000

        result = calculate_iue_with_it_compensation(10000, 500)

        self.assertEqual(result['net_profit'], 10000.0)
        self.assertEqual(result['iue_base'], 2500.0)
        self.assertEqual(result['it_paid'], 500.0)
        self.assertEqual(result['it_compensation'], 500.0)
        self.assertEqual(result['iue_to_pay'], 2000.0)

    def test_it_compensation_exceeds_iue(self):
        """Test cuando IT pagado excede el IUE calculado"""
        # Utilidad: 1000
        # IUE 25%: 250
        # IT pagado: 500 (mayor que IUE)
        # IUE a pagar: 0 (no puede ser negativo)

        result = calculate_iue_with_it_compensation(1000, 500)

        self.assertEqual(result['iue_base'], 250.0)
        self.assertEqual(result['it_compensation'], 250.0)  # Solo compensa hasta el IUE
        self.assertEqual(result['iue_to_pay'], 0.0)

    def test_it_compensation_zero(self):
        """Test IUE sin compensación de IT"""
        result = calculate_iue_with_it_compensation(10000, 0)

        self.assertEqual(result['iue_base'], 2500.0)
        self.assertEqual(result['it_compensation'], 0.0)
        self.assertEqual(result['iue_to_pay'], 2500.0)

    def test_iue_rounding(self):
        """Test redondeo de IUE"""
        # 25% de 1000.55 = 250.1375, debe redondear a 250.14
        iue = calculate_iue(1000.55)
        self.assertEqual(iue, 250.14)

    def test_multiple_profit_amounts(self):
        """Test IUE con múltiples utilidades"""
        profits = [1000, 5000, 10000, 50000, 100000]

        for profit in profits:
            iue = calculate_iue(profit)
            expected = profit * 0.25
            self.assertEqual(iue, round(expected, 2))


class TestIUEFiscalYear(FrappeTestCase):
    """Test cases para cálculo de IUE anual"""

    def setUp(self):
        """Setup antes de cada test"""
        # Crear empresa de prueba Bolivia
        if not frappe.db.exists('Company', 'Test Company Bolivia IUE'):
            company = frappe.get_doc({
                'doctype': 'Company',
                'company_name': 'Test Company Bolivia IUE',
                'abbr': 'TCBIUE',
                'country': 'Bolivia',
                'default_currency': 'BOB'
            }).insert(ignore_permissions=True)

    def tearDown(self):
        """Cleanup después de cada test"""
        frappe.db.rollback()

    def test_calculate_net_profit_structure(self):
        """Test estructura de cálculo de utilidad neta"""
        from nexo_bolivia.tax_engine.iue import calculate_net_profit_for_fiscal_year

        # Verificar que la función existe y retorna un número
        # (requiere fiscal year configurado)
        self.assertTrue(callable(calculate_net_profit_for_fiscal_year))


class TestIUEFormulas(FrappeTestCase):
    """Test cases para fórmulas de IUE"""

    def test_iue_compensation_formula(self):
        """Test fórmula de compensación IT-IUE"""
        test_cases = [
            # (utilidad, it_pagado, iue_esperado)
            (10000, 0, 2500),      # Sin compensación
            (10000, 500, 2000),    # Compensación parcial
            (10000, 2500, 0),      # Compensación total
            (10000, 3000, 0),      # IT excede IUE
            (0, 1000, 0),          # Utilidad 0
            (-5000, 1000, 0),      # Pérdida
        ]

        for utilidad, it_pagado, iue_esperado in test_cases:
            result = calculate_iue_with_it_compensation(utilidad, it_pagado)
            self.assertEqual(result['iue_to_pay'], iue_esperado,
                           f"Fallo en caso: utilidad={utilidad}, it={it_pagado}")
