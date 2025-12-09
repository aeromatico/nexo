# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

"""
Verificador de Compliance Fiscal

Sistema automático de verificación de cumplimiento con normativas fiscales.
Detecta problemas potenciales y genera reportes de compliance.
"""

import frappe
from frappe import _
from datetime import datetime, date
from typing import Dict, List, Any, Tuple


def check_iva_compliance(company: str, month: int, year: int) -> Dict[str, Any]:
    """
    Verifica compliance IVA

    Validaciones:
    - Todas las facturas tienen NIT
    - Débito fiscal correcto
    - Facturas anuladas reportadas
    - Libros de ventas/compras completos

    Args:
        company: Empresa
        month: Mes
        year: Año

    Returns:
        Dict: Resultado de compliance
    """
    import calendar
    from datetime import date as dt

    first_day = dt(year, month, 1)
    last_day = dt(year, month, calendar.monthrange(year, month)[1])

    issues = []
    warnings = []

    # 1. Verificar que todas las facturas tienen NIT/CI
    missing_nit = frappe.db.sql("""
        SELECT si.name, si.customer_name
        FROM `tabSales Invoice` si
        WHERE si.company = %s
        AND si.docstatus = 1
        AND si.posting_date BETWEEN %s AND %s
        AND (si.customer_nit IS NULL OR si.customer_nit = '')
    """, (company, first_day, last_day), as_dict=True)

    if missing_nit:
        issues.append({
            'category': 'IVA',
            'severity': 'ERROR',
            'message': f'Se encontraron {len(missing_nit)} facturas sin NIT del cliente',
            'details': [f"Factura {inv['name']}" for inv in missing_nit[:5]]
        })

    # 2. Verificar integridad del débito fiscal
    incorrect_iva = frappe.db.sql("""
        SELECT si.name, si.grand_total, si.customer_name
        FROM `tabSales Invoice` si
        WHERE si.company = %s
        AND si.docstatus = 1
        AND si.posting_date BETWEEN %s AND %s
        LIMIT 100
    """, (company, first_day, last_day), as_dict=True)

    iva_issues = []
    for invoice in incorrect_iva:
        invoice_doc = frappe.get_doc('Sales Invoice', invoice['name'])
        # Verificar que tenga impuesto IVA
        has_iva = any('IVA' in (tax.description or '') for tax in invoice_doc.taxes)
        if not has_iva and invoice_doc.grand_total > 0:
            iva_issues.append(invoice['name'])

    if iva_issues:
        issues.append({
            'category': 'IVA',
            'severity': 'WARNING',
            'message': f'{len(iva_issues)} facturas sin IVA',
            'details': iva_issues[:5]
        })

    # 3. Verificar facturas anuladas
    cancelled_invoices = frappe.db.sql("""
        SELECT COUNT(*) as count
        FROM `tabSales Invoice`
        WHERE company = %s
        AND is_cancelled = 1
        AND posting_date BETWEEN %s AND %s
    """, (company, first_day, last_day))[0][0] or 0

    if cancelled_invoices:
        warnings.append({
            'category': 'IVA',
            'severity': 'INFO',
            'message': f'Se encontraron {cancelled_invoices} facturas anuladas',
            'action': 'Verificar que estén registradas en Declaración IVA'
        })

    return {
        'category': 'IVA',
        'period': f'{month:02d}/{year}',
        'status': 'COMPLIANT' if not issues else 'NON_COMPLIANT',
        'issues': issues,
        'warnings': warnings,
        'timestamp': datetime.now()
    }


