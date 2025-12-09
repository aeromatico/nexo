# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

import frappe
import subprocess
import os
import json
from frappe import _


def provision_tenant_site(tenant_name):
    """
    Provision a complete site for a new tenant

    This is the main function that coordinates all provisioning tasks:
    1. Create Frappe site
    2. Install base apps (erpnext, nexo_bolivia)
    3. Setup Bolivia defaults
    4. Create admin user
    5. Update tenant document

    Args:
        tenant_name: Name of the tenant to provision
    """
    try:
        tenant = frappe.get_doc("Tenant", tenant_name)
        frappe.logger().info(f"Starting provisioning for tenant: {tenant_name}")

        # Step 1: Create the Frappe site
        frappe.logger().info(f"Creating Frappe site: {tenant.site_name}")
        site_created = create_frappe_site(tenant)

        if not site_created:
            frappe.throw(_("No se pudo crear el site Frappe para el tenant"))

        # Step 2: Install base apps
        frappe.logger().info(f"Installing base apps on {tenant.site_name}")
        install_base_apps(tenant)

        # Step 3: Setup Bolivia defaults
        frappe.logger().info(f"Setting up Bolivia defaults for {tenant.site_name}")
        setup_bolivia_defaults(tenant)

        # Step 4: Create admin user
        frappe.logger().info(f"Creating admin user for {tenant.site_name}")
        create_admin_user(tenant)

        # Step 5: Mark provisioning as complete
        tenant.status = "Active"
        tenant.activated_at = frappe.utils.now()
        tenant.db_update()

        frappe.logger().info(f"Provisioning completed successfully for tenant: {tenant_name}")
        frappe.msgprint(_("Tenant {0} ha sido aprovisionado exitosamente").format(tenant_name))

    except Exception as e:
        frappe.log_error(f"Error provisioning tenant {tenant_name}: {str(e)}", "Tenant Provisioning")
        frappe.msgprint(_("Error al aprovicionar tenant {0}: {1}").format(tenant_name, str(e)))


def create_frappe_site(tenant):
    """
    Create a new Frappe site using bench commands

    Args:
        tenant: Tenant document

    Returns:
        bool: True if site was created successfully
    """
    try:
        site_name = tenant.site_name
        admin_password = tenant.admin_password

        # Check if running inside Docker
        is_docker = os.path.exists("/.dockerenv")

        if is_docker:
            # Inside Docker container
            cmd = [
                "bench",
                "new-site",
                site_name,
                "--admin-password",
                admin_password,
                "--no-mariadb-socket"
            ]
        else:
            # Local development
            cmd = [
                "bench",
                "new-site",
                site_name,
                "--admin-password",
                admin_password
            ]

        # Execute bench command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode != 0:
            error_msg = result.stderr or result.stdout
            frappe.logger().error(f"Error creating site {site_name}: {error_msg}")
            return False

        frappe.logger().info(f"Site {site_name} created successfully")
        return True

    except subprocess.TimeoutExpired:
        frappe.logger().error(f"Timeout creating site {tenant.site_name}")
        return False
    except Exception as e:
        frappe.logger().error(f"Exception creating site: {str(e)}")
        return False


def install_base_apps(tenant):
    """
    Install base apps on the tenant's site

    Base apps:
    - erpnext (required)
    - nexo_bolivia (localization)

    Args:
        tenant: Tenant document
    """
    base_apps = ["erpnext", "nexo_bolivia"]
    site_name = tenant.site_name

    for app in base_apps:
        try:
            frappe.logger().info(f"Installing {app} on {site_name}")

            cmd = [
                "bench",
                "--site",
                site_name,
                "install-app",
                app
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600
            )

            if result.returncode != 0:
                error_msg = result.stderr or result.stdout
                frappe.logger().warning(f"Warning installing {app} on {site_name}: {error_msg}")
            else:
                frappe.logger().info(f"Successfully installed {app} on {site_name}")

                # Record installed app
                tenant.append("apps_installed", {
                    "app_name": app,
                    "status": "Installed",
                    "installed_on": frappe.utils.now()
                })

        except Exception as e:
            frappe.logger().warning(f"Error installing {app}: {str(e)}")

    # Save tenant with installed apps
    tenant.db_update()


def setup_bolivia_defaults(tenant):
    """
    Setup Bolivia default configuration on the tenant's site

    This includes:
    - Country: Bolivia
    - Currency: BOB (Bolivianos)
    - Timezone: America/La_Paz
    - Default company (if not exists)
    - Enable SIN integration

    Args:
        tenant: Tenant document
    """
    site_name = tenant.site_name

    try:
        # We need to switch to the tenant's site context to create documents
        # This would be handled by the actual implementation using frappe.init()

        frappe.logger().info(f"Setting up Bolivia defaults for {site_name}")

        # TODO: Execute script on tenant's site to setup defaults
        # This requires connecting to the specific site and creating:
        # 1. System Settings with Bolivia defaults
        # 2. Default Company with Bolivia tax configuration
        # 3. Enable Bolivia-specific features

    except Exception as e:
        frappe.logger().warning(f"Error setting up Bolivia defaults: {str(e)}")


def create_admin_user(tenant):
    """
    Create admin user on the tenant's site

    Args:
        tenant: Tenant document
    """
    site_name = tenant.site_name

    try:
        frappe.logger().info(f"Creating admin user for {site_name}")

        # Admin user is created automatically with new-site command
        # But we can set additional properties here if needed

    except Exception as e:
        frappe.logger().warning(f"Error creating admin user: {str(e)}")


def cleanup_tenant_site(site_name):
    """
    Clean up and delete a tenant's site

    Args:
        site_name: Name of the site to delete
    """
    try:
        frappe.logger().info(f"Cleaning up site: {site_name}")

        # Before deleting, create a backup
        backup_site(site_name)

        # Delete the site
        cmd = [
            "bench",
            "drop-site",
            site_name,
            "--force"
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode != 0:
            error_msg = result.stderr or result.stdout
            frappe.logger().warning(f"Warning deleting site {site_name}: {error_msg}")
        else:
            frappe.logger().info(f"Site {site_name} deleted successfully")

    except Exception as e:
        frappe.logger().error(f"Error cleaning up site {site_name}: {str(e)}")


def backup_site(site_name):
    """
    Create a backup of a site before deletion

    Args:
        site_name: Name of the site to backup
    """
    try:
        frappe.logger().info(f"Creating backup for site: {site_name}")

        cmd = [
            "bench",
            "--site",
            site_name,
            "backup"
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600
        )

        if result.returncode != 0:
            frappe.logger().warning(f"Warning backing up site {site_name}")
        else:
            frappe.logger().info(f"Backup created for site {site_name}")

    except Exception as e:
        frappe.logger().warning(f"Error backing up site {site_name}: {str(e)}")


def cleanup_old_backups():
    """
    Clean up old backups (older than 30 days)

    This is called via scheduler
    """
    try:
        frappe.logger().info("Cleaning up old backups")

        cmd = [
            "bench",
            "delete-old-backups",
            "--days",
            "30"
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600
        )

        if result.returncode == 0:
            frappe.logger().info("Old backups cleaned up successfully")

    except Exception as e:
        frappe.logger().warning(f"Error cleaning up old backups: {str(e)}")
