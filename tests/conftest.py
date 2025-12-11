"""Pytest configuration and shared fixtures for Nexo E2E tests."""

import os
import sys
import pytest
import frappe
from datetime import datetime, timedelta

# Add apps to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'apps', 'nexo_core'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'apps', 'nexo_bolivia'))


@pytest.fixture(scope="session")
def frappe_session():
    """Initialize Frappe for test session."""
    if not frappe.db:
        frappe.init_site('test_site')
    yield
    # Cleanup will happen when tests end


@pytest.fixture(autouse=True)
def reset_db():
    """Reset database between tests."""
    yield
    # Rollback changes after each test
    if frappe.db:
        try:
            frappe.db.rollback()
        except Exception:
            pass


@pytest.fixture
def test_company():
    """Create a test company for Bolivia."""
    company = frappe.get_doc({
        'doctype': 'Company',
        'company_name': f'Test Company {datetime.now().timestamp()}',
        'country': 'Bolivia',
        'abbr': 'TC',
        'parent_company': '',
        'company_type': 'Individual',
        'default_currency': 'BOB',
        'chart_of_accounts': 'Bolivia'
    })
    try:
        company.insert()
        company.submit()
    except frappe.DuplicateError:
        company = frappe.get_doc('Company', company.name)

    return company


@pytest.fixture
def test_supplier(test_company):
    """Create a test supplier."""
    supplier = frappe.get_doc({
        'doctype': 'Supplier',
        'supplier_name': f'Test Supplier {datetime.now().timestamp()}',
        'supplier_type': 'Services',
        'country': 'Bolivia',
        'currency': 'BOB',
        'tax_id': '123456789',
        'addresses': [{
            'doctype': 'Dynamic Link',
            'link_doctype': 'Supplier',
            'link_name': '',
            'address_line1': 'Test Address',
            'city': 'La Paz',
            'state': 'La Paz',
            'country': 'Bolivia',
            'address_type': 'Billing'
        }]
    })
    try:
        supplier.insert()
    except frappe.DuplicateError:
        supplier = frappe.get_doc('Supplier', supplier.name)

    return supplier


@pytest.fixture
def test_customer(test_company):
    """Create a test customer."""
    customer = frappe.get_doc({
        'doctype': 'Customer',
        'customer_name': f'Test Customer {datetime.now().timestamp()}',
        'customer_type': 'Individual',
        'country': 'Bolivia',
        'currency': 'BOB',
        'tax_id': '987654321',
    })
    try:
        customer.insert()
    except frappe.DuplicateError:
        customer = frappe.get_doc('Customer', customer.name)

    return customer


@pytest.fixture
def test_item():
    """Create a test item."""
    item = frappe.get_doc({
        'doctype': 'Item',
        'item_code': f'TEST-ITEM-{datetime.now().timestamp()}',
        'item_name': 'Test Item',
        'item_group': 'Products',
        'stock_uom': 'Nos',
        'is_stock_item': 1,
        'standard_rate': 100,
    })
    try:
        item.insert()
    except frappe.DuplicateError:
        item = frappe.get_doc('Item', item.item_code)

    return item


@pytest.fixture
def test_fiscal_year():
    """Create a test fiscal year."""
    fiscal_year = datetime.now().year
    fy_doc = frappe.get_doc({
        'doctype': 'Fiscal Year',
        'year': str(fiscal_year),
        'year_start_date': f'{fiscal_year}-01-01',
        'year_end_date': f'{fiscal_year}-12-31',
        'is_closing_fiscal_year': 0
    })

    try:
        fy_doc.insert()
    except frappe.DuplicateError:
        fy_doc = frappe.get_doc('Fiscal Year', str(fiscal_year))

    return fy_doc


@pytest.fixture
def create_purchase_invoice(test_company, test_supplier, test_item):
    """Factory to create purchase invoices."""
    def _create(qty=10, rate=100, submit=False):
        pi = frappe.get_doc({
            'doctype': 'Purchase Invoice',
            'company': test_company.name,
            'supplier': test_supplier.name,
            'posting_date': datetime.now().date(),
            'due_date': (datetime.now() + timedelta(days=30)).date(),
            'items': [{
                'item_code': test_item.item_code,
                'qty': qty,
                'rate': rate,
                'item_name': test_item.item_name,
                'uom': 'Nos'
            }],
            'taxes': [{
                'charge_type': 'On Net Total',
                'account_head': 'IVA Pagado - IVA',
                'description': 'IVA 13%',
                'rate': 13
            }]
        })
        pi.insert()

        if submit:
            pi.submit()

        return pi

    return _create


@pytest.fixture
def create_sales_invoice(test_company, test_customer, test_item):
    """Factory to create sales invoices."""
    def _create(qty=10, rate=100, submit=False):
        si = frappe.get_doc({
            'doctype': 'Sales Invoice',
            'company': test_company.name,
            'customer': test_customer.name,
            'posting_date': datetime.now().date(),
            'due_date': (datetime.now() + timedelta(days=30)).date(),
            'debit_to': 'Debtors - TC',
            'items': [{
                'item_code': test_item.item_code,
                'qty': qty,
                'rate': rate,
                'item_name': test_item.item_name,
                'uom': 'Nos'
            }],
            'taxes': [{
                'charge_type': 'On Net Total',
                'account_head': 'IVA Cobrado - IVA',
                'description': 'IVA 13%',
                'rate': 13
            }]
        })
        si.insert()

        if submit:
            si.submit()

        return si

    return _create


# Mock context managers
class MockSIATAPI:
    """Mock SIAT API for testing without real API calls."""

    def __init__(self):
        self.requests = []
        self.responses = {}

    def __enter__(self):
        self.original_post = frappe.call
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        frappe.call = self.original_post

    def register_response(self, method, response):
        """Register a mock response for a method."""
        self.responses[method] = response


@pytest.fixture
def mock_siat_api():
    """Fixture for mocking SIAT API."""
    return MockSIATAPI()


@pytest.fixture
def test_data_cleanup():
    """Cleanup test data after tests."""
    created_docs = []

    def _add_to_cleanup(doctype, docname):
        created_docs.append((doctype, docname))

    yield _add_to_cleanup

    # Cleanup
    for doctype, docname in created_docs:
        try:
            frappe.delete_doc(doctype, docname, force=True)
        except Exception:
            pass


# Utility functions
def setup_test_company_for_sin(company):
    """Setup a company with SIN configuration."""
    company.custom_nit = '123456789'
    company.custom_razon_social = 'Test Company'
    company.custom_sin_enabled = 1
    company.custom_sin_environment = 'Testing'
    company.save()
    return company


def create_tax_account(company, account_name, account_type='Tax'):
    """Create a tax account for testing."""
    account = frappe.get_doc({
        'doctype': 'Account',
        'account_name': account_name,
        'parent_account': 'Tax Assets - TC',
        'company': company.name,
        'account_type': account_type,
        'is_group': 0
    })
    try:
        account.insert()
    except frappe.DuplicateError:
        account = frappe.get_doc('Account', account.name)

    return account


def get_account_balance(account_name, company, date=None):
    """Get account balance as of a specific date."""
    if date is None:
        date = datetime.now().date()

    gl_entries = frappe.db.get_list(
        'GL Entry',
        filters={
            'account': account_name,
            'company': company.name,
            'posting_date': ['<=', date]
        }
    )

    balance = 0
    for entry in gl_entries:
        entry_doc = frappe.get_doc('GL Entry', entry.name)
        balance += (entry_doc.debit - entry_doc.credit)

    return balance
