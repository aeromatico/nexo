# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

import frappe
import unittest
import json


class TestSubscriptionPlan(unittest.TestCase):
    """Test cases for Subscription Plan DocType"""

    def test_create_basic_plan(self):
        """Test creating a basic subscription plan"""
        plan = frappe.new_doc("Subscription Plan")
        plan.plan_name = "Test Basic"
        plan.max_users = 5
        plan.max_storage_gb = 1.0
        plan.max_sites = 1
        plan.price_monthly = 29
        plan.price_annual = 290
        plan.currency = "BOB"
        plan.is_active = 1

        plan.insert(ignore_permissions=True)

        self.assertEqual(plan.name, "Test Basic")
        self.assertEqual(plan.max_users, 5)
        self.assertEqual(plan.price_monthly, 29)

    def test_plan_validation_negative_price(self):
        """Test that negative prices are rejected"""
        plan = frappe.new_doc("Subscription Plan")
        plan.plan_name = "Invalid Plan"
        plan.max_users = 5
        plan.max_storage_gb = 1.0
        plan.max_sites = 1
        plan.price_monthly = -29
        plan.currency = "BOB"

        self.assertRaises(frappe.ValidationError, plan.insert)

    def test_plan_validation_zero_users(self):
        """Test that max_users must be > 0"""
        plan = frappe.new_doc("Subscription Plan")
        plan.plan_name = "Invalid Plan"
        plan.max_users = 0
        plan.max_storage_gb = 1.0
        plan.max_sites = 1
        plan.price_monthly = 29
        plan.currency = "BOB"

        self.assertRaises(frappe.ValidationError, plan.insert)

    def test_plan_validation_zero_storage(self):
        """Test that max_storage_gb must be > 0"""
        plan = frappe.new_doc("Subscription Plan")
        plan.plan_name = "Invalid Plan"
        plan.max_users = 5
        plan.max_storage_gb = 0
        plan.max_sites = 1
        plan.price_monthly = 29
        plan.currency = "BOB"

        self.assertRaises(frappe.ValidationError, plan.insert)

    def test_plan_with_features(self):
        """Test creating a plan with features JSON"""
        plan = frappe.new_doc("Subscription Plan")
        plan.plan_name = "Featured Plan"
        plan.max_users = 10
        plan.max_storage_gb = 5.0
        plan.max_sites = 2
        plan.price_monthly = 79
        plan.currency = "BOB"
        features = {
            "invoicing": True,
            "inventory": True,
            "payroll": True
        }
        plan.features = json.dumps(features)
        plan.is_active = 1

        plan.insert(ignore_permissions=True)

        retrieved_plan = frappe.get_doc("Subscription Plan", plan.name)
        parsed_features = retrieved_plan.get_features_dict()

        self.assertEqual(parsed_features["invoicing"], True)
        self.assertEqual(parsed_features["inventory"], True)

    def test_get_active_plans(self):
        """Test getting all active plans"""
        # Create test plan
        plan = frappe.new_doc("Subscription Plan")
        plan.plan_name = "Active Test"
        plan.max_users = 5
        plan.max_storage_gb = 1.0
        plan.max_sites = 1
        plan.price_monthly = 29
        plan.currency = "BOB"
        plan.is_active = 1
        plan.insert(ignore_permissions=True)

        active_plans = frappe.get_list(
            "Subscription Plan",
            filters={"is_active": 1},
            fields=["name", "plan_name"]
        )

        plan_names = [p.plan_name for p in active_plans]
        self.assertIn("Active Test", plan_names)

    def test_plan_can_create_tenant(self):
        """Test checking if plan can create tenants"""
        plan = frappe.new_doc("Subscription Plan")
        plan.plan_name = "Tenant Test"
        plan.max_users = 5
        plan.max_storage_gb = 1.0
        plan.max_sites = 1
        plan.price_monthly = 29
        plan.currency = "BOB"
        plan.is_active = 1
        plan.insert(ignore_permissions=True)

        self.assertTrue(plan.can_create_tenant())

    def test_plan_cannot_create_when_inactive(self):
        """Test that inactive plans cannot create tenants"""
        plan = frappe.new_doc("Subscription Plan")
        plan.plan_name = "Inactive Test"
        plan.max_users = 5
        plan.max_storage_gb = 1.0
        plan.max_sites = 1
        plan.price_monthly = 29
        plan.currency = "BOB"
        plan.is_active = 0
        plan.insert(ignore_permissions=True)

        self.assertFalse(plan.can_create_tenant())

    def tearDown(self):
        """Clean up test data"""
        plans = frappe.db.get_list("Subscription Plan", filters={"plan_name": ["like", "%Test%"]})
        for plan in plans:
            frappe.db.delete("Subscription Plan", plan.name, ignore_permissions=True)
        frappe.db.commit()
