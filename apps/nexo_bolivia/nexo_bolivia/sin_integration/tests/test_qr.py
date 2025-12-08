"""
Tests for QR Code Generation
"""

import unittest
from nexo_bolivia.sin_integration.qr import generate_invoice_qr, verify_qr_content


class TestQRCode(unittest.TestCase):
    """Test cases for QR Code Generation"""

    def test_generate_qr_basic(self):
        """Test basic QR code generation"""
        qr_image = generate_invoice_qr(
            nit='1234567890',
            numero_factura='001',
            nit_cliente='9876543210',
            fecha_emision='2024-12-08',
            monto_total=1130.0,
            cuf='TEST_CUF_12345'
        )

        # Verificar que retorna base64
        self.assertIsNotNone(qr_image)
        self.assertTrue(qr_image.startswith('data:image/png;base64,'))

    def test_generate_qr_with_codigo_control(self):
        """Test QR generation with codigo control"""
        qr_image = generate_invoice_qr(
            nit='1234567890',
            numero_factura='001',
            nit_cliente='9876543210',
            fecha_emision='2024-12-08',
            monto_total=1130.0,
            cuf='TEST_CUF_12345',
            codigo_control='CTRL-123'
        )

        self.assertIsNotNone(qr_image)
        self.assertTrue(qr_image.startswith('data:image/png;base64,'))

    def test_verify_qr_content_valid(self):
        """Test QR content verification with valid data"""
        qr_data = '1234567890|001|9876543210|2024-12-08|1130.0|TEST_CUF_12345'

        result = verify_qr_content(qr_data)

        self.assertTrue(result['valid'])
        self.assertEqual(result['nit'], '1234567890')
        self.assertEqual(result['numero_factura'], '001')
        self.assertEqual(result['nit_cliente'], '9876543210')
        self.assertEqual(result['monto_total'], 1130.0)
        self.assertEqual(result['cuf'], 'TEST_CUF_12345')

    def test_verify_qr_content_with_codigo_control(self):
        """Test QR verification with codigo control"""
        qr_data = '1234567890|001|9876543210|2024-12-08|1130.0|CTRL-123|TEST_CUF_12345'

        result = verify_qr_content(qr_data)

        self.assertTrue(result['valid'])
        self.assertEqual(result['codigo_control'], 'CTRL-123')
        self.assertEqual(result['cuf'], 'TEST_CUF_12345')

    def test_verify_qr_content_invalid(self):
        """Test QR verification with invalid data"""
        qr_data = '1234567890|001'  # Incomplete

        result = verify_qr_content(qr_data)

        self.assertFalse(result['valid'])
        self.assertIn('error', result)

    def test_verify_qr_content_malformed(self):
        """Test QR verification with malformed data"""
        qr_data = '1234567890|001|9876543210|2024-12-08|not_a_number|TEST_CUF'

        result = verify_qr_content(qr_data)

        self.assertFalse(result['valid'])
        self.assertIn('error', result)

    def tearDown(self):
        """Clean up after tests"""
        pass


# Run tests
if __name__ == '__main__':
    unittest.main()
