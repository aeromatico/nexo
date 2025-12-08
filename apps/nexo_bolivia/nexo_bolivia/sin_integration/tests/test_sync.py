"""
Tests for SIAT Synchronization
"""

import unittest
import frappe
from unittest.mock import Mock, patch
from nexo_bolivia.sin_integration.sync import (
    validate_siat_status,
    check_cufd_validity,
    get_pending_invoices_count
)
from datetime import datetime, timedelta


class TestSIATSync(unittest.TestCase):
    """Test cases for SIAT Synchronization"""

    def test_validate_siat_status_online(self):
        """Test SIAT status validation when online"""
        with patch('nexo_bolivia.sin_integration.sync.SIATClient') as mock_client_class:
            mock_client = Mock()
            mock_client.test_connection.return_value = {'success': True}
            mock_client_class.return_value = mock_client

            result = validate_siat_status()

            self.assertTrue(result['online'])
            self.assertEqual(result['status'], 'ONLINE')

    def test_validate_siat_status_offline(self):
        """Test SIAT status validation when offline"""
        with patch('nexo_bolivia.sin_integration.sync.SIATClient') as mock_client_class:
            mock_client = Mock()
            mock_client.test_connection.return_value = {'success': False, 'message': 'Connection failed'}
            mock_client_class.return_value = mock_client

            result = validate_siat_status()

            self.assertFalse(result['online'])
            self.assertEqual(result['status'], 'OFFLINE')

    def test_check_cufd_validity_valid(self):
        """Test CUFD validity check with valid CUFD"""
        with patch('frappe.get_doc') as mock_get_doc:
            mock_company = Mock()
            mock_company.sin_cufd = 'TEST_CUFD'
            mock_company.sin_cufd_fecha = datetime.now().date()
            mock_get_doc.return_value = mock_company

            result = check_cufd_validity('Test Company')

            self.assertTrue(result['valid'])
            self.assertEqual(result['cufd'], 'TEST_CUFD')

    def test_check_cufd_validity_expired(self):
        """Test CUFD validity check with expired CUFD"""
        with patch('frappe.get_doc') as mock_get_doc:
            mock_company = Mock()
            mock_company.sin_cufd = 'TEST_CUFD'
            # CUFD de ayer
            mock_company.sin_cufd_fecha = datetime.now().date() - timedelta(days=1)
            mock_get_doc.return_value = mock_company

            result = check_cufd_validity('Test Company')

            self.assertFalse(result['valid'])
            self.assertEqual(result['reason'], 'CUFD vencido')
            self.assertTrue(result['needs_renewal'])

    def test_check_cufd_validity_not_configured(self):
        """Test CUFD validity check when not configured"""
        with patch('frappe.get_doc') as mock_get_doc:
            mock_company = Mock()
            mock_company.sin_cufd = None
            mock_company.sin_cufd_fecha = None
            mock_get_doc.return_value = mock_company

            result = check_cufd_validity('Test Company')

            self.assertFalse(result['valid'])
            self.assertEqual(result['reason'], 'CUFD no configurado')
            self.assertTrue(result['needs_renewal'])

    @patch('frappe.db.count')
    def test_get_pending_invoices_count(self, mock_count):
        """Test getting count of pending invoices"""
        mock_count.return_value = 5

        count = get_pending_invoices_count('Test Company')

        self.assertEqual(count, 5)
        mock_count.assert_called_once()

    @patch('frappe.db.count')
    def test_get_pending_invoices_count_zero(self, mock_count):
        """Test getting count when no pending invoices"""
        mock_count.return_value = 0

        count = get_pending_invoices_count()

        self.assertEqual(count, 0)

    def tearDown(self):
        """Clean up after tests"""
        pass


# Run tests
if __name__ == '__main__':
    unittest.main()
