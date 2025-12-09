# Copyright (c) 2024, Aero and Contributors
# See license.txt

"""
Tests para módulo de RC-IVA (rc_iva.py)
"""

import frappe
import unittest
from frappe.tests.utils import FrappeTestCase
from nexo_bolivia.payroll.rc_iva import (
    calculate_rc_iva,
    calculate_rc_iva_rate,
    get_rc_iva_breakdown,
    calculate_rc_iva_monthly,
    get_rc_iva_table,
    RC_IVA_MIN_NO_IMPONIBLE,
    SMN
)


class TestRCIVARate(FrappeTestCase):
    """Tests para tasas de RC-IVA"""

    def test_rc_iva_rate_min_no_imponible(self):
        """Test tasa en mínimo no imponible (0%)"""
        rate = calculate_rc_iva_rate(13000)
        self.assertEqual(rate, 0.0)

    def test_rc_iva_rate_below_min_no_imponible(self):
        """Test tasa por debajo del mínimo (0%)"""
        rate = calculate_rc_iva_rate(12000)
        self.assertEqual(rate, 0.0)

    def test_rc_iva_rate_first_bracket(self):
        """Test tasa en primer bracket (13%)"""
        # 13,001 - 25,000: 13%
        rate = calculate_rc_iva_rate(20000)
        self.assertEqual(rate, 13.0)

    def test_rc_iva_rate_second_bracket(self):
        """Test tasa en segundo bracket (16.5%)"""
        # 25,001 - 50,000: 16.5%
        rate = calculate_rc_iva_rate(40000)
        self.assertEqual(rate, 16.5)

    def test_rc_iva_rate_third_bracket(self):
        """Test tasa en tercer bracket (19.5%)"""
        # 50,001 - 75,000: 19.5%
        rate = calculate_rc_iva_rate(60000)
        self.assertEqual(rate, 19.5)

    def test_rc_iva_rate_fourth_bracket(self):
        """Test tasa en cuarto bracket (22.5%)"""
        # 75,001 - 150,000: 22.5%
        rate = calculate_rc_iva_rate(100000)
        self.assertEqual(rate, 22.5)

    def test_rc_iva_rate_fifth_bracket(self):
        """Test tasa en quinto bracket (27.5%)"""
        # Más de 150,000: 27.5%
        rate = calculate_rc_iva_rate(200000)
        self.assertEqual(rate, 27.5)

    def test_rc_iva_rate_negative_salary(self):
        """Test tasa con salario negativo (0%)"""
        rate = calculate_rc_iva_rate(-10000)
        self.assertEqual(rate, 0.0)


class TestRCIVACalculations(FrappeTestCase):
    """Tests para cálculos de RC-IVA"""

    def test_calculate_rc_iva_below_min(self):
        """Test RC-IVA por debajo del mínimo no imponible (0)"""
        rc_iva = calculate_rc_iva(10000)
        self.assertEqual(rc_iva, 0.0)

    def test_calculate_rc_iva_at_min(self):
        """Test RC-IVA en mínimo no imponible (0)"""
        rc_iva = calculate_rc_iva(13000)
        self.assertEqual(rc_iva, 0.0)

    def test_calculate_rc_iva_first_bracket(self):
        """Test RC-IVA en primer bracket"""
        # 25,000 - (0 dependientes × 4,724) = 25,000
        # Tasa 13% = 3,250
        rc_iva = calculate_rc_iva(25000)
        expected = (25000 - 13000) * 0.13
        self.assertEqual(rc_iva, round(expected, 2))

    def test_calculate_rc_iva_with_dependents(self):
        """Test RC-IVA con deducción por dependientes"""
        # 25,000 - (1 × 2 × 2,362) = 25,000 - 4,724 = 20,276
        # Tasa 13% = 2,635.88
        rc_iva = calculate_rc_iva(25000, dependents=1)
        deduction = 2 * SMN
        base = 25000 - deduction
        expected = base * 0.13
        self.assertEqual(rc_iva, round(expected, 2))

    def test_calculate_rc_iva_with_multiple_dependents(self):
        """Test RC-IVA con múltiples dependientes"""
        # 25,000 - (2 × 2 × 2,362) = 25,000 - 9,448 = 15,552
        # Tasa 13% = 2,021.76
        rc_iva = calculate_rc_iva(25000, dependents=2)
        deduction = 2 * SMN * 2
        base = max(0, 25000 - deduction)
        expected = max(0, base) * 0.13
        self.assertEqual(rc_iva, round(expected, 2))

    def test_calculate_rc_iva_high_salary(self):
        """Test RC-IVA con salario alto"""
        # 200,000 - 0 = 200,000
        # Tasa 27.5% = 55,000
        rc_iva = calculate_rc_iva(200000)
        expected = 200000 * 0.275
        self.assertEqual(rc_iva, round(expected, 2))

    def test_calculate_rc_iva_zero_salary(self):
        """Test RC-IVA con salario cero"""
        rc_iva = calculate_rc_iva(0)
        self.assertEqual(rc_iva, 0.0)

    def test_calculate_rc_iva_small_salary(self):
        """Test RC-IVA con salario muy bajo"""
        rc_iva = calculate_rc_iva(5000)
        self.assertEqual(rc_iva, 0.0)  # Menor a mínimo no imponible


