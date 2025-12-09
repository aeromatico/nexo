# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

import frappe
import unittest
import json


class TestProvisioningAPI(unittest.TestCase):
    """Test cases for Provisioning API endpoints"""

    def setUp(self):
        """Setup test data"""
        # Create test subscription plan
        if not frappe.db.exists("Subscription Plan", "Prov Test Plan"):
            plan = frappe.new_doc("Subscription Plan")
            plan.plan_name = "Prov Test Plan"
            plan.max_users = 10
            plan.max_storage_gb = 5.0
            plan.max_sites = 1
            plan.price_monthly = 50
            plan.currency = "BOB"
            plan.is_active = 1
            plan.insert(ignore_permissions=True)

    def test_check_subdomain_available(self):
        """Test checking subdomain availability"""
        from nexo_core.api.provisioning_api import check_subdomain_available

        result = check_subdomain_available("available-subdomain-xyz")

        self.assertTrue(result["success"])
        self.assertTrue(result["available"])

    def test_check_subdomain_with_invalid_chars(self):
        """Test that invalid characters are rejected"""
        from nexo_core.api.provisioning_api import check_subdomain_available

        result = check_subdomain_available("invalid_domain!")

        self.assertFalse(result["success"])
        self.assertFalse(result["available"])

    def test_check_subdomain_too_short(self):
        """Test that subdomains that are too short are rejected"""
        from nexo_core.api.provisioning_api import check_subdomain_available

        result = check_subdomain_available("ab")

        self.assertFalse(result["success"])
        self.assertFalse(result["available"])

    def test_check_reserved_subdomain(self):
        """Test that reserved subdomains are rejected"""
        from nexo_core.api.provisioning_api import check_subdomain_available

        result = check_subdomain_available("admin")

        self.assertFalse(result["success"])
        self.assertFalse(result["available"])

    def test_get_provisioning_status(self):
        """Test getting provisioning status"""
        from nexo_core.api.provisioning_api import get_provisioning_status

        # Create a test tenant
        tenant = frappe.new_doc("Tenant")
        tenant.tenant_name = "prov_status_test"
        tenant.subdomain = "prov-status-test"
        tenant.company_name = "Prov Status Test"
        tenant.nit = "1234567890120"
        tenant.admin_email = "prov@test.com"
        tenant.admin_password = "password"
        tenant.subscription_plan = "Prov Test Plan"
        tenant.insert(ignore_permissions=True)

        # Get status
        result = get_provisioning_status("prov-status-test")

        self.assertTrue(result["success"])
        self.assertEqual(result["tenant"], "prov-status-test")
        self.assertIn("status", result)
        self.assertIn("site_name", result)

    def test_get_nonexistent_provisioning_status(self):
        """Test getting status for nonexistent tenant"""
        from nexo_core.api.provisioning_api import get_provisioning_status

        result = get_provisioning_status("nonexistent-xyz")

        self.assertFalse(result["success"])

    def test_provision_new_tenant_missing_fields(self):
        """Test provisioning with missing required fields"""
        from nexo_core.api.provisioning_api import provision_new_tenant

        data = {
            "tenant_name": "incomplete",
            # Missing other required fields
        }

        result = provision_new_tenant(json.dumps(data))

        self.assertFalse(result["success"])
        self.assertIn("errors", result)

    def test_provision_new_tenant_invalid_plan(self):
        """Test provisioning with invalid plan"""
        from nexo_core.api.provisioning_api import provision_new_tenant

        data = {
            "tenant_name": "invalid_plan_test",
            "subdomain": "invalid-plan-test",
            "company_name": "Invalid Plan Test",
            "nit": "1234567890121",
            "admin_email": "invalid@test.com",
            "admin_password": "password",
            "subscription_plan": "NonexistentPlan"
        }

        result = provision_new_tenant(json.dumps(data))

        self.assertFalse(result["success"])

    def test_provision_new_tenant_taken_subdomain(self):
        """Test provisioning with taken subdomain"""
        from nexo_core.api.provisioning_api import provision_new_tenant

        # Create first tenant
        tenant1 = frappe.new_doc("Tenant")
        tenant1.tenant_name = "first_tenant"
        tenant1.subdomain = "taken-domain"
        tenant1.company_name = "First"
        tenant1.nit = "1234567890122"
        tenant1.admin_email = "first@test.com"
        tenant1.admin_password = "password"
        tenant1.subscription_plan = "Prov Test Plan"
        tenant1.insert(ignore_permissions=True)

        # Try to create another with same subdomain
        data = {
            "tenant_name": "second_tenant",
            "subdomain": "taken-domain",
            "company_name": "Second",
            "nit": "1234567890123",
            "admin_email": "second@test.com",
            "admin_password": "password",
            "subscription_plan": "Prov Test Plan"
        }

        result = provision_new_tenant(json.dumps(data))

        self.assertFalse(result["success"])

    def test_retry_provisioning(self):
        """Test retrying provisioning for a tenant"""
        from nexo_core.api.provisioning_api import retry_provisioning

        # Create a test tenant
        tenant = frappe.new_doc("Tenant")
        tenant.tenant_name = "retry_test"
        tenant.subdomain = "retry-test"
        tenant.company_name = "Retry Test"
        tenant.nit = "1234567890124"
        tenant.admin_email = "retry@test.com"
        tenant.admin_password = "password"
        tenant.subscription_plan = "Prov Test Plan"
        tenant.insert(ignore_permissions=True)

        # Retry provisioning
        result = retry_provisioning("retry-test")

        self.assertTrue(result["success"])

    def test_retry_nonexistent_tenant(self):
        """Test retrying provisioning for nonexistent tenant"""
        from nexo_core.api.provisioning_api import retry_provisioning

        result = retry_provisioning("nonexistent-xyz")

        self.assertFalse(result["success"])

    def tearDown(self):
        """Clean up test data"""
        tenants = frappe.db.get_list("Tenant", filters={"tenant_name": ["like", "%_test"]})
        for tenant in tenants:
            try:
                frappe.db.delete("Tenant", tenant.name, ignore_permissions=True)
            except Exception:
                pass

        frappe.db.commit()
