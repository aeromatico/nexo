# Copyright (c) 2024, Aero and Contributors
# See license.txt

import frappe
import unittest
from frappe.tests.utils import FrappeTestCase
from nexo_bolivia.tax_engine.iva import (
    calculate_iva,
    calculate_total_with_iva,
    extract_iva_from_total,
    IVA_RATE
)


class TestIVA(FrappeTestCase):
    """Test cases para cálculo de IVA"""

    def test_calculate_iva(self):
        """Test cálculo básico de IVA"""
        # IVA del 13% sobre 1000
        iva = calculate_iva(1000)
        self.assertEqual(iva, 130.0)

        # IVA del 13% sobre 500
        iva = calculate_iva(500)
        self.assertEqual(iva, 65.0)

    def test_calculate_iva_with_custom_rate(self):
        """Test cálculo de IVA con tasa personalizada"""
        # IVA del 10% sobre 1000
        iva = calculate_iva(1000, rate=10)
        self.assertEqual(iva, 100.0)

    def test_calculate_total_with_iva(self):
        """Test cálculo de total con IVA incluido"""
        result = calculate_total_with_iva(1000)

        self.assertEqual(result['base'], 1000.0)
        self.assertEqual(result['iva'], 130.0)
        self.assertEqual(result['total'], 1130.0)
        self.assertEqual(result['rate'], 13.0)

    def test_extract_iva_from_total(self):
        """Test extracción de IVA de total con IVA"""
        # Total de 1130 incluye IVA 13%
        result = extract_iva_from_total(1130)

        self.assertEqual(result['base'], 1000.0)
        self.assertEqual(result['iva'], 130.0)
        self.assertEqual(result['total'], 1130.0)

    def test_iva_rate_constant(self):
        """Test que la constante IVA_RATE sea 13%"""
        self.assertEqual(IVA_RATE, 13.0)

    def test_iva_rounding(self):
        """Test redondeo de IVA"""
        # 13% de 100.5556 = 13.072228, debe redondear a 13.07
        iva = calculate_iva(100.5556)
        self.assertEqual(iva, 13.07)

    def test_iva_zero_amount(self):
        """Test IVA sobre monto cero"""
        iva = calculate_iva(0)
        self.assertEqual(iva, 0.0)

    def test_iva_negative_amount(self):
        """Test IVA sobre monto negativo (nota de crédito)"""
        iva = calculate_iva(-1000)
        self.assertEqual(iva, -130.0)


class TestIVAInvoice(FrappeTestCase):
    """Test cases para aplicación de IVA en facturas"""

    def setUp(self):
        """Setup antes de cada test"""
        # Crear empresa de prueba Bolivia
        if not frappe.db.exists('Company', 'Test Company Bolivia'):
            company = frappe.get_doc({
                'doctype': 'Company',
                'company_name': 'Test Company Bolivia',
                'abbr': 'TCB',
                'country': 'Bolivia',
                'default_currency': 'BOB'
            }).insert(ignore_permissions=True)

    def tearDown(self):
        """Cleanup después de cada test"""
        frappe.db.rollback()

    def test_is_bolivia_company(self):
        """Test verificación de empresa boliviana"""
        from nexo_bolivia.tax_engine.iva import is_bolivia_company

        is_bolivia = is_bolivia_company('Test Company Bolivia')
        self.assertTrue(is_bolivia)

    def test_calculate_iva_balance(self):
        """Test cálculo de balance IVA"""
        from nexo_bolivia.tax_engine.iva import calculate_iva_balance
        from datetime import datetime

        # Crear facturas de prueba (requiere setup complejo)
        # Por ahora test básico
        today = datetime.today().strftime('%Y-%m-%d')

        balance = calculate_iva_balance('Test Company Bolivia', today, today)

        self.assertIn('iva_debit_fiscal', balance)
        self.assertIn('iva_credit_fiscal', balance)
        self.assertIn('balance', balance)
        self.assertIn('status', balance)


class TestIVAFormulas(FrappeTestCase):
    """Test cases para fórmulas matemáticas de IVA"""

    def test_iva_formula_consistency(self):
        """Test que calcular y extraer IVA sean operaciones inversas"""
        base = 1000

        # Calcular total con IVA
        result = calculate_total_with_iva(base)
        total = result['total']

        # Extraer base desde total
        extracted = extract_iva_from_total(total)

        # Debe dar el mismo base original
        self.assertEqual(extracted['base'], base)

    def test_multiple_amounts(self):
        """Test IVA con múltiples montos"""
        amounts = [100, 500, 1000, 5000, 10000]

        for amount in amounts:
            iva = calculate_iva(amount)
            expected = amount * 0.13
            self.assertEqual(iva, round(expected, 2))