class TestRCIVAMonthly(FrappeTestCase):
    """Tests para cálculos mensuales de RC-IVA"""

    def test_calculate_rc_iva_monthly_basic(self):
        """Test cálculo mensual de RC-IVA"""
        monthly = calculate_rc_iva_monthly(25000, dependents=0, month=12)

        annual_rc_iva = calculate_rc_iva(25000, dependents=0)
        expected_monthly = annual_rc_iva / 12

        self.assertEqual(monthly['monthly_rc_iva'], round(expected_monthly, 2))

    def test_calculate_rc_iva_monthly_accumulated(self):
        """Test RC-IVA acumulada en mes específico"""
        monthly = calculate_rc_iva_monthly(25000, dependents=0, month=6)

        annual_rc_iva = calculate_rc_iva(25000, dependents=0)
        monthly_rc_iva = annual_rc_iva / 12
        expected_accumulated = monthly_rc_iva * 6

        self.assertEqual(monthly['accumulated_rc_iva'], round(expected_accumulated, 2))

    def test_calculate_rc_iva_monthly_month_1(self):
        """Test RC-IVA en mes 1"""
        monthly = calculate_rc_iva_monthly(25000, dependents=0, month=1)

        annual_rc_iva = calculate_rc_iva(25000, dependents=0)
        monthly_rc_iva = annual_rc_iva / 12

        self.assertEqual(monthly['accumulated_rc_iva'], round(monthly_rc_iva, 2))

    def test_calculate_rc_iva_monthly_month_12(self):
        """Test RC-IVA en mes 12 (año completo)"""
        monthly = calculate_rc_iva_monthly(25000, dependents=0, month=12)

        annual_rc_iva = calculate_rc_iva(25000, dependents=0)

        self.assertEqual(monthly['accumulated_rc_iva'], round(annual_rc_iva, 2))


