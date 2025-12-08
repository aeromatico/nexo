"""
Tests for SIAT Client
"""

import unittest
import frappe
from unittest.mock import Mock, patch, MagicMock
from nexo_bolivia.sin_integration.client import SIATClient


class TestSIATClient(unittest.TestCase):
    """Test cases for SIATClient"""

    def setUp(self):
        """Set up test fixtures"""
        self.client = SIATClient()
        self.client.base_url = 'https://test.impuestos.gob.bo'
        self.client.nit = '1234567890'

    def test_client_initialization(self):
        """Test client initializes correctly"""
        self.assertIsNotNone(self.client)
        self.assertEqual(self.client.nit, '1234567890')
        self.assertIsNone(self.client.token)

    @patch('requests.post')
    def test_authenticate_success(self, mock_post):
        """Test successful authentication"""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            'transaccion': True,
            'codigo': 200,
            'respuesta': {
                'token': 'test_token_123'
            }
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        # Mock config
        with patch.object(self.client, '_get_config', side_effect=lambda k, d=None: {
            'sin_username': 'test_user',
            'sin_password': 'test_pass',
            'sin_modalidad': '1'
        }.get(k, d)):
            result = self.client.authenticate()

        self.assertTrue(result['success'])
        self.assertEqual(self.client.token, 'test_token_123')

    @patch('requests.post')
    def test_authenticate_failure(self, mock_post):
        """Test authentication failure"""
        # Mock failed response
        mock_response = Mock()
        mock_response.json.return_value = {
            'transaccion': False,
            'codigo': 401,
            'mensaje': 'Credenciales inválidas'
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        # Mock config
        with patch.object(self.client, '_get_config', side_effect=lambda k, d=None: {
            'sin_username': 'test_user',
            'sin_password': 'wrong_pass',
            'sin_modalidad': '1'
        }.get(k, d)):
            with self.assertRaises(frappe.ValidationError):
                self.client.authenticate()

    @patch('requests.post')
    def test_send_invoice_success(self, mock_post):
        """Test successful invoice sending"""
        self.client.token = 'test_token'
        self.client.token_expiry = None  # Bypass expiry check

        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            'transaccion': True,
            'codigo': 200,
            'respuesta': {
                'cuf': 'TEST_CUF_12345',
                'estado': 'VALIDA'
            }
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        # Mock _ensure_token
        with patch.object(self.client, '_ensure_token'):
            invoice_data = {'numeroFactura': '001'}
            result = self.client.send_invoice(invoice_data)

        self.assertTrue(result['success'])
        self.assertEqual(result['cuf'], 'TEST_CUF_12345')
        self.assertEqual(result['estado'], 'VALIDA')

    @patch('requests.post')
    def test_send_invoice_offline_mode(self, mock_post):
        """Test invoice sending when SIAT is offline"""
        self.client.token = 'test_token'

        # Mock connection error
        mock_post.side_effect = Exception('Connection error')

        with patch.object(self.client, '_ensure_token'):
            invoice_data = {'numeroFactura': '001'}
            result = self.client.send_invoice(invoice_data)

        self.assertFalse(result['success'])
        self.assertTrue(result['offline_mode'])

    @patch('requests.post')
    def test_verify_invoice(self, mock_post):
        """Test invoice verification"""
        self.client.token = 'test_token'

        # Mock successful verification
        mock_response = Mock()
        mock_response.json.return_value = {
            'transaccion': True,
            'respuesta': {
                'estado': 'VALIDA',
                'valida': True
            }
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        with patch.object(self.client, '_ensure_token'):
            result = self.client.verify_invoice('TEST_CUF')

        self.assertTrue(result['success'])
        self.assertEqual(result['estado'], 'VALIDA')

    @patch('requests.post')
    def test_cancel_invoice(self, mock_post):
        """Test invoice cancellation"""
        self.client.token = 'test_token'

        # Mock successful cancellation
        mock_response = Mock()
        mock_response.json.return_value = {
            'transaccion': True,
            'respuesta': {
                'fechaAnulacion': '2024-12-08'
            }
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        with patch.object(self.client, '_ensure_token'):
            result = self.client.cancel_invoice('TEST_CUF', 1, 'Anulación de prueba')

        self.assertTrue(result['success'])
        self.assertEqual(result['estado'], 'ANULADA')

    def test_test_connection(self):
        """Test connection testing method"""
        with patch.object(self.client, 'authenticate') as mock_auth:
            mock_auth.return_value = {'success': True}

            result = self.client.test_connection()

            self.assertTrue(result['success'])
            self.assertIn('Conexión exitosa', result['message'])

    def tearDown(self):
        """Clean up after tests"""
        pass


# Run tests
if __name__ == '__main__':
    unittest.main()
