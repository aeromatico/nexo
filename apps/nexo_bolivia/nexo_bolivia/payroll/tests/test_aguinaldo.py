# Copyright (c) 2024, Aero and Contributors
# See license.txt

"""
Tests para módulo de Aguinaldo (aguinaldo.py)
"""

import frappe
import unittest
from frappe.tests.utils import FrappeTestCase
from nexo_bolivia.payroll.aguinaldo import (
    calculate_aguinaldo,
    calculate_double_aguinaldo,
    is_eligible_for_double_aguinaldo,
    calculate_proportional_aguinaldo,
    get_aguinaldo_payment_dates,
    get_aguinaldo_breakdown,
    PIB_GROWTH_THRESHOLD
)


class TestAguinaldoBasic(FrappeTestCase):
    """Tests básicos para aguinaldo"""

    def test_calculate_aguinaldo_simple_basic(self):
        """Test cálculo simple de aguinaldo (1/12 del total ganado)"""
        # Aguinaldo = 12,000 / 12 = 1,000
        aguinaldo = calculate_aguinaldo('test_emp', 2024, 'simple', 12000)
        self.assertEqual(aguinaldo, 1000.0)

    def test_calculate_aguinaldo_simple_annual(self):
        """Test aguinaldo simple para año completo"""
        # 24,000 ganado en el año / 12 = 2,000
        aguinaldo = calculate_aguinaldo('test_emp', 2024, 'simple', 24000)
        self.assertEqual(aguinaldo, 2000.0)

    def test_calculate_aguinaldo_simple_smn(self):
        """Test aguinaldo simple sobre SMN anual"""
        # SMN 2,362 × 12 = 28,344 / 12 = 2,362
        annual_smn = 2362 * 12
        aguinaldo = calculate_aguinaldo('test_emp', 2024, 'simple', annual_smn)
        self.assertEqual(aguinaldo, 2362.0)

    def test_calculate_aguinaldo_zero_earned(self):
        """Test aguinaldo con cero ganado"""
        aguinaldo = calculate_aguinaldo('test_emp', 2024, 'simple', 0)
        self.assertEqual(aguinaldo, 0.0)

    def test_calculate_aguinaldo_small_amount(self):
        """Test aguinaldo con monto pequeño"""
        # 600 / 12 = 50
        aguinaldo = calculate_aguinaldo('test_emp', 2024, 'simple', 600)
        self.assertEqual(aguinaldo, 50.0)

    def test_calculate_aguinaldo_high_amount(self):
        """Test aguinaldo con monto alto"""
        # 1,200,000 / 12 = 100,000
        aguinaldo = calculate_aguinaldo('test_emp', 2024, 'simple', 1200000)
        self.assertEqual(aguinaldo, 100000.0)


class TestAguinaldoDouble(FrappeTestCase):
    """Tests para aguinaldo doble"""

    def test_is_eligible_for_double_aguinaldo_threshold_met(self):
        """Test elegibilidad cuando PIB cumple threshold"""
        # PIB 4.5% cumple threshold
        eligible = is_eligible_for_double_aguinaldo(4.5)
        self.assertTrue(eligible)

    def test_is_eligible_for_double_aguinaldo_above_threshold(self):
        """Test elegibilidad cuando PIB supera threshold"""
        # PIB 5.2% > 4.5%
        eligible = is_eligible_for_double_aguinaldo(5.2)
        self.assertTrue(eligible)

    def test_is_eligible_for_double_aguinaldo_below_threshold(self):
        """Test elegibilidad cuando PIB no cumple"""
        # PIB 3.0% < 4.5%
        eligible = is_eligible_for_double_aguinaldo(3.0)
        self.assertFalse(eligible)

    def test_is_eligible_for_double_aguinaldo_zero(self):
        """Test elegibilidad con PIB 0%"""
        eligible = is_eligible_for_double_aguinaldo(0.0)
        self.assertFalse(eligible)

    def test_is_eligible_for_double_aguinaldo_negative(self):
        """Test elegibilidad con PIB negativo"""
        eligible = is_eligible_for_double_aguinaldo(-2.0)
        self.assertFalse(eligible)

    def test_calculate_double_aguinaldo_eligible(self):
        """Test cálculo de aguinaldo doble cuando aplica"""
        # PIB 5.0%, total 24,000 / 12 = 2,000 × 2 = 4,000
        double = calculate_double_aguinaldo('test_emp', 2024, 5.0, 24000)
        self.assertEqual(double, 2000.0)  # Monto adicional (otro 1/12)

    def test_calculate_double_aguinaldo_not_eligible(self):
        """Test cálculo de aguinaldo doble cuando no aplica"""
        # PIB 3.0% < 4.5%, no hay doble
        double = calculate_double_aguinaldo('test_emp', 2024, 3.0, 24000)
        self.assertEqual(double, 0.0)

    def test_calculate_double_aguinaldo_zero_total_earned(self):
        """Test doble aguinaldo sin ganancia"""
        double = calculate_double_aguinaldo('test_emp', 2024, 5.0, 0)
        self.assertEqual(double, 0.0)

    def test_pib_growth_threshold(self):
        """Test que threshold PIB sea 4.5%"""
        self.assertEqual(PIB_GROWTH_THRESHOLD, 4.5)


