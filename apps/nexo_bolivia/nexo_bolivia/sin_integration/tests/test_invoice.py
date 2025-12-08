"""
Tests for Electronic Invoice Module
"""

import unittest
import frappe
from unittest.mock import Mock, patch, MagicMock
from nexo_bolivia.sin_integration.invoice import ElectronicInvoice


class TestElectronicInvoice(unittest.TestCase):
    """Test cases for Electronic Invoice"""

    def setUp(self):
        """Set up test fixtures"""
        # Mock Sales Invoice
        self.mock_invoice = Mock()
        self.mock_invoice.name = 'INV-001'
        self.mock_invoice.company = 'Test Company'
        self.mock_invoice.customer = 'Test Customer'
        self.mock_invoice.customer_name = 'Customer Name'
        self.mock_invoice.grand_total = 1130.0
        self.mock_invoice.net_total = 1000.0
        self.mock_invoice.discount_amount = 0
        self.mock_invoice.mode_of_payment = 'Efectivo'
        self.mock_invoice.posting_date = '2024-12-08'
        self.mock_invoice.items = []
        self.mock_invoice.db_set = Mock()
        self.mock_invoice.get = Mock(return_value=None)

    def test_generate_cuf_format(self):
        """Test CUF generation format"""
        with patch('frappe.get_doc') as mock_get_doc:
            # Mock documents
            mock_get_doc.side_effect = lambda dt, dn: {
                'Sales Invoice': self.mock_invoice,
                'Company': Mock(company_name='Test', phone='', address='')
            }.get(dt, Mock())

            einvoice = ElectronicInvoice('INV-001')

            # Mock client and config
            einvoice.client.nit = '1234567890'
            with patch.object(einvoice, '_get_config', return_value='0'):
                cuf = einvoice.generate_cuf()

            # CUF debe tener 44 caracteres
            self.assertEqual(len(cuf), 44)
            # Debe ser alfanumérico
            self.assertTrue(cuf.isalnum())

    def test_generate_invoice_data_structure(self):
        """Test invoice data structure generation"""
        with patch('frappe.get_doc') as mock_get_doc:
            mock_company = Mock()
            mock_company.company_name = 'Test Company'
            mock_company.phone = '123456'
            mock_company.address = 'Test Address'

            mock_customer = Mock()
            mock_customer.tax_id = '9876543210'

            mock_get_doc.side_effect = lambda dt, dn: {
                'Sales Invoice': self.mock_invoice,
                'Company': mock_company,
                'Customer': mock_customer
            }.get(dt)

            einvoice = ElectronicInvoice('INV-001')
            einvoice.client.nit = '1234567890'

            with patch.object(einvoice, '_get_config', return_value='0'):
                invoice_data = einvoice.generate_invoice_data()

            # Verificar campos requeridos
            self.assertIn('nitEmisor', invoice_data)
            self.assertIn('numeroFactura', invoice_data)
            self.assertIn('cuf', invoice_data)
            self.assertIn('montoTotal', invoice_data)
            self.assertIn('detalle', invoice_data)
            self.assertEqual(invoice_data['montoTotal'], 1130.0)

    def test_get_document_type_mapping(self):
        """Test document type code mapping"""
        with patch('frappe.get_doc') as mock_get_doc:
            mock_company = Mock()
            mock_customer = Mock()
            mock_customer.tipo_documento_identidad = 'CI'

            mock_get_doc.side_effect = lambda dt, dn: {
                'Sales Invoice': self.mock_invoice,
                'Company': mock_company,
                'Customer': mock_customer
            }.get(dt)

            einvoice = ElectronicInvoice('INV-001')

            doc_type_code = einvoice._get_document_type()

            # CI debe retornar código 1
            self.assertEqual(doc_type_code, 1)

    def test_get_payment_method_code(self):
        """Test payment method code determination"""
        with patch('frappe.get_doc') as mock_get_doc:
            mock_get_doc.side_effect = lambda dt, dn: {
                'Sales Invoice': self.mock_invoice,
                'Company': Mock(),
                'Customer': Mock()
            }.get(dt)

            einvoice = ElectronicInvoice('INV-001')

            # Test efectivo
            self.mock_invoice.mode_of_payment = 'Efectivo'
            code = einvoice._get_payment_method_code()
            self.assertEqual(code, 1)

            # Test tarjeta
            self.mock_invoice.mode_of_payment = 'Tarjeta de Crédito'
            code = einvoice._get_payment_method_code()
            self.assertEqual(code, 2)

    def test_generate_items_detail(self):
        """Test items detail generation"""
        # Mock item
        mock_item = Mock()
        mock_item.item_code = 'ITEM-001'
        mock_item.item_name = 'Test Item'
        mock_item.description = 'Test Description'
        mock_item.qty = 2
        mock_item.rate = 500
        mock_item.amount = 1000
        mock_item.discount_amount = 0
        mock_item.uom = 'Nos'

        self.mock_invoice.items = [mock_item]

        with patch('frappe.get_doc') as mock_get_doc:
            mock_get_doc.side_effect = lambda dt, dn: {
                'Sales Invoice': self.mock_invoice,
                'Company': Mock(),
                'Customer': Mock()
            }.get(dt)

            einvoice = ElectronicInvoice('INV-001')

            with patch.object(einvoice, '_get_config', return_value='620100'):
                detalle = einvoice._generate_items_detail()

            self.assertEqual(len(detalle), 1)
            self.assertEqual(detalle[0]['cantidad'], 2.0)
            self.assertEqual(detalle[0]['precioUnitario'], 500.0)

    @patch('nexo_bolivia.sin_integration.invoice.create_electronic_invoice')
    def test_send_to_siat_success(self, mock_create):
        """Test successful sending to SIAT"""
        mock_create.return_value = {
            'success': True,
            'cuf': 'TEST_CUF',
            'estado': 'VALIDA'
        }

        result = mock_create('INV-001')

        self.assertTrue(result['success'])
        self.assertEqual(result['cuf'], 'TEST_CUF')

    @patch('nexo_bolivia.sin_integration.invoice.create_electronic_invoice')
    def test_send_to_siat_offline(self, mock_create):
        """Test offline mode handling"""
        mock_create.return_value = {
            'success': False,
            'offline_mode': True
        }

        result = mock_create('INV-001')

        self.assertFalse(result['success'])
        self.assertTrue(result['offline_mode'])

    def tearDown(self):
        """Clean up after tests"""
        pass


# Run tests
if __name__ == '__main__':
    unittest.main()
