# Copyright (c) 2025, Aero and contributors
# For license information, please see license.txt

import frappe


TEMPLATES = {
	"home": {
		"name": "Home",
		"description": "Homepage with hero section, featured products, and testimonials",
		"content": """<section class="hero">
	<div class="hero-content">
		<h1>Welcome to Our Store</h1>
		<p>Discover our amazing products</p>
		<a href="/products" class="btn">Shop Now</a>
	</div>
</section>

<section class="featured-products">
	<h2>Featured Products</h2>
	<div class="products-grid">
		<!-- Featured products will be loaded here -->
	</div>
</section>

<section class="testimonials">
	<h2>What Our Customers Say</h2>
	<div class="testimonials-grid">
		<!-- Testimonials will be displayed here -->
	</div>
</section>""",
	},
	"about": {
		"name": "About Us",
		"description": "About company page template",
		"content": """<div class="about-container">
	<h1>About Us</h1>

	<section class="about-intro">
		<h2>Who We Are</h2>
		<p>Tell your company story here...</p>
	</section>

	<section class="company-values">
		<h2>Our Values</h2>
		<div class="values-grid">
			<div class="value">
				<h3>Quality</h3>
				<p>We deliver the highest quality products</p>
			</div>
			<div class="value">
				<h3>Customer Service</h3>
				<p>Your satisfaction is our priority</p>
			</div>
			<div class="value">
				<h3>Innovation</h3>
				<p>We constantly improve our offerings</p>
			</div>
		</div>
	</section>

	<section class="company-team">
		<h2>Our Team</h2>
		<p>Meet the talented people behind our company...</p>
	</section>
</div>""",
	},
	"contact": {
		"name": "Contact",
		"description": "Contact page with form",
		"content": """<div class="contact-container">
	<h1>Get In Touch</h1>
	<p>Have a question? We'd love to hear from you.</p>

	<div class="contact-content">
		<div class="contact-form">
			<form id="contact-form">
				<div class="form-group">
					<label for="name">Name</label>
					<input type="text" id="name" name="name" required>
				</div>
				<div class="form-group">
					<label for="email">Email</label>
					<input type="email" id="email" name="email" required>
				</div>
				<div class="form-group">
					<label for="message">Message</label>
					<textarea id="message" name="message" rows="5" required></textarea>
				</div>
				<button type="submit" class="btn">Send Message</button>
			</form>
		</div>

		<div class="contact-info">
			<h3>Contact Information</h3>
			<p><strong>Address:</strong> Your address here</p>
			<p><strong>Phone:</strong> Your phone number</p>
			<p><strong>Email:</strong> Your email</p>
			<p><strong>Hours:</strong> Your business hours</p>
		</div>
	</div>
</div>""",
	},
	"products": {
		"name": "Products",
		"description": "Product catalog/listing page",
		"content": """<div class="products-page">
	<h1>Our Products</h1>

	<div class="filters">
		<h3>Filter by Category</h3>
		<!-- Filters will be displayed here -->
	</div>

	<div class="products-grid">
		<!-- Products will be loaded here -->
	</div>

	<div class="pagination">
		<!-- Pagination will be displayed here -->
	</div>
</div>""",
	},
	"blog": {
		"name": "Blog Post",
		"description": "Blog post page template",
		"content": """<article class="blog-post">
	<header class="post-header">
		<h1 class="post-title">Article Title</h1>
		<div class="post-meta">
			<span class="post-author">By Author Name</span>
			<span class="post-date">Published on Date</span>
			<span class="post-category">Category</span>
		</div>
	</header>

	<img class="post-image" src="" alt="Article image">

	<div class="post-content">
		<p>Your blog post content goes here...</p>
	</div>

	<footer class="post-footer">
		<div class="tags">
			<!-- Tags will be displayed here -->
		</div>
		<div class="share">
			<!-- Social sharing buttons -->
		</div>
	</footer>
</article>""",
	},
	"faq": {
		"name": "FAQ",
		"description": "Frequently Asked Questions page",
		"content": """<div class="faq-container">
	<h1>Frequently Asked Questions</h1>
	<p>Find answers to common questions about our products and services.</p>

	<div class="faq-list">
		<div class="faq-item">
			<h3 class="faq-question">How do I place an order?</h3>
			<p class="faq-answer">Explain how customers can place an order...</p>
		</div>

		<div class="faq-item">
			<h3 class="faq-question">What is your return policy?</h3>
			<p class="faq-answer">Describe your return policy...</p>
		</div>

		<div class="faq-item">
			<h3 class="faq-question">How long does shipping take?</h3>
			<p class="faq-answer">Explain shipping times...</p>
		</div>

		<div class="faq-item">
			<h3 class="faq-question">Do you offer discounts?</h3>
			<p class="faq-answer">Explain discount policies...</p>
		</div>
	</div>
</div>""",
	},
}


@frappe.whitelist(allow_guest=True)
def get_templates():
	"""Get available page templates"""
	try:
		template_list = []

		for key, template in TEMPLATES.items():
			template_list.append({
				"id": key,
				"name": template.get("name"),
				"description": template.get("description"),
			})

		return {
			"status": "success",
			"templates": template_list,
		}

	except Exception as e:
		frappe.logger().error(f"Error getting templates: {str(e)}")
		return {
			"status": "error",
			"message": str(e),
		}


@frappe.whitelist(allow_guest=True)
def get_template_content(template_id):
	"""Get template content"""
	try:
		template = TEMPLATES.get(template_id)

		if not template:
			return {
				"status": "error",
				"message": f"Template {template_id} not found",
			}

		return {
			"status": "success",
			"template": {
				"id": template_id,
				"name": template.get("name"),
				"description": template.get("description"),
				"content": template.get("content"),
			},
		}

	except Exception as e:
		frappe.logger().error(f"Error getting template content: {str(e)}")
		return {
			"status": "error",
			"message": str(e),
		}
