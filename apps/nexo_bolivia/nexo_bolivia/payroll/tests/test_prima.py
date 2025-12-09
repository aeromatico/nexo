# Copyright (c) 2024, Aero and Contributors
# See license.txt

"""
Tests para módulo de Prima Anual (prima.py)
"""

import frappe
import unittest
from frappe.tests.utils import FrappeTestCase
from nexo_bolivia.payroll.prima import (
    calculate_prima_anual,
    calculate_proportional_prima,
    get_prima_breakdown,
    is_eligible_for_prima,
    calculate_prima_at_termination
)


class TestPrimaBasic(FrappeTestCase):
    """Tests básicos para prima anual"""

    def test_calculate_prima_one_year(self):
        """Test prima para 1 año completo"""
        # Prima = (12 meses / 12) × 2,362 = 2,362
        prima = calculate_prima_anual('test_emp', 2362, 12)
        self.assertEqual(prima, 2362.0)

    def test_calculate_prima_6_months(self):
        """Test prima para 6 meses"""
        # Prima = (6 / 12) × 2,362 = 1,181
        prima = calculate_prima_anual('test_emp', 2362, 6)
        expected = (6 / 12) * 2362
        self.assertEqual(prima, round(expected, 2))

    def test_calculate_prima_1_month(self):
        """Test prima para 1 mes"""
        # Prima = (1 / 12) × 2,362 = 196.83
        prima = calculate_prima_anual('test_emp', 2362, 1)
        expected = (1 / 12) * 2362
        self.assertEqual(prima, round(expected, 2))

    def test_calculate_prima_zero_months(self):
        """Test prima para 0 meses"""
        prima = calculate_prima_anual('test_emp', 2362, 0)
        self.assertEqual(prima, 0.0)

    def test_calculate_prima_high_salary(self):
        """Test prima con salario alto"""
        # Prima = (12 / 12) × 10,000 = 10,000
        prima = calculate_prima_anual('test_emp', 10000, 12)
        self.assertEqual(prima, 10000.0)

    def test_calculate_prima_2_years(self):
        """Test prima para 2 años"""
        # Prima = (24 meses / 12) × 2,362 = 2 × 2,362 = 4,724
        prima = calculate_prima_anual('test_emp', 2362, 24)
        expected = (24 / 12) * 2362
        self.assertEqual(prima, round(expected, 2))

    def test_calculate_prima_3_months(self):
        """Test prima para 3 meses"""
        prima = calculate_prima_anual('test_emp', 2362, 3)
        expected = (3 / 12) * 2362
        self.assertEqual(prima, round(expected, 2))

    def test_calculate_prima_zero_salary(self):
        """Test prima con salario 0"""
        # No debe permitir salario 0
        with self.assertRaises(Exception):
            calculate_prima_anual('test_emp', 0, 12)


class TestPrimaProportional(FrappeTestCase):
    """Tests para prima prorrateada"""

    def test_calculate_proportional_prima_6_months(self):
        """Test prima proporcional para 6 meses"""
        # Proporcional: (6 / 12) × 2,362 = 1,181
        prop = calculate_proportional_prima('test_emp', 2362, 6)
        expected = (6 / 12) * 2362
        self.assertEqual(prop, round(expected, 2))

    def test_calculate_proportional_prima_3_months(self):
        """Test prima proporcional para 3 meses"""
        prop = calculate_proportional_prima('test_emp', 2362, 3)
        expected = (3 / 12) * 2362
        self.assertEqual(prop, round(expected, 2))


class TestPrimaEligibility(FrappeTestCase):
    """Tests para elegibilidad de prima"""

    def test_is_eligible_for_prima_one_year(self):
        """Test elegibilidad después de 1 año"""
        # Debe ser elegible
        eligible = is_eligible_for_prima('test_emp')
        # Dependiente del documento del empleado, aquí es teórico
        # En tests reales requeriría mock

    def test_is_eligible_for_prima_less_than_one_month(self):
        """Test elegibilidad sin completar 1 mes"""
        # Menos de 1 mes = no elegible
        # Requiere mock del documento


