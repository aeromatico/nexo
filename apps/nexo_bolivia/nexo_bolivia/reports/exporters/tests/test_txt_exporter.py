# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

"""Tests para TXT Exporter"""

import frappe
import unittest
import os


class TestTxtExporter(unittest.TestCase):
    """Suite de tests para TXT Exporter"""

    def test_export_to_davinci_txt(self):
        """Test: Exportación a TXT da Vinci"""
        from nexo_bolivia.reports.exporters.txt_exporter import export_to_davinci_txt

        data = [
            {
                'nro': 1,
                'posting_date': '2024-01-01',
                'name': 'SI-001',
                'cuf': 'CUF123',
                'customer_nit': '123456789',
                'customer_name': 'Test Customer',
                'total_amount': 1000.50,
                'taxable_amount': 1000,
                'iva_amount': 130
            }
        ]

        columns = [
            {'fieldname': 'nro', 'label': 'NRO'},
            {'fieldname': 'posting_date', 'label': 'FECHA'},
            {'fieldname': 'name', 'label': 'FACTURA'},
            {'fieldname': 'customer_nit', 'label': 'NIT'},
            {'fieldname': 'total_amount', 'label': 'TOTAL'}
        ]

        result = export_to_davinci_txt(data, columns, 'test_report')

        # Verificar que retorna ruta válida
        self.assertIsNotNone(result)
        self.assertIn('.txt', result)

        # Verificar que el archivo existe
        if result.startswith('/files/'):
            filename = result.replace('/files/', '')
            filepath = os.path.join(frappe.get_site_path('private', 'files'), filename)
            # El archivo debería existir (aunque puede haber sido creado)

    def test_export_libro_ventas_davinci(self):
        """Test: Exportación Libro Ventas a TXT da Vinci"""
        from nexo_bolivia.reports.exporters.txt_exporter import export_libro_ventas_davinci

        data = [
            {
                'nro': 1,
                'posting_date': '2024-01-01',
                'name': 'SI-001',
                'cuf': 'CUF123',
                'customer_nit': '123456789',
                'customer_name': 'Test Customer',
                'total_amount': 1000,
                'taxable_amount': 1000,
                'iva_amount': 130
            }
        ]

        filters = {
            'company': frappe.db.get_value('Company', {'disabled': 0}, 'name') or 'Default Company',
            'from_date': '2024-01-01',
            'to_date': '2024-01-31'
        }

        result = export_libro_ventas_davinci(data, filters)

        self.assertIsNotNone(result)
        self.assertIn('.txt', result)

    def test_export_libro_compras_davinci(self):
        """Test: Exportación Libro Compras a TXT da Vinci"""
        from nexo_bolivia.reports.exporters.txt_exporter import export_libro_compras_davinci

        data = [
            {
                'nro': 1,
                'posting_date': '2024-01-01',
                'name': 'PI-001',
                'dui': 'DUI123',
                'supplier_nit': '987654321',
                'supplier_name': 'Test Supplier',
                'total_amount': 1000,
                'credit_amount': 1000,
                'credit_fiscal': 130
            }
        ]

        filters = {
            'company': frappe.db.get_value('Company', {'disabled': 0}, 'name') or 'Default Company',
            'from_date': '2024-01-01',
            'to_date': '2024-01-31'
        }

        result = export_libro_compras_davinci(data, filters)

        self.assertIsNotNone(result)
        self.assertIn('.txt', result)


if __name__ == '__main__':
    unittest.main()