class TestAguinaldoProportional(FrappeTestCase):
    """Tests para aguinaldo prorrateado"""

    def test_calculate_proportional_aguinaldo_6_months(self):
        """Test aguinaldo prorrateado por 6 meses"""
        # Proporcional: (24,000 / 12) × (6 / 12) = 2,000 × 0.5 = 1,000
        prop = calculate_proportional_aguinaldo('test_emp', 2024, 6, 24000)
        expected = (24000 / 12) * (6 / 12)
        self.assertEqual(prop, round(expected, 2))

    def test_calculate_proportional_aguinaldo_1_month(self):
        """Test aguinaldo prorrateado por 1 mes"""
        prop = calculate_proportional_aguinaldo('test_emp', 2024, 1, 12000)
        expected = (12000 / 12) * (1 / 12)
        self.assertEqual(prop, round(expected, 2))

    def test_calculate_proportional_aguinaldo_12_months(self):
        """Test aguinaldo para año completo (sin prorrateo)"""
        prop = calculate_proportional_aguinaldo('test_emp', 2024, 12, 24000)
        expected = 24000 / 12  # Un mes completo
        self.assertEqual(prop, round(expected, 2))

    def test_calculate_proportional_aguinaldo_zero_months(self):
        """Test aguinaldo con cero meses"""
        prop = calculate_proportional_aguinaldo('test_emp', 2024, 0, 24000)
        self.assertEqual(prop, 0.0)

    def test_calculate_proportional_aguinaldo_3_months(self):
        """Test aguinaldo para 3 meses"""
        prop = calculate_proportional_aguinaldo('test_emp', 2024, 3, 12000)
        expected = (12000 / 12) * (3 / 12)
        self.assertEqual(prop, round(expected, 2))


class TestAguinaldoPaymentDates(FrappeTestCase):
    """Tests para fechas de pago de aguinaldo"""

    def test_get_aguinaldo_payment_dates(self):
        """Test obtener fechas de pago"""
        dates = get_aguinaldo_payment_dates(2024)

        self.assertIn('christmas', dates)
        self.assertIn('anniversary', dates)

    def test_aguinaldo_christmas_date(self):
        """Test fecha de aguinaldo de Navidad"""
        dates = get_aguinaldo_payment_dates(2024)

        # Debe ser 21 de Diciembre
        self.assertEqual(str(dates['christmas']), '2024-12-21')

    def test_aguinaldo_anniversary_date(self):
        """Test fecha de aguinaldo de Aniversario"""
        dates = get_aguinaldo_payment_dates(2024)

        # Debe ser 21 de Junio
        self.assertEqual(str(dates['anniversary']), '2024-06-21')

    def test_aguinaldo_payment_dates_different_year(self):
        """Test fechas en año diferente"""
        dates = get_aguinaldo_payment_dates(2025)

        self.assertEqual(str(dates['christmas']), '2025-12-21')
        self.assertEqual(str(dates['anniversary']), '2025-06-21')


