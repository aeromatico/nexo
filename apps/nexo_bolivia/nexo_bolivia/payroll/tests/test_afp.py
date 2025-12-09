# Copyright (c) 2024, Aero and Contributors
# See license.txt

"""
Tests para módulo de AFP (afp.py)
"""

import frappe
import unittest
from frappe.tests.utils import FrappeTestCase
from nexo_bolivia.payroll.afp import (
    calculate_afp,
    get_afp_breakdown,
    validate_afp_amount,
    AFP_RATE,
    AFP_COMPONENTS
)


class TestAFPCalculations(FrappeTestCase):
    """Tests para cálculos de AFP"""

    def test_calculate_afp_basic(self):
        """Test cálculo básico de AFP (12.71%)"""
        # AFP de 10,000 × 12.71% = 1,271
        afp = calculate_afp(10000)
        self.assertEqual(afp, 1271.0)

    def test_calculate_afp_smn(self):
        """Test AFP sobre SMN (2,362)"""
        # AFP de 2,362 × 12.71% = 300.34
        afp = calculate_afp(2362)
        expected = 2362 * 0.1271
        self.assertEqual(afp, round(expected, 2))

    def test_calculate_afp_zero(self):
        """Test AFP sobre monto cero"""
        afp = calculate_afp(0)
        self.assertEqual(afp, 0.0)

    def test_calculate_afp_custom_rate(self):
        """Test AFP con tasa personalizada"""
        # AFP de 10,000 × 10% = 1,000
        afp = calculate_afp(10000, rate=10)
        self.assertEqual(afp, 1000.0)

    def test_calculate_afp_high_salary(self):
        """Test AFP con salario alto"""
        afp = calculate_afp(100000)
        expected = 100000 * 0.1271
        self.assertEqual(afp, round(expected, 2))

    def test_afp_rate_constant(self):
        """Test que AFP_RATE sea 12.71%"""
        self.assertEqual(AFP_RATE, 12.71)

    def test_afp_components_sum(self):
        """Test que componentes de AFP sumen 12.71%"""
        total = sum(AFP_COMPONENTS.values())
        self.assertEqual(total, 12.71)

    def test_get_afp_breakdown(self):
        """Test desglose completo de AFP"""
        breakdown = get_afp_breakdown(10000)

        self.assertEqual(breakdown['gross_salary'], 10000.0)
        self.assertEqual(breakdown['labor_solidarity'], 50.0)  # 0.5%
        self.assertEqual(breakdown['commission'], 50.0)  # 0.5%
        self.assertEqual(breakdown['common_risk'], 171.0)  # 1.71%
        self.assertEqual(breakdown['employee_contribution'], 1000.0)  # 10%
        self.assertEqual(breakdown['total_afp'], 1271.0)

    def test_get_afp_breakdown_smn(self):
        """Test desglose AFP sobre SMN"""
        breakdown = get_afp_breakdown(2362)

        self.assertEqual(breakdown['gross_salary'], 2362.0)
        # Verificar suma correcta
        expected_total = (
            2362 * 0.005 +  # labor_solidarity
            2362 * 0.005 +  # commission
            2362 * 0.0171 + # common_risk
            2362 * 0.10     # employee_contribution
        )
        self.assertAlmostEqual(breakdown['total_afp'], round(expected_total, 2), places=1)

    def test_afp_components_labor_solidarity(self):
        """Test componente aporte laboral solidario (0.5%)"""
        breakdown = get_afp_breakdown(1000)
        expected = 1000 * 0.005
        self.assertEqual(breakdown['labor_solidarity'], expected)

    def test_afp_components_commission(self):
        """Test componente comisión (0.5%)"""
        breakdown = get_afp_breakdown(1000)
        expected = 1000 * 0.005
        self.assertEqual(breakdown['commission'], expected)

    def test_afp_components_common_risk(self):
        """Test componente prima riesgo común (1.71%)"""
        breakdown = get_afp_breakdown(1000)
        expected = 1000 * 0.0171
        self.assertEqual(breakdown['common_risk'], round(expected, 2))

    def test_afp_components_employee_contribution(self):
        """Test componente aporte del asegurado (10%)"""
        breakdown = get_afp_breakdown(1000)
        expected = 1000 * 0.10
        self.assertEqual(breakdown['employee_contribution'], expected)

    def test_validate_afp_amount_correct(self):
        """Test validación de AFP correcta"""
        gross = 10000
        afp = calculate_afp(gross)
        valid = validate_afp_amount(afp, gross)
        self.assertTrue(valid)

    def test_validate_afp_amount_incorrect(self):
        """Test validación de AFP incorrecta"""
        gross = 10000
        wrong_afp = 1000  # Debería ser 1271
        valid = validate_afp_amount(wrong_afp, gross)
        self.assertFalse(valid)

    def test_validate_afp_amount_small_difference(self):
        """Test validación con pequeña diferencia por redondeo"""
        gross = 10000
        afp = calculate_afp(gross)
        # Diferencia de 0.01 (dentro de tolerancia)
        afp_with_difference = afp + 0.01
        valid = validate_afp_amount(afp_with_difference, gross)
        self.assertTrue(valid)


