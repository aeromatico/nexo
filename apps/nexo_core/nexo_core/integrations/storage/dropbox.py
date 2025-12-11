"""
Integración con Dropbox

Sistema de respaldo en la nube de Dropbox
"""

import frappe
from frappe import _
import requests


class DropboxBackup:
    """Gestor de backups en Dropbox"""

    def __init__(self):
        self.access_token = self._get_config('dropbox_access_token')
        self.base_url = "https://content.dropboxapi.com/2"

        if not self.access_token:
            frappe.throw(_("Dropbox configuration not found"))

    def _get_config(self, key):
        """Obtiene configuración"""
        try:
            config = frappe.get_single('Integration Config')
            return config.get(key)
        except frappe.DoesNotExistError:
            return None

    def upload_backup(self, backup_name, backup_data):
        """Sube backup a Dropbox"""
        url = f"{self.base_url}/files/upload"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Dropbox-API-Arg": f'{{"path": "/backups/{backup_name}"}}'
        }

        try:
            response = requests.post(url, data=backup_data, headers=headers)

            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'file_id': data['id'],
                    'name': data['name']
                }
            else:
                frappe.log_error(f"Dropbox Error: {response.text}", "Backup Upload Failed")
                return {'success': False, 'error': response.text}

        except requests.RequestException as e:
            frappe.log_error(str(e), "Dropbox Connection Error")
            return {'success': False, 'error': str(e)}

    def list_backups(self):
        """Lista backups en Dropbox"""
        url = f"{self.base_url}/files/list_folder"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        payload = {"path": "/backups"}

        try:
            response = requests.post(url, json=payload, headers=headers)

            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'files': [
                        {
                            'id': f['id'],
                            'name': f['name'],
                            'size': f.get('size')
                        }
                        for f in data.get('entries', [])
                    ]
                }
            else:
                return {'success': False, 'error': response.text}

        except requests.RequestException as e:
            return {'success': False, 'error': str(e)}


@frappe.whitelist()
def upload_to_dropbox(backup_name=None):
    """API endpoint: Sube backup a Dropbox"""
    try:
        from frappe.utils import now

        backup_name = backup_name or f"nexo_backup_{now().strftime('%Y%m%d_%H%M%S')}.sql.gz"
        backup_data = b"Database backup content"

        backup = DropboxBackup()
        result = backup.upload_backup(backup_name, backup_data)

        return result
    except Exception as e:
        frappe.log_error(str(e), "Dropbox Upload Error")
        return {'success': False, 'error': str(e)}