class TestPrimaBreakdown(FrappeTestCase):
    """Tests para desglose de prima"""

    def test_get_prima_breakdown_one_year(self):
        """Test desglose de prima para 1 año"""
        breakdown = get_prima_breakdown('test_emp', 2362, 12)

        self.assertEqual(breakdown['base_salary'], 2362.0)
        self.assertEqual(breakdown['months_worked'], 12.0)
        self.assertEqual(breakdown['complete_years'], 1)
        self.assertEqual(breakdown['remaining_months'], 0.0)
        self.assertEqual(breakdown['total_prima'], 2362.0)

    def test_get_prima_breakdown_6_months(self):
        """Test desglose para 6 meses"""
        breakdown = get_prima_breakdown('test_emp', 2362, 6)

        self.assertEqual(breakdown['months_worked'], 6.0)
        self.assertEqual(breakdown['complete_years'], 0)
        expected = (6 / 12) * 2362
        self.assertEqual(breakdown['total_prima'], round(expected, 2))

    def test_get_prima_breakdown_2_years_6_months(self):
        """Test desglose para 2 años y 6 meses"""
        breakdown = get_prima_breakdown('test_emp', 2362, 30)

        self.assertEqual(breakdown['months_worked'], 30.0)
        self.assertEqual(breakdown['complete_years'], 2)
        self.assertEqual(breakdown['remaining_months'], 6.0)

    def test_get_prima_breakdown_components(self):
        """Test que desglose incluya todos los componentes"""
        breakdown = get_prima_breakdown('test_emp', 2362, 12)

        self.assertIn('employee', breakdown)
        self.assertIn('base_salary', breakdown)
        self.assertIn('months_worked', breakdown)
        self.assertIn('complete_years', breakdown)
        self.assertIn('remaining_months', breakdown)
        self.assertIn('prima_per_year', breakdown)
        self.assertIn('prima_for_complete_years', breakdown)
        self.assertIn('prima_for_remaining_months', breakdown)
        self.assertIn('total_prima', breakdown)

    def test_get_prima_breakdown_prima_per_year(self):
        """Test que prima por año = salario base"""
        breakdown = get_prima_breakdown('test_emp', 2362, 12)

        self.assertEqual(breakdown['prima_per_year'], breakdown['base_salary'])

    def test_get_prima_breakdown_complete_years_calculation(self):
        """Test cálculo de prima para años completos"""
        breakdown = get_prima_breakdown('test_emp', 2362, 30)

        # 2 años completos × 2,362 = 4,724
        expected = 2 * 2362
        self.assertEqual(breakdown['prima_for_complete_years'], round(expected, 2))

    def test_get_prima_breakdown_remaining_months_calculation(self):
        """Test cálculo de prima para meses restantes"""
        breakdown = get_prima_breakdown('test_emp', 2362, 30)

        # 6 meses / 12 × 2,362 = 1,181
        expected = (6 / 12) * 2362
        self.assertEqual(breakdown['prima_for_remaining_months'], round(expected, 2))

    def test_get_prima_breakdown_total_is_sum(self):
        """Test que total sea suma de componentes"""
        breakdown = get_prima_breakdown('test_emp', 2362, 30)

        total = (breakdown['prima_for_complete_years'] +
                 breakdown['prima_for_remaining_months'])
        self.assertEqual(breakdown['total_prima'], total)


class TestPrimaValidations(FrappeTestCase):
    """Tests para validaciones de prima"""

    def test_calculate_prima_negative_months(self):
        """Test error con meses negativos"""
        with self.assertRaises(Exception):
            calculate_prima_anual('test_emp', 2362, -6)

    def test_calculate_prima_negative_salary(self):
        """Test error con salario negativo"""
        with self.assertRaises(Exception):
            calculate_prima_anual('test_emp', -2362, 12)

    def test_get_prima_breakdown_negative_months(self):
        """Test error en desglose con meses negativos"""
        with self.assertRaises(Exception):
            get_prima_breakdown('test_emp', 2362, -1)


class TestPrimaEdgeCases(FrappeTestCase):
    """Tests para casos especiales de prima"""

    def test_prima_high_salary(self):
        """Test prima con salario muy alto"""
        # 1,000,000 × (12 / 12) = 1,000,000
        prima = calculate_prima_anual('test_emp', 1000000, 12)
        self.assertEqual(prima, 1000000.0)

    def test_prima_fractional_salary(self):
        """Test prima con salario fraccionario"""
        # 2,345.67 × (12 / 12) = 2,345.67
        prima = calculate_prima_anual('test_emp', 2345.67, 12)
        self.assertEqual(prima, 2345.67)

    def test_prima_many_years(self):
        """Test prima después de muchos años"""
        # 10 años = 120 meses
        prima = calculate_prima_anual('test_emp', 2362, 120)
        expected = (120 / 12) * 2362
        self.assertEqual(prima, round(expected, 2))

    def test_prima_fraction_of_month(self):
        """Test prima con fracción de mes"""
        # 0.5 meses × 2,362 / 12 = 98.41
        prima = calculate_prima_anual('test_emp', 2362, 0.5)
        expected = (0.5 / 12) * 2362
        self.assertEqual(prima, round(expected, 2))

    def test_prima_different_salaries(self):
        """Test prima con diferentes salarios"""
        salaries = [1000, 2362, 5000, 10000, 50000]

        for salary in salaries:
            prima = calculate_prima_anual('test_emp', salary, 12)
            self.assertEqual(prima, float(salary))

    def test_prima_different_months(self):
        """Test prima con diferentes meses"""
        months = [1, 3, 6, 12, 24, 36, 60]
        salary = 2362

        for months_count in months:
            prima = calculate_prima_anual('test_emp', salary, months_count)
            expected = (months_count / 12) * salary
            self.assertEqual(prima, round(expected, 2))

    def test_prima_breakdown_with_high_salary_multiple_years(self):
        """Test desglose con salario alto y múltiples años"""
        breakdown = get_prima_breakdown('test_emp', 50000, 36)

        self.assertEqual(breakdown['complete_years'], 3)
        self.assertEqual(breakdown['remaining_months'], 0.0)
        expected = 3 * 50000
        self.assertEqual(breakdown['total_prima'], expected)

    def test_prima_salary_minimum(self):
        """Test prima con salario mínimo nacional"""
        smn = 2362
        prima = calculate_prima_anual('test_emp', smn, 12)
        self.assertEqual(prima, smn)
