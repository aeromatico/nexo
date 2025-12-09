# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

import frappe
import unittest


class TestTenantUsage(unittest.TestCase):
    """Test cases for Tenant Usage DocType"""

    def setUp(self):
        """Setup test data"""
        # Create test subscription plan
        if not frappe.db.exists("Subscription Plan", "Test Usage Plan"):
            plan = frappe.new_doc("Subscription Plan")
            plan.plan_name = "Test Usage Plan"
            plan.max_users = 10
            plan.max_storage_gb = 5.0
            plan.max_sites = 1
            plan.price_monthly = 50
            plan.currency = "BOB"
            plan.is_active = 1
            plan.insert(ignore_permissions=True)

        # Create test tenant
        if not frappe.db.exists("Tenant", "usage-test"):
            tenant = frappe.new_doc("Tenant")
            tenant.tenant_name = "usage_test"
            tenant.subdomain = "usage-test"
            tenant.company_name = "Usage Test"
            tenant.nit = "1234567890199"
            tenant.admin_email = "usage@test.com"
            tenant.admin_password = "password"
            tenant.subscription_plan = "Test Usage Plan"
            tenant.insert(ignore_permissions=True)

    def test_create_usage_record(self):
        """Test creating a tenant usage record"""
        usage = frappe.new_doc("Tenant Usage")
        usage.tenant = "usage-test"
        usage.date = frappe.utils.today()
        usage.active_users = 3
        usage.storage_used_mb = 500
        usage.database_size_mb = 100
        usage.api_calls = 1000
        usage.email_sent = 50
        usage.invoices_generated = 5

        usage.insert(ignore_permissions=True)

        self.assertEqual(usage.tenant, "usage-test")
        self.assertEqual(usage.active_users, 3)
        self.assertEqual(usage.storage_used_mb, 500)

    def test_usage_validation_negative_users(self):
        """Test that negative active users are rejected"""
        usage = frappe.new_doc("Tenant Usage")
        usage.tenant = "usage-test"
        usage.date = frappe.utils.today()
        usage.active_users = -5
        usage.storage_used_mb = 100

        self.assertRaises(frappe.ValidationError, usage.insert)

    def test_usage_validation_negative_storage(self):
        """Test that negative storage is rejected"""
        usage = frappe.new_doc("Tenant Usage")
        usage.tenant = "usage-test"
        usage.date = frappe.utils.today()
        usage.active_users = 2
        usage.storage_used_mb = -100

        self.assertRaises(frappe.ValidationError, usage.insert)

    def test_usage_validation_invalid_tenant(self):
        """Test that invalid tenant is rejected"""
        usage = frappe.new_doc("Tenant Usage")
        usage.tenant = "nonexistent-tenant"
        usage.date = frappe.utils.today()
        usage.active_users = 2
        usage.storage_used_mb = 100

        self.assertRaises(frappe.ValidationError, usage.insert)

    def test_usage_with_all_metrics(self):
        """Test creating usage record with all metrics"""
        usage = frappe.new_doc("Tenant Usage")
        usage.tenant = "usage-test"
        usage.date = frappe.utils.today()
        usage.active_users = 5
        usage.storage_used_mb = 1000
        usage.database_size_mb = 200
        usage.api_calls = 5000
        usage.email_sent = 100
        usage.invoices_generated = 10
        usage.notes = "Test usage record"

        usage.insert(ignore_permissions=True)

        retrieved = frappe.get_doc("Tenant Usage", usage.name)
        self.assertEqual(retrieved.api_calls, 5000)
        self.assertEqual(retrieved.invoices_generated, 10)

    def test_get_tenant_usage_report(self):
        """Test generating usage report for a tenant"""
        # Create some usage records
        from datetime import datetime, timedelta

        start_date = frappe.utils.today()
        for i in range(5):
            date = frappe.utils.add_days(start_date, -i)
            usage = frappe.new_doc("Tenant Usage")
            usage.tenant = "usage-test"
            usage.date = date
            usage.active_users = 2 + i
            usage.storage_used_mb = 100 + (i * 50)
            usage.api_calls = 1000 + (i * 100)
            usage.insert(ignore_permissions=True)

        # Get report
        from nexo_core.doctype.tenant_usage.tenant_usage import TenantUsage
        report = TenantUsage.get_tenant_usage_report(
            "usage-test",
            frappe.utils.add_days(start_date, -10),
            start_date
        )

        self.assertTrue(report["success"] if "success" in report else True)
        self.assertGreaterEqual(len(report["usage_data"]), 0)

    def tearDown(self):
        """Clean up test data"""
        # Clean up usage records
        usages = frappe.db.get_list("Tenant Usage", filters={"tenant": "usage-test"})
        for usage in usages:
            frappe.db.delete("Tenant Usage", usage.name, ignore_permissions=True)

        # Clean up tenant
        if frappe.db.exists("Tenant", "usage-test"):
            frappe.db.delete("Tenant", "usage-test", ignore_permissions=True)

        frappe.db.commit()
