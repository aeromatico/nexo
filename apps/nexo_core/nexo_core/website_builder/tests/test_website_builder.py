# Copyright (c) 2025, Aero and contributors
# For license information, please see license.txt

import frappe
import unittest
from nexo_core.website_builder.page_builder import (
	create_page, update_page, publish_page, unpublish_page,
	render_page, get_pages
)
from nexo_core.website_builder.templates import get_templates, get_template_content


class TestPageBuilder(unittest.TestCase):
	"""Test page builder functionality"""

	def setUp(self):
		"""Setup test data"""
		# Clean up test pages
		test_pages = frappe.db.get_list("Website Page", filters={"page_name": ["like", "test%"]})
		for page in test_pages:
			try:
				frappe.delete_doc("Website Page", page.name, force=1, ignore_permissions=True)
			except Exception:
				pass

	def test_create_page(self):
		"""Test creating page"""
		result = create_page(
			page_name="test-home",
			route="/test-home",
			title="Test Home Page",
			content="<h1>Welcome</h1>",
			template="Custom",
		)

		self.assertEqual(result.get("status"), "success")
		self.assertIn("page_id", result)

	def test_create_page_with_seo(self):
		"""Test creating page with SEO"""
		result = create_page(
			page_name="test-seo",
			route="/test-seo",
			title="Test SEO Page",
			content="<h1>SEO Page</h1>",
			template="Custom",
			seo_title="Test SEO Title",
			seo_description="Test SEO description",
			seo_keywords="test, seo, keywords",
		)

		self.assertEqual(result.get("status"), "success")

	def test_create_page_missing_required_field(self):
		"""Test creating page with missing field"""
		result = create_page(
			page_name="",  # Missing page name
			route="/test",
			title="Test",
			content="<h1>Test</h1>",
		)

		self.assertEqual(result.get("status"), "error")

	def test_update_page(self):
		"""Test updating page"""
		# Create page first
		create_result = create_page(
			page_name="test-update",
			route="/test-update",
			title="Original Title",
			content="<h1>Original</h1>",
		)

		page_id = create_result.get("page_id")

		# Update page
		result = update_page(
			page_name=page_id,
			title="Updated Title",
			content="<h1>Updated</h1>",
		)

		self.assertEqual(result.get("status"), "success")

	def test_publish_page(self):
		"""Test publishing page"""
		# Create page
		create_result = create_page(
			page_name="test-publish",
			route="/test-publish",
			title="Publish Test",
			content="<h1>Test</h1>",
		)

		page_id = create_result.get("page_id")

		# Publish page
		result = publish_page(page_id)

		self.assertEqual(result.get("status"), "success")

	def test_unpublish_page(self):
		"""Test unpublishing page"""
		# Create and publish page
		create_result = create_page(
			page_name="test-unpublish",
			route="/test-unpublish",
			title="Unpublish Test",
			content="<h1>Test</h1>",
		)

		page_id = create_result.get("page_id")

		publish_page(page_id)

		# Unpublish
		result = unpublish_page(page_id)

		self.assertEqual(result.get("status"), "success")

	def test_get_pages(self):
		"""Test getting pages"""
		# Create a page
		create_page(
			page_name="test-list",
			route="/test-list",
			title="List Test",
			content="<h1>Test</h1>",
		)

		result = get_pages()

		self.assertEqual(result.get("status"), "success")
		self.assertIn("pages", result)

	def test_render_page(self):
		"""Test rendering page"""
		# Create and publish page
		create_result = create_page(
			page_name="test-render",
			route="/test-render",
			title="Render Test",
			content="<h1>Hello World</h1>",
		)

		page_id = create_result.get("page_id")
		publish_page(page_id)

		# Render page
		result = render_page("/test-render")

		self.assertEqual(result.get("status"), "success")
		self.assertIn("page", result)

	def test_render_unpublished_page(self):
		"""Test rendering unpublished page"""
		result = render_page("/nonexistent-page")

		self.assertEqual(result.get("status"), "error")


class TestTemplates(unittest.TestCase):
	"""Test template functionality"""

	def test_get_templates(self):
		"""Test getting templates"""
		result = get_templates()

		self.assertEqual(result.get("status"), "success")
		templates = result.get("templates", [])
		self.assertGreater(len(templates), 0)

	def test_get_template_content(self):
		"""Test getting template content"""
		result = get_template_content("home")

		self.assertEqual(result.get("status"), "success")
		template = result.get("template", {})
		self.assertEqual(template.get("id"), "home")
		self.assertIn("content", template)

	def test_get_invalid_template(self):
		"""Test getting non-existent template"""
		result = get_template_content("nonexistent")

		self.assertEqual(result.get("status"), "error")

	def test_all_templates_have_content(self):
		"""Test that all templates have content"""
		result = get_templates()

		self.assertEqual(result.get("status"), "success")
		templates = result.get("templates", [])

		for template in templates:
			template_id = template.get("id")
			content_result = get_template_content(template_id)
			self.assertEqual(content_result.get("status"), "success")
			self.assertIn("content", content_result.get("template", {}))


if __name__ == "__main__":
	unittest.main()