class TestAguinaldoBreakdown(FrappeTestCase):
    """Tests para desglose de aguinaldo"""

    def test_get_aguinaldo_breakdown_basic(self):
        """Test desglose básico de aguinaldo"""
        breakdown = get_aguinaldo_breakdown('test_emp', 2024, None, 24000)

        self.assertEqual(breakdown['employee'], 'test_emp')
        self.assertEqual(breakdown['year'], 2024)
        self.assertEqual(breakdown['total_earned'], 24000.0)
        self.assertIn('simple_aguinaldo', breakdown)
        self.assertIn('total_aguinaldo', breakdown)

    def test_get_aguinaldo_breakdown_eligible_for_double(self):
        """Test desglose cuando es elegible para doble"""
        breakdown = get_aguinaldo_breakdown('test_emp', 2024, 5.0, 24000)

        self.assertTrue(breakdown['eligible_for_double'])
        self.assertGreater(breakdown['double_aguinaldo'], 0)

    def test_get_aguinaldo_breakdown_not_eligible_for_double(self):
        """Test desglose cuando no es elegible para doble"""
        breakdown = get_aguinaldo_breakdown('test_emp', 2024, 3.0, 24000)

        self.assertFalse(breakdown['eligible_for_double'])
        self.assertEqual(breakdown['double_aguinaldo'], 0.0)

    def test_get_aguinaldo_breakdown_total(self):
        """Test que total sea suma de componentes"""
        breakdown = get_aguinaldo_breakdown('test_emp', 2024, 5.0, 24000)

        total = breakdown['simple_aguinaldo'] + breakdown['double_aguinaldo']
        self.assertEqual(breakdown['total_aguinaldo'], total)

    def test_get_aguinaldo_breakdown_payment_dates(self):
        """Test que desglose incluya fechas de pago"""
        breakdown = get_aguinaldo_breakdown('test_emp', 2024, None, 24000)

        self.assertIn('christmas_payment_date', breakdown)
        self.assertIn('anniversary_payment_date', breakdown)


class TestAguinaldoValidations(FrappeTestCase):
    """Tests para validaciones de aguinaldo"""

    def test_calculate_aguinaldo_invalid_year_too_old(self):
        """Test error con año muy antiguo"""
        with self.assertRaises(Exception):
            calculate_aguinaldo('test_emp', 1999, 'simple', 12000)

    def test_calculate_aguinaldo_invalid_year_future(self):
        """Test error con año en el futuro"""
        with self.assertRaises(Exception):
            calculate_aguinaldo('test_emp', 2150, 'simple', 12000)

    def test_calculate_proportional_aguinaldo_invalid_months_negative(self):
        """Test error con meses negativos"""
        with self.assertRaises(Exception):
            calculate_proportional_aguinaldo('test_emp', 2024, -1, 12000)

    def test_calculate_proportional_aguinaldo_invalid_months_over_12(self):
        """Test error con más de 12 meses"""
        with self.assertRaises(Exception):
            calculate_proportional_aguinaldo('test_emp', 2024, 13, 12000)


class TestAguinaldoEdgeCases(FrappeTestCase):
    """Tests para casos especiales de aguinaldo"""

    def test_aguinaldo_high_salary(self):
        """Test aguinaldo con salario muy alto"""
        # 1,200,000 / 12 = 100,000
        aguinaldo = calculate_aguinaldo('test_emp', 2024, 'simple', 1200000)
        self.assertEqual(aguinaldo, 100000.0)

    def test_aguinaldo_fractional_amount(self):
        """Test aguinaldo con monto fraccionario"""
        # 12,345.67 / 12 = 1,028.81
        aguinaldo = calculate_aguinaldo('test_emp', 2024, 'simple', 12345.67)
        expected = 12345.67 / 12
        self.assertEqual(aguinaldo, round(expected, 2))

    def test_aguinaldo_pib_exactly_at_threshold(self):
        """Test aguinaldo cuando PIB es exactamente 4.5%"""
        eligible = is_eligible_for_double_aguinaldo(4.5)
        self.assertTrue(eligible)

    def test_aguinaldo_pib_just_below_threshold(self):
        """Test aguinaldo cuando PIB es justo debajo del threshold"""
        eligible = is_eligible_for_double_aguinaldo(4.49)
        self.assertFalse(eligible)
