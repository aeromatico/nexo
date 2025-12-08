"""
Nexo Core - Daily Tasks
Tasks that run once per day
"""

import frappe


def cleanup_expired_sessions():
    """Clean up expired user sessions"""
    frappe.db.sql("""
        DELETE FROM `tabSessions`
        WHERE lastupdate < DATE_SUB(NOW(), INTERVAL 7 DAY)
    """)
    frappe.db.commit()


def update_tenant_metrics():
    """Update tenant usage metrics and analytics"""
    # TODO: Implement tenant metrics update
    # - Calculate storage usage
    # - Count active users
    # - Update billing metrics
    pass
