"""
Integración con Google Drive para backup automático

Sistema de respaldo en la nube de Google Drive
"""

import frappe
from frappe import _
import requests
import json
import base64


class GoogleDriveBackup:
    """Gestor de backups en Google Drive"""

    def __init__(self):
        self.api_key = self._get_config('google_drive_api_key')
        self.folder_id = self._get_config('google_drive_folder_id')
        self.base_url = "https://www.googleapis.com/drive/v3"

        if not self.api_key:
            frappe.throw(_("Google Drive configuration not found"))

    def _get_config(self, key):
        """Obtiene configuración"""
        try:
            config = frappe.get_single('Integration Config')
            return config.get(key)
        except frappe.DoesNotExistError:
            return None

    def upload_backup(self, backup_name, backup_data):
        """
        Sube backup a Google Drive

        Args:
            backup_name: Nombre del backup
            backup_data: Datos del backup (bytes)

        Returns:
            dict: ID del archivo en Google Drive
        """
        url = f"{self.base_url}/files?uploadType=multipart"
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

        metadata = {
            'name': backup_name,
            'parents': [self.folder_id] if self.folder_id else [],
            'mimeType': 'application/gzip'
        }

        files = {
            'data': ('metadata', json.dumps(metadata), 'application/json'),
            'file': ('file', backup_data, 'application/gzip')
        }

        try:
            response = requests.post(url, files=files, headers=headers)

            if response.status_code == 200:
                data = response.json()
                self._log_backup('uploaded', data['id'], backup_name)
                return {
                    'success': True,
                    'file_id': data['id'],
                    'name': data['name']
                }
            else:
                frappe.log_error(f"Google Drive Error: {response.text}", "Backup Upload Failed")
                return {'success': False, 'error': response.text}

        except requests.RequestException as e:
            frappe.log_error(str(e), "Google Drive Connection Error")
            return {'success': False, 'error': str(e)}

    def list_backups(self):
        """
        Lista backups en Google Drive

        Returns:
            dict: Lista de archivos
        """
        url = f"{self.base_url}/files"
        params = {
            'q': f"'{self.folder_id}' in parents and trashed=false" if self.folder_id else "trashed=false"
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}

        try:
            response = requests.get(url, params=params, headers=headers)

            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'files': [
                        {
                            'id': f['id'],
                            'name': f['name'],
                            'size': f.get('size'),
                            'created_time': f.get('createdTime')
                        }
                        for f in data.get('files', [])
                    ]
                }
            else:
                return {'success': False, 'error': response.text}

        except requests.RequestException as e:
            return {'success': False, 'error': str(e)}

    def delete_backup(self, file_id):
        """
        Elimina backup de Google Drive

        Args:
            file_id: ID del archivo

        Returns:
            dict: Resultado
        """
        url = f"{self.base_url}/files/{file_id}"
        headers = {"Authorization": f"Bearer {self.api_key}"}

        try:
            response = requests.delete(url, headers=headers)

            if response.status_code == 204:
                self._log_backup('deleted', file_id, 'Unknown')
                return {'success': True}
            else:
                return {'success': False, 'error': response.text}

        except requests.RequestException as e:
            return {'success': False, 'error': str(e)}

    def _log_backup(self, status, file_id, name):
        """Registra backup en log"""
        try:
            frappe.get_doc({
                'doctype': 'Integration Log',
                'integration': 'Google Drive',
                'status': status,
                'transaction_id': file_id,
                'content': name
            }).insert(ignore_permissions=True)
            frappe.db.commit()
        except Exception as e:
            frappe.log_error(str(e), "Failed to log Google Drive backup")


@frappe.whitelist()
def create_google_drive_backup(backup_name=None):
    """
    API endpoint: Crea backup en Google Drive

    Args:
        backup_name: Nombre personalizado del backup

    Returns:
        dict: Resultado
    """
    try:
        from frappe.utils import now
        import gzip
        import io

        # Generar backup
        backup_name = backup_name or f"nexo_backup_{now().strftime('%Y%m%d_%H%M%S')}.sql.gz"

        # Aquí iría la lógica de generar dump de BD
        # Por ahora es un stub
        backup_data = b"Database backup content"

        backup = GoogleDriveBackup()
        result = backup.upload_backup(backup_name, backup_data)

        return result
    except Exception as e:
        frappe.log_error(str(e), "Google Drive Backup Error")
        return {'success': False, 'error': str(e)}


@frappe.whitelist()
def list_google_drive_backups():
    """
    API endpoint: Lista backups en Google Drive

    Returns:
        dict: Lista de backups
    """
    try:
        backup = GoogleDriveBackup()
        result = backup.list_backups()
        return result
    except Exception as e:
        frappe.log_error(str(e), "Google Drive List Error")
        return {'success': False, 'error': str(e)}
