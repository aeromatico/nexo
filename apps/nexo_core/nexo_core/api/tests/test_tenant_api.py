# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

import frappe
import unittest
import json


class TestTenantAPI(unittest.TestCase):
    """Test cases for Tenant API endpoints"""

    def setUp(self):
        """Setup test data"""
        # Create test subscription plan
        if not frappe.db.exists("Subscription Plan", "API Test Plan"):
            plan = frappe.new_doc("Subscription Plan")
            plan.plan_name = "API Test Plan"
            plan.max_users = 10
            plan.max_storage_gb = 5.0
            plan.max_sites = 1
            plan.price_monthly = 50
            plan.currency = "BOB"
            plan.is_active = 1
            plan.insert(ignore_permissions=True)

    def test_get_available_plans(self):
        """Test getting available subscription plans"""
        from nexo_core.api.tenant_api import get_available_plans

        result = get_available_plans()

        self.assertTrue(result["success"])
        self.assertGreaterEqual(result["count"], 0)
        self.assertIsInstance(result["plans"], list)

    def test_check_subdomain_available(self):
        """Test checking subdomain availability"""
        from nexo_core.api.tenant_api import check_subdomain_available

        result = check_subdomain_available("unique-subdomain-12345")

        self.assertTrue(result["success"])
        self.assertIn("available", result)

    def test_check_subdomain_taken(self):
        """Test that taken subdomains are not available"""
        from nexo_core.api.tenant_api import check_subdomain_available

        # Create a tenant first
        tenant = frappe.new_doc("Tenant")
        tenant.tenant_name = "api_taken_test"
        tenant.subdomain = "api-taken-test"
        tenant.company_name = "API Taken Test"
        tenant.nit = "1234567890111"
        tenant.admin_email = "api@test.com"
        tenant.admin_password = "password"
        tenant.subscription_plan = "API Test Plan"
        tenant.insert(ignore_permissions=True)

        # Check if taken
        result = check_subdomain_available("api-taken-test")

        self.assertTrue(result["success"])
        self.assertFalse(result["available"])

    def test_check_invalid_subdomain(self):
        """Test that invalid subdomains are rejected"""
        from nexo_core.api.tenant_api import check_subdomain_available

        result = check_subdomain_available("invalid spaces")

        self.assertFalse(result["success"])
        self.assertFalse(result["available"])

    def test_get_tenant_info(self):
        """Test getting tenant information"""
        from nexo_core.api.tenant_api import get_tenant_info

        # Create a test tenant
        tenant = frappe.new_doc("Tenant")
        tenant.tenant_name = "api_info_test"
        tenant.subdomain = "api-info-test"
        tenant.company_name = "API Info Test"
        tenant.nit = "1234567890112"
        tenant.admin_email = "info@test.com"
        tenant.admin_password = "password"
        tenant.subscription_plan = "API Test Plan"
        tenant.insert(ignore_permissions=True)

        # Get info
        result = get_tenant_info("api-info-test")

        self.assertTrue(result["success"])
        self.assertEqual(result["tenant"]["name"], "api-info-test")
        self.assertEqual(result["tenant"]["status"], "Trial")

    def test_get_nonexistent_tenant_info(self):
        """Test getting info for nonexistent tenant"""
        from nexo_core.api.tenant_api import get_tenant_info

        result = get_tenant_info("nonexistent-tenant-xyz")

        self.assertFalse(result["success"])

    def test_get_all_tenants(self):
        """Test getting all tenants"""
        from nexo_core.api.tenant_api import get_all_tenants

        result = get_all_tenants()

        self.assertTrue(result["success"])
        self.assertGreaterEqual(result["count"], 0)
        self.assertIsInstance(result["tenants"], list)

    def test_get_all_tenants_with_filters(self):
        """Test getting tenants with filters"""
        from nexo_core.api.tenant_api import get_all_tenants

        filters = json.dumps({"status": "Trial"})
        result = get_all_tenants(filters=filters)

        self.assertTrue(result["success"])
        self.assertIsInstance(result["tenants"], list)

    def test_get_tenant_metrics(self):
        """Test getting tenant metrics"""
        from nexo_core.api.tenant_api import get_tenant_metrics

        # Create a test tenant
        tenant = frappe.new_doc("Tenant")
        tenant.tenant_name = "api_metrics_test"
        tenant.subdomain = "api-metrics-test"
        tenant.company_name = "API Metrics Test"
        tenant.nit = "1234567890113"
        tenant.admin_email = "metrics@test.com"
        tenant.admin_password = "password"
        tenant.subscription_plan = "API Test Plan"
        tenant.insert(ignore_permissions=True)

        # Get metrics
        result = get_tenant_metrics("api-metrics-test")

        self.assertTrue(result["success"])
        self.assertEqual(result["tenant"], "api-metrics-test")
        self.assertIn("metrics", result)
        self.assertIn("quota_status", result)

    def test_upgrade_plan(self):
        """Test upgrading a tenant's plan"""
        from nexo_core.api.tenant_api import upgrade_plan

        # Create test plan
        if not frappe.db.exists("Subscription Plan", "API Upgrade Plan"):
            plan = frappe.new_doc("Subscription Plan")
            plan.plan_name = "API Upgrade Plan"
            plan.max_users = 20
            plan.max_storage_gb = 10.0
            plan.max_sites = 2
            plan.price_monthly = 100
            plan.currency = "BOB"
            plan.is_active = 1
            plan.insert(ignore_permissions=True)

        # Create test tenant
        tenant = frappe.new_doc("Tenant")
        tenant.tenant_name = "api_upgrade_test"
        tenant.subdomain = "api-upgrade-test"
        tenant.company_name = "API Upgrade Test"
        tenant.nit = "1234567890114"
        tenant.admin_email = "upgrade@test.com"
        tenant.admin_password = "password"
        tenant.subscription_plan = "API Test Plan"
        tenant.insert(ignore_permissions=True)

        # Upgrade plan
        result = upgrade_plan("api-upgrade-test", "API Upgrade Plan")

        self.assertTrue(result["success"])
        self.assertEqual(result["tenant"]["subscription_plan"], "API Upgrade Plan")

    def tearDown(self):
        """Clean up test data"""
        tenants = frappe.db.get_list("Tenant", filters={"tenant_name": ["like", "api_%_test"]})
        for tenant in tenants:
            frappe.db.delete("Tenant", tenant.name, ignore_permissions=True)

        plans = frappe.db.get_list("Subscription Plan", filters={"plan_name": ["like", "API%"]})
        for plan in plans:
            frappe.db.delete("Subscription Plan", plan.name, ignore_permissions=True)

        frappe.db.commit()