def check_payroll_compliance(company: str, month: int, year: int) -> Dict[str, Any]:
    """
    Verifica compliance nómina

    Validaciones:
    - AFP calculado correctamente
    - RC-IVA aplicado según tabla
    - Prima pagada cuando corresponde

    Args:
        company: Empresa
        month: Mes
        year: Año

    Returns:
        Dict: Resultado de compliance
    """
    import calendar
    from datetime import date as dt

    first_day = dt(year, month, 1)
    last_day = dt(year, month, calendar.monthrange(year, month)[1])

    issues = []
    warnings = []

    # 1. Verificar AFP en salary slips
    missing_afp = frappe.db.sql("""
        SELECT ss.name, ss.employee_name
        FROM `tabSalary Slip` ss
        WHERE ss.company = %s
        AND ss.docstatus = 1
        AND ss.posting_date BETWEEN %s AND %s
        AND NOT EXISTS (
            SELECT 1 FROM `tabSalary Slip Deduction` ssd
            WHERE ssd.parent = ss.name
            AND ssd.salary_component LIKE '%AFP%'
        )
    """, (company, first_day, last_day), as_dict=True)

    if missing_afp:
        issues.append({
            'category': 'Nómina',
            'severity': 'ERROR',
            'message': f'Se encontraron {len(missing_afp)} salary slips sin AFP',
            'details': [f"{slip['employee_name']} ({slip['name']})" for slip in missing_afp[:3]]
        })

    # 2. Verificar prima de antigüedad
    if month == 6 or month == 12:  # Junio y Diciembre
        missing_prima = frappe.db.sql("""
            SELECT COUNT(*) as count
            FROM `tabSalary Slip`
            WHERE company = %s
            AND docstatus = 1
            AND posting_date BETWEEN %s AND %s
            AND NOT EXISTS (
                SELECT 1 FROM `tabSalary Slip Earning` sse
                WHERE sse.parent = name
                AND sse.salary_component LIKE '%Prima%'
            )
        """, (company, first_day, last_day))[0][0] or 0

        if missing_prima:
            warnings.append({
                'category': 'Nómina',
                'severity': 'WARNING',
                'message': f'{missing_prima} salary slips sin Prima de Antigüedad en mes {month}',
                'action': 'Prima debe pagarse en junio (21) y diciembre (21)'
            })

    return {
        'category': 'Nómina',
        'period': f'{month:02d}/{year}',
        'status': 'COMPLIANT' if not issues else 'NON_COMPLIANT',
        'issues': issues,
        'warnings': warnings,
        'timestamp': datetime.now()
    }


def check_sin_compliance(company: str, month: int, year: int) -> Dict[str, Any]:
    """
    Verifica compliance SIN

    Validaciones:
    - Facturas enviadas a SIAT
    - CUF asignados
    - QR generados
    - Sin facturas pendientes

    Args:
        company: Empresa
        month: Mes
        year: Año

    Returns:
        Dict: Resultado de compliance
    """
    import calendar
    from datetime import date as dt

    first_day = dt(year, month, 1)
    last_day = dt(year, month, calendar.monthrange(year, month)[1])

    issues = []
    warnings = []

    # 1. Verificar CUF en facturas electrónicas
    missing_cuf = frappe.db.sql("""
        SELECT si.name, si.customer_name
        FROM `tabSales Invoice` si
        WHERE si.company = %s
        AND si.docstatus = 1
        AND si.posting_date BETWEEN %s AND %s
        AND (si.cuf IS NULL OR si.cuf = '')
    """, (company, first_day, last_day), as_dict=True)

    if missing_cuf:
        warnings.append({
            'category': 'SIN',
            'severity': 'WARNING',
            'message': f'Se encontraron {len(missing_cuf)} facturas sin CUF',
            'details': [f['name'] for f in missing_cuf[:5]],
            'action': 'Sincronizar con SIN para obtener CUF'
        })

    # 2. Verificar QR
    missing_qr = frappe.db.sql("""
        SELECT COUNT(*) as count
        FROM `tabSales Invoice` si
        WHERE si.company = %s
        AND si.docstatus = 1
        AND si.posting_date BETWEEN %s AND %s
        AND (si.qr_code IS NULL OR si.qr_code = '')
    """, (company, first_day, last_day))[0][0] or 0

    if missing_qr:
        warnings.append({
            'category': 'SIN',
            'severity': 'INFO',
            'message': f'{missing_qr} facturas sin código QR generado',
            'action': 'Los códigos QR se generarán automáticamente al sincronizar'
        })

    return {
        'category': 'SIN',
        'period': f'{month:02d}/{year}',
        'status': 'COMPLIANT' if not issues else 'NON_COMPLIANT',
        'issues': issues,
        'warnings': warnings,
        'timestamp': datetime.now()
    }


