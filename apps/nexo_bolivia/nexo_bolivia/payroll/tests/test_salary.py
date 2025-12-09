# Copyright (c) 2024, Aero and Contributors
# See license.txt

"""
Tests para módulo de salarios (salary.py)
"""

import frappe
import unittest
from frappe.tests.utils import FrappeTestCase
from nexo_bolivia.payroll.salary import (
    calculate_base_salary,
    calculate_seniority_bonus,
    calculate_overtime,
    calculate_hourly_rate,
    calculate_daily_rate,
    calculate_total_salary,
    validate_minimum_salary,
    SMN
)


class TestSalaryCalculations(FrappeTestCase):
    """Tests para cálculos salariales básicos"""

    def test_calculate_seniority_bonus_no_years(self):
        """Test bono de antigüedad con 0 años"""
        bonus = calculate_seniority_bonus(0, 2362)
        self.assertEqual(bonus, 0.0)

    def test_calculate_seniority_bonus_2_years(self):
        """Test bono de antigüedad con 2 años"""
        # 2 años × 5% = 10%
        bonus = calculate_seniority_bonus(2, 2362)
        expected = 2362 * 0.10
        self.assertEqual(bonus, round(expected, 2))

    def test_calculate_seniority_bonus_20_years(self):
        """Test bono de antigüedad con 20 años (máximo 100%)"""
        # 20 años × 5% = 100% (máximo)
        bonus = calculate_seniority_bonus(20, 2362)
        self.assertEqual(bonus, 2362.0)  # 100% del salario

    def test_calculate_seniority_bonus_exceeding_max(self):
        """Test bono de antigüedad no puede exceder 100%"""
        # Incluso con 25 años, máximo es 100%
        bonus = calculate_seniority_bonus(25, 2362)
        self.assertEqual(bonus, 2362.0)

    def test_calculate_seniority_bonus_decimal_years(self):
        """Test bono de antigüedad con años decimales"""
        # 2.5 años × 5% = 12.5%
        bonus = calculate_seniority_bonus(2.5, 1000)
        expected = 1000 * 0.125
        self.assertEqual(bonus, round(expected, 2))

    def test_calculate_overtime_normal(self):
        """Test horas extras normales (50% adicional)"""
        # 2 horas a 100 Bs/hora × 1.5
        overtime = calculate_overtime(2, 100, 'normal')
        self.assertEqual(overtime, 300.0)  # 2 × 100 × 1.5

    def test_calculate_overtime_festivo(self):
        """Test horas extras en festivo (100% adicional)"""
        # 2 horas a 100 Bs/hora × 2.0
        overtime = calculate_overtime(2, 100, 'festivo')
        self.assertEqual(overtime, 400.0)  # 2 × 100 × 2.0

    def test_calculate_overtime_nocturno(self):
        """Test horas extras nocturnas (50% adicional)"""
        overtime = calculate_overtime(2, 100, 'nocturno')
        self.assertEqual(overtime, 300.0)

    def test_calculate_overtime_zero_hours(self):
        """Test horas extras con 0 horas"""
        overtime = calculate_overtime(0, 100, 'normal')
        self.assertEqual(overtime, 0.0)

    def test_calculate_hourly_rate(self):
        """Test cálculo de tarifa horaria"""
        # SMN 2362 / 22 días / 8 horas = 13.42 Bs/hora
        rate = calculate_hourly_rate(2362, 22)
        expected = 2362 / (22 * 8)
        self.assertEqual(rate, round(expected, 2))

    def test_calculate_daily_rate(self):
        """Test cálculo de tarifa diaria"""
        # 2362 / 22 = 107.36 Bs/día
        rate = calculate_daily_rate(2362, 22)
        expected = 2362 / 22
        self.assertEqual(rate, round(expected, 2))

    def test_validate_minimum_salary_meets(self):
        """Test validación de SMN que cumple"""
        valid = validate_minimum_salary(2362)
        self.assertTrue(valid)

    def test_validate_minimum_salary_below(self):
        """Test validación de salario menor a SMN"""
        valid = validate_minimum_salary(2000)
        self.assertFalse(valid)

    def test_calculate_total_salary_components(self):
        """Test cálculo de salario total con todos los componentes"""
        result = calculate_total_salary(
            base_salary=2362,
            seniority_bonus=236.2,  # 10%
            overtime_pay=300,
            subsidies=100,
            bonuses=50,
            other_allowances=20
        )

        self.assertEqual(result['base_salary'], 2362.0)
        self.assertEqual(result['seniority_bonus'], 236.2)
        self.assertEqual(result['overtime_pay'], 300.0)
        self.assertEqual(result['gross_salary'], 3068.4)

    def test_calculate_total_salary_base_only(self):
        """Test cálculo de salario solo con base"""
        result = calculate_total_salary(base_salary=2362)

        self.assertEqual(result['base_salary'], 2362.0)
        self.assertEqual(result['seniority_bonus'], 0.0)
        self.assertEqual(result['overtime_pay'], 0.0)
        self.assertEqual(result['gross_salary'], 2362.0)

    def test_calculate_total_salary_with_multiple_components(self):
        """Test suma correcta de múltiples componentes"""
        result = calculate_total_salary(
            base_salary=1000,
            seniority_bonus=100,
            overtime_pay=200,
            subsidies=50,
            bonuses=50
        )

        total = 1000 + 100 + 200 + 50 + 50
        self.assertEqual(result['gross_salary'], float(total))

    def test_smn_constant(self):
        """Test que SMN sea 2362"""
        self.assertEqual(SMN, 2362)