class TestRCIVABreakdown(FrappeTestCase):
    """Tests para desglose de RC-IVA"""

    def test_get_rc_iva_breakdown_basic(self):
        """Test desglose básico de RC-IVA"""
        breakdown = get_rc_iva_breakdown(25000, dependents=0)

        self.assertEqual(breakdown['annual_salary'], 25000.0)
        self.assertEqual(breakdown['dependents'], 0)
        self.assertEqual(breakdown['taxable_base'], 25000.0)
        self.assertIn('rc_iva', breakdown)
        self.assertIn('net_salary', breakdown)

    def test_get_rc_iva_breakdown_with_dependents(self):
        """Test desglose con dependientes"""
        breakdown = get_rc_iva_breakdown(25000, dependents=1)

        deduction = 2 * SMN
        expected_base = 25000 - deduction

        self.assertEqual(breakdown['total_deduction'], round(deduction, 2))
        self.assertEqual(breakdown['taxable_base'], round(expected_base, 2))

    def test_get_rc_iva_breakdown_net_salary(self):
        """Test salario neto en desglose"""
        breakdown = get_rc_iva_breakdown(25000, dependents=0)

        expected_net = 25000 - breakdown['rc_iva']

        self.assertEqual(breakdown['net_salary'], round(expected_net, 2))

    def test_get_rc_iva_breakdown_effective_rate(self):
        """Test tasa efectiva en desglose"""
        breakdown = get_rc_iva_breakdown(50000, dependents=0)

        effective_rate = (breakdown['rc_iva'] / breakdown['annual_salary']) * 100

        self.assertEqual(breakdown['effective_rate'], round(effective_rate, 2))


class TestRCIVATable(FrappeTestCase):
    """Tests para tablas de RC-IVA"""

    def test_get_rc_iva_table(self):
        """Test obtener tabla de RC-IVA"""
        table = get_rc_iva_table(2024)

        self.assertIsInstance(table, list)
        self.assertGreater(len(table), 0)
        # Debe tener al menos 6 brackets
        self.assertGreaterEqual(len(table), 6)

    def test_rc_iva_min_no_imponible_constant(self):
        """Test que mínimo no imponible sea 13,000"""
        self.assertEqual(RC_IVA_MIN_NO_IMPONIBLE, 13000)

    def test_smn_constant(self):
        """Test que SMN sea 2,362"""
        self.assertEqual(SMN, 2362)


class TestRCIVAValidations(FrappeTestCase):
    """Tests para validaciones de RC-IVA"""

    def test_calculate_rc_iva_negative_salary(self):
        """Test error con salario negativo"""
        with self.assertRaises(Exception):
            calculate_rc_iva(-25000)

    def test_calculate_rc_iva_negative_dependents(self):
        """Test error con dependientes negativos"""
        with self.assertRaises(Exception):
            calculate_rc_iva(25000, dependents=-1)

    def test_get_rc_iva_breakdown_negative_salary(self):
        """Test error en desglose con salario negativo"""
        with self.assertRaises(Exception):
            get_rc_iva_breakdown(-25000)


class TestRCIVAEdgeCases(FrappeTestCase):
    """Tests para casos especiales de RC-IVA"""

    def test_rc_iva_high_salary_high_dependents(self):
        """Test RC-IVA con salario alto y muchos dependientes"""
        # 150,000 - (5 × 4,724) = 150,000 - 23,620 = 126,380
        # Tasa 22.5% = 28,435.50
        rc_iva = calculate_rc_iva(150000, dependents=5)
        deduction = 2 * SMN * 5
        base = 150000 - deduction
        expected = base * 0.225
        self.assertEqual(rc_iva, round(expected, 2))

    def test_rc_iva_dependents_exceed_deduction(self):
        """Test cuando deducción por dependientes es mayor al salario"""
        # 10,000 - (5 × 4,724) = 10,000 - 23,620 = -13,620
        # Debe retornar 0 (no negativo)
        rc_iva = calculate_rc_iva(10000, dependents=5)
        self.assertEqual(rc_iva, 0.0)

    def test_rc_iva_fractional_salary(self):
        """Test RC-IVA con salario fraccionario"""
        rc_iva = calculate_rc_iva(25555.55, dependents=0)
        expected_base = 25555.55 - 13000
        expected = expected_base * 0.13
        self.assertEqual(rc_iva, round(expected, 2))

    def test_rc_iva_different_salaries(self):
        """Test RC-IVA con diferentes salarios"""
        salaries = [15000, 30000, 60000, 90000, 150000, 200000]

        for salary in salaries:
            rc_iva = calculate_rc_iva(salary)
            # RC-IVA debe ser >= 0
            self.assertGreaterEqual(rc_iva, 0)