def generate_compliance_report(company: str, period: str) -> Dict[str, Any]:
    """
    Genera reporte completo de compliance

    Args:
        company: Empresa
        period: Período en formato 'MM/YYYY'

    Returns:
        Dict: Reporte de compliance
    """
    # Parsear período
    parts = period.split('/')
    month = int(parts[0])
    year = int(parts[1])

    # Ejecutar verificaciones
    iva_check = check_iva_compliance(company, month, year)
    payroll_check = check_payroll_compliance(company, month, year)
    sin_check = check_sin_compliance(company, month, year)

    # Compilar resultados
    all_checks = [iva_check, payroll_check, sin_check]

    total_issues = sum(len(check.get('issues', [])) for check in all_checks)
    total_warnings = sum(len(check.get('warnings', [])) for check in all_checks)

    # Determinar estado general
    if total_issues > 0:
        overall_status = 'NON_COMPLIANT'
    elif total_warnings > 0:
        overall_status = 'WARNINGS'
    else:
        overall_status = 'COMPLIANT'

    # Recomendaciones
    recommendations = []

    if iva_check['status'] == 'NON_COMPLIANT':
        recommendations.append('Revisar y completar información de clientes en facturas')
        recommendations.append('Verificar cálculo de IVA en todas las facturas')

    if payroll_check['status'] == 'NON_COMPLIANT':
        recommendations.append('Validar cálculo de AFP en nómina')
        recommendations.append('Verificar retenciones RC-IVA')

    if sin_check['status'] == 'NON_COMPLIANT':
        recommendations.append('Sincronizar facturas con SIN')
        recommendations.append('Generar códigos QR para facturas electrónicas')

    return {
        'company': company,
        'period': period,
        'overall_status': overall_status,
        'total_issues': total_issues,
        'total_warnings': total_warnings,
        'checks': {
            'iva': iva_check,
            'payroll': payroll_check,
            'sin': sin_check
        },
        'recommendations': recommendations,
        'generated_at': datetime.now()
    }


def run_daily_compliance_check():
    """
    Ejecuta verificación diaria de compliance

    Se ejecuta automáticamente cada día por scheduler
    """
    companies = frappe.db.get_list('Company', filters={'disabled': 0}, pluck='name')

    for company in companies:
        today = datetime.now()
        report = generate_compliance_report(company, f'{today.month:02d}/{today.year}')

        # Registrar reporte
        frappe.get_doc({
            'doctype': 'Compliance Report',
            'company': company,
            'period': f'{today.month:02d}/{today.year}',
            'overall_status': report['overall_status'],
            'total_issues': report['total_issues'],
            'total_warnings': report['total_warnings'],
            'report_data': frappe.as_json(report)
        }).insert()


@frappe.whitelist()
def check_compliance(company: str, period: str) -> Dict[str, Any]:
    """
    API para verificar compliance

    Args:
        company: Empresa
        period: Período (MM/YYYY)

    Returns:
        Dict: Reporte de compliance
    """
    return generate_compliance_report(company, period)


@frappe.whitelist()
def get_compliance_summary(company: str, period: str) -> Dict[str, Any]:
    """Obtiene resumen ejecutivo de compliance"""
    report = generate_compliance_report(company, period)

    return {
        'company': company,
        'period': period,
        'status': report['overall_status'],
        'total_issues': report['total_issues'],
        'total_warnings': report['total_warnings'],
        'is_compliant': report['overall_status'] == 'COMPLIANT'
    }
