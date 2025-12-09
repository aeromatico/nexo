# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

import frappe
import subprocess
from frappe import _


def install_apps_on_site(site_name, apps_list):
    """
    Install multiple apps on a site

    Args:
        site_name: Name of the site
        apps_list: List of app names to install

    Returns:
        dict: Installation results for each app
    """
    results = {}

    for app in apps_list:
        try:
            frappe.logger().info(f"Installing app {app} on {site_name}")

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

            if result.returncode == 0:
                results[app] = {
                    "success": True,
                    "message": f"App {app} installed successfully"
                }
                frappe.logger().info(f"Successfully installed {app}")
            else:
                error_msg = result.stderr or result.stdout
                results[app] = {
                    "success": False,
                    "message": f"Error installing {app}: {error_msg}"
                }
                frappe.logger().warning(f"Error installing {app}: {error_msg}")

        except subprocess.TimeoutExpired:
            results[app] = {
                "success": False,
                "message": f"Timeout installing {app}"
            }
        except Exception as e:
            results[app] = {
                "success": False,
                "message": f"Exception installing {app}: {str(e)}"
            }

    return results


def configure_apps(site_name, config):
    """
    Configure apps after installation

    Args:
        site_name: Name of the site
        config: Configuration dictionary

    Returns:
        bool: True if configuration was successful
    """
    try:
        frappe.logger().info(f"Configuring apps on {site_name}")

        # TODO: Configure apps based on config dictionary
        # This could involve:
        # 1. Setting system settings
        # 2. Creating initial documents
        # 3. Enabling features
        # 4. Setting permissions

        return True

    except Exception as e:
        frappe.logger().error(f"Error configuring apps: {str(e)}")
        return False


def uninstall_app(site_name, app_name):
    """
    Uninstall an app from a site

    Args:
        site_name: Name of the site
        app_name: Name of the app to uninstall

    Returns:
        bool: True if successful
    """
    try:
        frappe.logger().info(f"Uninstalling {app_name} from {site_name}")

        cmd = [
            "bench",
            "--site",
            site_name,
            "uninstall-app",
            app_name,
            "--force"
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600
        )

        if result.returncode == 0:
            frappe.logger().info(f"Successfully uninstalled {app_name}")
            return True
        else:
            error_msg = result.stderr or result.stdout
            frappe.logger().warning(f"Error uninstalling {app_name}: {error_msg}")
            return False

    except Exception as e:
        frappe.logger().error(f"Error uninstalling app: {str(e)}")
        return False


def get_installed_apps(site_name):
    """
    Get list of installed apps on a site

    Args:
        site_name: Name of the site

    Returns:
        list: List of installed app names
    """
    try:
        frappe.logger().info(f"Getting installed apps for {site_name}")

        cmd = [
            "bench",
            "--site",
            site_name,
            "list-apps"
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            apps = result.stdout.strip().split('\n')
            return [app.strip() for app in apps if app.strip()]
        else:
            frappe.logger().warning(f"Error getting installed apps: {result.stderr}")
            return []

    except Exception as e:
        frappe.logger().error(f"Error getting installed apps: {str(e)}")
        return []
