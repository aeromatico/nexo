# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

import frappe
import unittest
from datetime import timedelta


class TestTenant(unittest.TestCase):
    """Test cases for Tenant DocType"""

    def setUp(self):
        """Setup test data"""
        # Create test subscription plan
        if not frappe.db.exists("Subscription Plan", "Test Plan"):
            test_plan = frappe.new_doc("Subscription Plan")
            test_plan.plan_name = "Test Plan"
            test_plan.max_users = 5
            test_plan.max_storage_gb = 1.0
            test_plan.max_sites = 1
            test_plan.price_monthly = 29
            test_plan.currency = "BOB"
            test_plan.is_active = 1
            test_plan.insert(ignore_permissions=True)

    def test_create_tenant(self):
        """Test creating a new tenant"""
        tenant = frappe.new_doc("Tenant")
        tenant.tenant_name = "test_tenant"
        tenant.subdomain = "test-tenant"
        tenant.company_name = "Test Company"
        tenant.nit = "1234567890123"
        tenant.admin_email = "admin@test.com"
        tenant.admin_password = "secure_password"
        tenant.subscription_plan = "Test Plan"

        tenant.insert(ignore_permissions=True)

        self.assertEqual(tenant.name, "test-tenant")
        self.assertEqual(tenant.status, "Trial")
        self.assertIsNotNone(tenant.created_at)

    def test_subdomain_validation(self):
        """Test subdomain validation"""
        tenant = frappe.new_doc("Tenant")
        tenant.tenant_name = "test"
        tenant.subdomain = "invalid spaces"
        tenant.company_name = "Test"
        tenant.nit = "1234567890123"
        tenant.admin_email = "test@test.com"
        tenant.admin_password = "password"
        tenant.subscription_plan = "Test Plan"

        self.assertRaises(frappe.ValidationError, tenant.insert)

    def test_subdomain_length_validation(self):
        """Test subdomain minimum length"""
        tenant = frappe.new_doc("Tenant")
        tenant.tenant_name = "t"
        tenant.subdomain = "ab"  # Too short
        tenant.company_name = "Test"
        tenant.nit = "1234567890123"
        tenant.admin_email = "test@test.com"
        tenant.admin_password = "password"
        tenant.subscription_plan = "Test Plan"

        self.assertRaises(frappe.ValidationError, tenant.insert)

    def test_reserved_subdomain(self):
        """Test that reserved subdomains are rejected"""
        tenant = frappe.new_doc("Tenant")
        tenant.tenant_name = "admin"
        tenant.subdomain = "admin"  # Reserved
        tenant.company_name = "Test"
        tenant.nit = "1234567890123"
        tenant.admin_email = "test@test.com"
        tenant.admin_password = "password"
        tenant.subscription_plan = "Test Plan"

        self.assertRaises(frappe.ValidationError, tenant.insert)

    def test_nit_validation(self):
        """Test NIT validation"""
        tenant = frappe.new_doc("Tenant")
        tenant.tenant_name = "test"
        tenant.subdomain = "test-valid"
        tenant.company_name = "Test"
        tenant.nit = "invalid_nit"  # Not numeric
        tenant.admin_email = "test@test.com"
        tenant.admin_password = "password"
        tenant.subscription_plan = "Test Plan"

        self.assertRaises(frappe.ValidationError, tenant.insert)

    def test_nit_length_validation(self):
        """Test NIT must be 13 digits"""
        tenant = frappe.new_doc("Tenant")
        tenant.tenant_name = "test"
        tenant.subdomain = "test-nit"
        tenant.company_name = "Test"
        tenant.nit = "123456789"  # Too short
        tenant.admin_email = "test@test.com"
        tenant.admin_password = "password"
        tenant.subscription_plan = "Test Plan"

        self.assertRaises(frappe.ValidationError, tenant.insert)

    def test_email_validation(self):
        """Test email format validation"""
        tenant = frappe.new_doc("Tenant")
        tenant.tenant_name = "test"
        tenant.subdomain = "test-email"
        tenant.company_name = "Test"
        tenant.nit = "1234567890123"
        tenant.admin_email = "invalid_email"
        tenant.admin_password = "password"
        tenant.subscription_plan = "Test Plan"

        self.assertRaises(frappe.ValidationError, tenant.insert)

    def test_get_active_tenants(self):
        """Test getting active tenants"""
        # Create active tenant
        tenant = frappe.new_doc("Tenant")
        tenant.tenant_name = "active_test"
        tenant.subdomain = "active-test"
        tenant.company_name = "Active Test"
        tenant.nit = "1234567890124"
        tenant.admin_email = "active@test.com"
        tenant.admin_password = "password"
        tenant.subscription_plan = "Test Plan"
        tenant.status = "Active"
        tenant.insert(ignore_permissions=True)

        active_tenants = frappe.get_list(
            "Tenant",
            filters={"status": ["in", ["Active", "Trial"]]},
            fields=["name", "status"]
        )

        self.assertGreaterEqual(len(active_tenants), 1)

    def test_plan_limits(self):
        """Test getting plan limits for tenant"""
        tenant = frappe.new_doc("Tenant")
        tenant.tenant_name = "limits_test"
        tenant.subdomain = "limits-test"
        tenant.company_name = "Limits Test"
        tenant.nit = "1234567890125"
        tenant.admin_email = "limits@test.com"
        tenant.admin_password = "password"
        tenant.subscription_plan = "Test Plan"
        tenant.insert(ignore_permissions=True)

        limits = tenant.get_plan_limits()

        self.assertEqual(limits["max_users"], 5)
        self.assertEqual(limits["max_storage_gb"], 1.0)

    def test_trial_end_date_set(self):
        """Test that trial end date is automatically set"""
        tenant = frappe.new_doc("Tenant")
        tenant.tenant_name = "trial_test"
        tenant.subdomain = "trial-test"
        tenant.company_name = "Trial Test"
        tenant.nit = "1234567890126"
        tenant.admin_email = "trial@test.com"
        tenant.admin_password = "password"
        tenant.subscription_plan = "Test Plan"
        tenant.insert(ignore_permissions=True)

        self.assertIsNotNone(tenant.trial_end_date)
        self.assertGreater(tenant.trial_end_date, frappe.utils.today())

    def test_tenant_suspend(self):
        """Test suspending a tenant"""
        tenant = frappe.new_doc("Tenant")
        tenant.tenant_name = "suspend_test"
        tenant.subdomain = "suspend-test"
        tenant.company_name = "Suspend Test"
        tenant.nit = "1234567890127"
        tenant.admin_email = "suspend@test.com"
        tenant.admin_password = "password"
        tenant.subscription_plan = "Test Plan"
        tenant.status = "Active"
        tenant.insert(ignore_permissions=True)

        tenant.suspend()

        updated_tenant = frappe.get_doc("Tenant", tenant.name)
        self.assertEqual(updated_tenant.status, "Suspended")

    def test_tenant_activate(self):
        """Test activating a tenant"""
        tenant = frappe.new_doc("Tenant")
        tenant.tenant_name = "activate_test"
        tenant.subdomain = "activate-test"
        tenant.company_name = "Activate Test"
        tenant.nit = "1234567890128"
        tenant.admin_email = "activate@test.com"
        tenant.admin_password = "password"
        tenant.subscription_plan = "Test Plan"
        tenant.status = "Trial"
        tenant.insert(ignore_permissions=True)

        tenant.activate()

        updated_tenant = frappe.get_doc("Tenant", tenant.name)
        self.assertEqual(updated_tenant.status, "Active")
        self.assertIsNotNone(updated_tenant.activated_at)

    def tearDown(self):
        """Clean up test data"""
        # Clean up test tenants
        tenants = frappe.db.get_list("Tenant", filters={"tenant_name": ["like", "%_test"]})
        for tenant in tenants:
            frappe.db.delete("Tenant", tenant.name, ignore_permissions=True)
        frappe.db.commit()
