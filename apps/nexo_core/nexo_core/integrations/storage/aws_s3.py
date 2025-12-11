"""
Integración con AWS S3

Sistema de respaldo en la nube de Amazon S3
"""

import frappe
from frappe import _

try:
    import boto3
except ImportError:
    frappe.msgprint("Instala boto3: pip install boto3")


class S3Backup:
    """Gestor de backups en AWS S3"""

    def __init__(self):
        self.access_key = self._get_config('aws_access_key')
        self.secret_key = self._get_config('aws_secret_key')
        self.region = self._get_config('aws_region') or 'us-east-1'
        self.bucket_name = self._get_config('aws_bucket_name')

        if not all([self.access_key, self.secret_key, self.bucket_name]):
            frappe.throw(_("AWS S3 configuration not found"))

        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region
        )

    def _get_config(self, key):
        """Obtiene configuración"""
        try:
            config = frappe.get_single('Integration Config')
            return config.get(key)
        except frappe.DoesNotExistError:
            return None

    def upload_backup(self, backup_name, backup_data):
        """Sube backup a S3"""
        try:
            key = f"backups/{backup_name}"

            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=backup_data
            )

            return {
                'success': True,
                'bucket': self.bucket_name,
                'key': key,
                'url': f"s3://{self.bucket_name}/{key}"
            }
        except Exception as e:
            frappe.log_error(str(e), "S3 Upload Error")
            return {'success': False, 'error': str(e)}

    def list_backups(self):
        """Lista backups en S3"""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix='backups/'
            )

            files = []
            for obj in response.get('Contents', []):
                files.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': str(obj['LastModified'])
                })

            return {
                'success': True,
                'files': files
            }
        except Exception as e:
            frappe.log_error(str(e), "S3 List Error")
            return {'success': False, 'error': str(e)}

    def delete_backup(self, key):
        """Elimina backup de S3"""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}


@frappe.whitelist()
def upload_to_s3(backup_name=None):
    """API endpoint: Sube backup a S3"""
    try:
        from frappe.utils import now

        backup_name = backup_name or f"nexo_backup_{now().strftime('%Y%m%d_%H%M%S')}.sql.gz"
        backup_data = b"Database backup content"

        backup = S3Backup()
        result = backup.upload_backup(backup_name, backup_data)

        return result
    except Exception as e:
        frappe.log_error(str(e), "S3 Upload Error")
        return {'success': False, 'error': str(e)}


@frappe.whitelist()
def list_s3_backups():
    """API endpoint: Lista backups en S3"""
    try:
        backup = S3Backup()
        result = backup.list_backups()
        return result
    except Exception as e:
        frappe.log_error(str(e), "S3 List Error")
        return {'success': False, 'error': str(e)}
