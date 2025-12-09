# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

"""Tests para Excel Exporter"""

import frappe
import unittest


class TestExcelExporter(unittest.TestCase):
    """Suite de tests para Excel Exporter"""

    def test_export_libro_ventas_to_excel(self):
        """Test: Exportación a Excel de Libro Ventas"""
        from nexo_bolivia.reports.exporters.excel_exporter import export_libro_ventas_to_excel

        data = [
            {
                'nro': 1,
                'posting_date': '2024-01-01',
                'name': 'SI-001',
                'cuf': 'CUF123',
                'status': 'Válida',
                'customer_nit': '123456789',
                'customer_name': 'Test Customer',
                'total_amount': 1000,
                'ice_amount': 0,
                'exempt_amount': 0,
                'taxable_amount': 1000,
                'iva_amount': 130,
                'control_code': 'CODE123'
            }
        ]

        columns = [
            {'fieldname': 'nro', 'label': 'Nro', 'fieldtype': 'Int'},
            {'fieldname': 'posting_date', 'label': 'Fecha', 'fieldtype': 'Date'},
            {'fieldname': 'name', 'label': 'Factura', 'fieldtype': 'Link'},
            {'fieldname': 'total_amount', 'label': 'Total', 'fieldtype': 'Currency'}
        ]

        filters = {
            'company': frappe.db.get_value('Company', {'disabled': 0}, 'name') or 'Default Company',
            'from_date': '2024-01-01',
            'to_date': '2024-01-31'
        }

        # No debe lanzar excepción
        try:
            result = export_libro_ventas_to_excel(data, columns, filters)
            # result será la ruta del archivo
            self.assertIsNotNone(result)
        except ImportError:
            # openpyxl no está instalado
            self.skipTest('openpyxl not installed')

    def test_export_libro_compras_to_excel(self):
        """Test: Exportación a Excel de Libro Compras"""
        from nexo_bolivia.reports.exporters.excel_exporter import export_libro_compras_to_excel

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

        columns = [
            {'fieldname': 'nro', 'label': 'Nro', 'fieldtype': 'Int'},
            {'fieldname': 'posting_date', 'label': 'Fecha', 'fieldtype': 'Date'},
            {'fieldname': 'name', 'label': 'Factura', 'fieldtype': 'Link'},
            {'fieldname': 'total_amount', 'label': 'Total', 'fieldtype': 'Currency'}
        ]

        filters = {
            'company': frappe.db.get_value('Company', {'disabled': 0}, 'name') or 'Default Company',
            'from_date': '2024-01-01',
            'to_date': '2024-01-31'
        }

        try:
            result = export_libro_compras_to_excel(data, columns, filters)
            self.assertIsNotNone(result)
        except ImportError:
            self.skipTest('openpyxl not installed')


if __name__ == '__main__':
    unittest.main()