class TestSalaryValidations(FrappeTestCase):
    """Tests para validaciones de salario"""

    def test_overtime_invalid_type(self):
        """Test error al usar tipo de hora extra inválido"""
        with self.assertRaises(Exception):
            calculate_overtime(2, 100, 'invalid_type')

    def test_overtime_negative_hours(self):
        """Test error con horas negativas"""
        with self.assertRaises(Exception):
            calculate_overtime(-1, 100, 'normal')

    def test_overtime_negative_rate(self):
        """Test error con tarifa negativa"""
        with self.assertRaises(Exception):
            calculate_overtime(2, -100, 'normal')

    def test_seniority_bonus_negative_years(self):
        """Test bono de antigüedad con años negativos"""
        bonus = calculate_seniority_bonus(-5, 2362)
        self.assertEqual(bonus, 0.0)

    def test_hourly_rate_invalid_days(self):
        """Test error con días hábiles inválidos"""
        with self.assertRaises(Exception):
            calculate_hourly_rate(2362, 0)

    def test_daily_rate_invalid_days(self):
        """Test error con días hábiles inválidos"""
        with self.assertRaises(Exception):
            calculate_daily_rate(2362, 0)


class TestSalaryEdgeCases(FrappeTestCase):
    """Tests para casos especiales"""

    def test_zero_salary(self):
        """Test salario cero"""
        result = calculate_total_salary(base_salary=0)
        self.assertEqual(result['gross_salary'], 0.0)

    def test_very_high_salary(self):
        """Test salario muy alto"""
        high_salary = 1000000
        bonus = calculate_seniority_bonus(10, high_salary)
        expected = high_salary * 0.5  # 10 años = 50%
        self.assertEqual(bonus, expected)

    def test_fractional_amounts(self):
        """Test con montos fraccionarios"""
        result = calculate_total_salary(
            base_salary=1234.56,
            seniority_bonus=123.45,
            overtime_pay=67.89
        )

        # Debe redondearse correctamente
        total = 1234.56 + 123.45 + 67.89
        self.assertEqual(result['gross_salary'], round(total, 2))

    def test_hourly_rate_different_working_days(self):
        """Test tarifa horaria con diferentes días trabajados"""
        # 22 días (estándar)
        rate_22 = calculate_hourly_rate(2362, 22)

        # 20 días (menos días)
        rate_20 = calculate_hourly_rate(2362, 20)

        # Con 20 días la tarifa es más alta
        self.assertGreater(rate_20, rate_22)