class TestAFPValidations(FrappeTestCase):
    """Tests para validaciones de AFP"""

    def test_calculate_afp_negative_salary(self):
        """Test error con salario negativo"""
        with self.assertRaises(Exception):
            calculate_afp(-10000)

    def test_calculate_afp_invalid_rate_too_high(self):
        """Test error con tasa > 100%"""
        with self.assertRaises(Exception):
            calculate_afp(10000, rate=150)

    def test_calculate_afp_invalid_rate_negative(self):
        """Test error con tasa negativa"""
        with self.assertRaises(Exception):
            calculate_afp(10000, rate=-10)

    def test_get_afp_breakdown_negative_salary(self):
        """Test error con salario negativo en desglose"""
        with self.assertRaises(Exception):
            get_afp_breakdown(-10000)


class TestAFPEdgeCases(FrappeTestCase):
    """Tests para casos especiales de AFP"""

    def test_afp_very_high_salary(self):
        """Test AFP con salario muy alto"""
        afp = calculate_afp(1000000)
        expected = 1000000 * 0.1271
        self.assertEqual(afp, round(expected, 2))

    def test_afp_fractional_salary(self):
        """Test AFP con salario fraccionario"""
        afp = calculate_afp(1234.56)
        expected = 1234.56 * 0.1271
        self.assertEqual(afp, round(expected, 2))

    def test_afp_rate_zero(self):
        """Test AFP con tasa 0%"""
        afp = calculate_afp(10000, rate=0)
        self.assertEqual(afp, 0.0)

    def test_afp_rate_one_hundred(self):
        """Test AFP con tasa 100%"""
        afp = calculate_afp(10000, rate=100)
        self.assertEqual(afp, 10000.0)

    def test_afp_breakdown_all_components_positive(self):
        """Test que todos los componentes sean positivos"""
        breakdown = get_afp_breakdown(10000)

        self.assertGreaterEqual(breakdown['labor_solidarity'], 0)
        self.assertGreaterEqual(breakdown['commission'], 0)
        self.assertGreaterEqual(breakdown['common_risk'], 0)
        self.assertGreaterEqual(breakdown['employee_contribution'], 0)
        self.assertGreaterEqual(breakdown['total_afp'], 0)

    def test_afp_different_amounts(self):
        """Test AFP con diferentes montos"""
        amounts = [100, 500, 1000, 5000, 10000]

        for amount in amounts:
            afp = calculate_afp(amount)
            expected = amount * 0.1271
            self.assertEqual(afp, round(expected, 2))

    def test_afp_breakdown_consistency(self):
        """Test que componentes de desglose sumen correctamente"""
        breakdown = get_afp_breakdown(10000)

        total = (
            breakdown['labor_solidarity'] +
            breakdown['commission'] +
            breakdown['common_risk'] +
            breakdown['employee_contribution']
        )

        self.assertAlmostEqual(total, breakdown['total_afp'], places=1)
