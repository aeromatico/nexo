# Módulo de Reportes Fiscales Bolivia - Fase 4

Reportes fiscales oficiales requeridos por el **SIN (Sistema de Impuestos Nacionales)** de Bolivia, incluyendo libros IVA, declaraciones, auditoría y exportadores.

## Tabla de Contenidos

1. [Reportes Principales](#reportes-principales)
2. [Módulo de Auditoría](#módulo-de-auditoría)
3. [Exportadores](#exportadores)
4. [APIs REST](#apis-rest)
5. [Configuración](#configuración)
6. [Ejemplos de Uso](#ejemplos-de-uso)
7. [Normativa](#normativa)

## Reportes Principales

### 1. Libro de Ventas IVA

**Propósito**: Registro detallado y oficial de todas las ventas con IVA del período según Resolución Normativa 10-0001-07.

**Ubicación**: `nexo_bolivia/reports/libro_ventas_iva/`

**Columnas del Reporte**:
- Nro: Número correlativo
- Fecha de Factura
- Nro de Factura
- CUF/Autorización (para electrónicas)
- Estado: Válida, Anulada, Borrador
- NIT/CI del Cliente
- Nombre/Razón Social del Cliente
- Monto Total Venta
- Importe ICE (si aplica)
- Importe Exentas
- Importe Gravadas (Base imponible)
- Débito Fiscal (IVA 13%)
- Código de Control

**Funcionalidades**:
```python
# Ejecutar reporte
from nexo_bolivia.reports.libro_ventas_iva.libro_ventas_iva import execute

filters = {
    'company': 'Mi Empresa',
    'from_date': '2024-01-01',
    'to_date': '2024-01-31',
    'customer': 'Cliente X'  # Opcional
}

columns, data = execute(filters)
```

**Validaciones Automáticas**:
- ✅ Todas las facturas válidas deben tener NIT del cliente
- ✅ Débito fiscal debe ser exactamente 13% de base imponible
- ✅ Fechas deben estar en el período fiscal
- ✅ Facturas anuladas deben aparecer con estado "Anulada"

**Exportación**:
- Excel formato oficial SIN
- TXT formato da Vinci

---

### 2. Libro de Compras IVA

**Propósito**: Registro detallado y oficial de todas las compras con IVA del período.

**Ubicación**: `nexo_bolivia/reports/libro_compras_iva/`

**Columnas del Reporte**:
- Nro: Número correlativo
- Fecha de Factura
- Nro de Factura
- Nro de DUI (Declaración Única de Importación, si aplica)
- NIT del Proveedor
- Nombre/Razón Social del Proveedor
- Monto Total Compra
- Importe ICE (si aplica)
- Importe No Sujeto a Crédito Fiscal
- Importes con Derecho a Crédito Fiscal
- Crédito Fiscal (IVA 13%)
- Código de Control

**Funcionalidades**:
```python
from nexo_bolivia.reports.libro_compras_iva.libro_compras_iva import execute

filters = {
    'company': 'Mi Empresa',
    'from_date': '2024-01-01',
    'to_date': '2024-01-31'
}

columns, data = execute(filters)
```

**Validaciones**:
- ✅ Todas las facturas válidas deben tener NIT del proveedor
- ✅ Crédito fiscal debe ser exactamente 13% de monto con derecho a CF
- ✅ Todas las facturas publicadas deben estar incluidas

---

### 3. Declaración Jurada IVA (Form 200)

**Propósito**: Formulario oficial de declaración mensual de IVA ante el SIN.

**Ubicación**: `nexo_bolivia/reports/declaracion_iva/`

**Estructura del Formulario**:

**Sección I: VENTAS**
- Total de facturas del período
- Facturas anuladas (ajustes)
- Total Débito Fiscal (DF)

**Sección II: COMPRAS**
- Total de compras con crédito fiscal
- Total de compras sin derecho a crédito
- Total Crédito Fiscal (CF)

**Sección III: DETERMINACIÓN**
- Débito Fiscal Total
- Menos: Crédito Fiscal Total
- Saldo a favor del fisco (si DF > CF)
- Saldo a favor del contribuyente (si CF > DF)
- Saldo período anterior
- Total a pagar o saldo siguiente período

**Uso**:
```python
from nexo_bolivia.reports.declaracion_iva.declaracion_iva import calculate_iva_declaration

# API REST para calcular declaración
form_200 = calculate_iva_declaration(
    company='Mi Empresa',
    month=1,
    year=2024
)

# Exportar a PDF
export_form_200_pdf(
    company='Mi Empresa',
    month=1,
    year=2024
)
```

---

### 4. Reporte IT Mensual

**Propósito**: Reporte del Impuesto a las Transacciones (3%) para el período.

**Ubicación**: `nexo_bolivia/reports/reporte_it/`

**Información Incluida**:
- Ingresos totales del período
- Base imponible IT (ingresos con IVA)
- Tasa aplicable (3%)
- IT generado en el período
- Pagos a cuenta realizados
- Saldo a pagar

**Uso**:
```python
from nexo_bolivia.reports.reporte_it.reporte_it import get_it_report

result = get_it_report(
    company='Mi Empresa',
    month=1,
    year=2024
)

# result contiene:
# {
#     'ingresos_totales': float,
#     'base_imponible': float,
#     'it_generado': float,
#     'pagos_cuenta': float,
#     'saldo_pagar': float
# }
```

---

### 5. Reporte IUE Anual

**Propósito**: Reporte del Impuesto sobre Utilidades de Empresas (25%) para el año fiscal.

**Ubicación**: `nexo_bolivia/reports/reporte_iue/`

**Información Incluida**:
- Utilidad neta del ejercicio
- Ajustes fiscales (adiciones/deducciones)
- Base imponible IUE
- IUE calculado (25%)
- IT pagado en el año (compensable 100%)
- IUE neto a pagar

**Uso**:
```python
from nexo_bolivia.reports.reporte_iue.reporte_iue import generate_declaracion_iue

# Generar Form 500 (Declaración Jurada IUE)
form_500 = generate_declaracion_iue(
    company='Mi Empresa',
    fiscal_year='2024'
)
```

---

### 6. Reporte RC-IVA

**Propósito**: Reporte de Retenciones de RC-IVA en planilla del período.

**Ubicación**: `nexo_bolivia/reports/reporte_rc_iva/`

**Información por Empleado**:
- Salario mensual
- Otros ingresos
- Deducciones (dependientes)
- Base imponible
- RC-IVA retenido según tabla
- Total retenido en el período

**Tabla de Retención RC-IVA**:
```
Salario Mensual          Tasa RC-IVA
Hasta Bs. 2,500          0%
Bs. 2,501 - 5,000        0.5%
Bs. 5,001 - 7,500        1.0%
Bs. 7,501 - 10,000       1.5%
Mayor a Bs. 10,000       2.0%
```

---

## Módulo de Auditoría

### Pista de Auditoría (Audit Trail)

**Propósito**: Sistema inmutable de registro de todas las transacciones fiscales. Permite rastrear cambios en facturas, impuestos y documentos críticos.

**Ubicación**: `nexo_bolivia/reports/audit/audit_trail.py`

**Funcionalidades**:

```python
from nexo_bolivia.reports.audit.audit_trail import (
    log_fiscal_transaction,
    get_audit_trail,
    verify_audit_integrity,
    verify_document_integrity
)

# Registrar transacción
audit_id = log_fiscal_transaction(
    doctype='Sales Invoice',
    docname='SI-001',
    action='submit',
    user='user@company.com',
    data={'customer': 'ABC Corp', 'amount': 5000},
    description='Invoice submitted'
)

# Obtener pista de auditoría
entries = get_audit_trail(filters={
    'doctype': 'Sales Invoice',
    'from_date': '2024-01-01',
    'to_date': '2024-01-31'
})

# Verificar integridad general
integrity = verify_audit_integrity()

# Verificar documento específico
doc_integrity = verify_document_integrity('Sales Invoice', 'SI-001')
```

**Características**:
- ✅ Registro inmutable con hash SHA256
- ✅ Cadena de auditoría continua
- ✅ Validación de integridad
- ✅ Timestamp automático
- ✅ Usuario responsable registrado

---

### Verificador de Compliance

**Propósito**: Sistema automático de verificación de cumplimiento con normativas fiscales. Detecta problemas potenciales y genera reportes.

**Ubicación**: `nexo_bolivia/reports/audit/compliance_checker.py`

**Funcionalidades**:

```python
from nexo_bolivia.reports.audit.compliance_checker import (
    check_iva_compliance,
    check_payroll_compliance,
    check_sin_compliance,
    generate_compliance_report,
    get_compliance_summary
)

# Verificar compliance IVA
iva_check = check_iva_compliance(
    company='Mi Empresa',
    month=1,
    year=2024
)

# Verificar compliance Nómina
payroll_check = check_payroll_compliance(
    company='Mi Empresa',
    month=1,
    year=2024
)

# Verificar compliance SIN
sin_check = check_sin_compliance(
    company='Mi Empresa',
    month=1,
    year=2024
)

# Generar reporte completo
full_report = generate_compliance_report(
    company='Mi Empresa',
    period='01/2024'
)

# Obtener resumen ejecutivo
summary = get_compliance_summary(
    company='Mi Empresa',
    period='01/2024'
)
```

**Validaciones de IVA**:
- ✅ Todas las facturas tienen NIT del cliente
- ✅ Débito fiscal calculado correctamente
- ✅ Facturas anuladas reportadas
- ✅ Libros de ventas/compras completos

**Validaciones de Nómina**:
- ✅ AFP calculado correctamente
- ✅ RC-IVA aplicado según tabla
- ✅ Prima de antigüedad pagada en fechas (21/06, 21/12)

**Validaciones de SIN**:
- ✅ Facturas enviadas a SIAT
- ✅ CUF asignados
- ✅ Códigos QR generados
- ✅ Sin facturas pendientes

---

## Exportadores

### Excel Exporter

**Propósito**: Exportar reportes a formato Excel oficial del SIN con formato y estilos profesionales.

**Ubicación**: `nexo_bolivia/reports/exporters/excel_exporter.py`

**Funcionalidades**:

```python
from nexo_bolivia.reports.exporters.excel_exporter import (
    export_libro_ventas_to_excel,
    export_libro_compras_to_excel,
    export_form_200_to_excel
)

# Exportar Libro de Ventas
excel_file = export_libro_ventas_to_excel(
    data=report_data,
    columns=columns,
    filters=filters
)

# Exportar Libro de Compras
excel_file = export_libro_compras_to_excel(
    data=report_data,
    columns=columns,
    filters=filters
)

# Exportar Form 200
excel_file = export_form_200_to_excel(
    data=form_200_data,
    filters=filters
)
```

**Características del Excel**:
- ✅ Formato profesional con encabezados
- ✅ Información de empresa y período
- ✅ Estilos de celda personalizados
- ✅ Formatos de moneda y fecha
- ✅ Filas de totales destacadas
- ✅ Ancho de columnas automático

---

### TXT Exporter (da Vinci)

**Propósito**: Exportar reportes a formato TXT delimitado por pipes para importación en sistema da Vinci del SIN.

**Ubicación**: `nexo_bolivia/reports/exporters/txt_exporter.py`

**Funcionalidades**:

```python
from nexo_bolivia.reports.exporters.txt_exporter import (
    export_to_davinci_txt,
    export_libro_ventas_davinci,
    export_libro_compras_davinci,
    export_form_200_davinci
)

# Exportar a formato da Vinci
txt_file = export_to_davinci_txt(
    data=report_data,
    columns=columns,
    report_type='libro_ventas'
)

# Exportar Libro de Ventas
txt_file = export_libro_ventas_davinci(
    data=report_data,
    filters=filters
)
```

**Características**:
- ✅ Delimitado por pipes (|)
- ✅ Encoding UTF-8 sin BOM
- ✅ Escapado de caracteres especiales
- ✅ Formato compatible con da Vinci

---

## APIs REST

### Reportes

```javascript
// Libro de Ventas IVA
GET /api/resource/Query Report/Libro de Ventas IVA
POST /api/method/nexo_bolivia.reports.libro_ventas_iva.export_to_excel
POST /api/method/nexo_bolivia.reports.libro_ventas_iva.export_to_txt

// Libro de Compras IVA
GET /api/resource/Query Report/Libro de Compras IVA
POST /api/method/nexo_bolivia.reports.libro_compras_iva.export_to_excel
POST /api/method/nexo_bolivia.reports.libro_compras_iva.export_to_txt

// Declaración IVA
POST /api/method/nexo_bolivia.reports.declaracion_iva.calculate_iva_declaration
POST /api/method/nexo_bolivia.reports.declaracion_iva.export_form_200_pdf
POST /api/method/nexo_bolivia.reports.declaracion_iva.get_form_200_summary

// Reporte IT
POST /api/method/nexo_bolivia.reports.reporte_it.get_it_report
POST /api/method/nexo_bolivia.reports.reporte_it.get_it_summary

// Reporte IUE
POST /api/method/nexo_bolivia.reports.reporte_iue.get_iue_report
POST /api/method/nexo_bolivia.reports.reporte_iue.generate_declaracion_iue
POST /api/method/nexo_bolivia.reports.reporte_iue.get_iue_summary

// Reporte RC-IVA
POST /api/method/nexo_bolivia.reports.reporte_rc_iva.get_rc_iva_report
POST /api/method/nexo_bolivia.reports.reporte_rc_iva.get_rc_iva_summary
```

### Auditoría y Compliance

```javascript
// Audit Trail
POST /api/method/nexo_bolivia.reports.audit.audit_trail.get_audit_trail_report
POST /api/method/nexo_bolivia.reports.audit.audit_trail.verify_document_integrity

// Compliance
POST /api/method/nexo_bolivia.reports.audit.compliance_checker.check_compliance
POST /api/method/nexo_bolivia.reports.audit.compliance_checker.get_compliance_summary
```

---

## Configuración

### Hooks en `nexo_bolivia/hooks.py`

```python
# Reportes personalizados
regional_overrides = {
    "Bolivia": {
        "erpnext.regional.report.gstr_1.gstr_1.execute":
            "nexo_bolivia.reports.libro_ventas_iva.libro_ventas_iva.execute",
        "erpnext.regional.report.gstr_2.gstr_2.execute":
            "nexo_bolivia.reports.libro_compras_iva.libro_compras_iva.execute",
    }
}

# Eventos de documentos para auditoría
doc_events = {
    "Sales Invoice": {
        "on_submit": "nexo_bolivia.reports.audit.audit_trail.log_sales_invoice_submit",
    },
    "Purchase Invoice": {
        "on_submit": "nexo_bolivia.reports.audit.audit_trail.log_purchase_invoice_submit",
    }
}

# Tareas programadas
scheduler_events = {
    "daily": [
        "nexo_bolivia.reports.audit.compliance_checker.run_daily_compliance_check",
    ],
    "monthly": [
        "nexo_bolivia.reports.declaracion_iva.send_declaration_reminder",
    ]
}
```

---

## Ejemplos de Uso

### Generar Libro de Ventas IVA

```python
import frappe
from nexo_bolivia.reports.libro_ventas_iva.libro_ventas_iva import execute

# Ejecutar reporte
filters = {
    'company': 'Acme Bolivia S.A.',
    'from_date': '2024-01-01',
    'to_date': '2024-01-31'
}

columns, data = execute(filters)

# Procesar datos
for row in data:
    print(f"Factura: {row['name']}")
    print(f"Cliente: {row['customer_name']}")
    print(f"Débito Fiscal: {row['iva_amount']}")
```

### Exportar Form 200 a PDF

```python
from nexo_bolivia.reports.declaracion_iva.declaracion_iva import export_form_200_pdf

pdf_file = export_form_200_pdf(
    company='Acme Bolivia S.A.',
    month=1,
    year=2024
)

# pdf_file contiene la ruta del PDF generado
```

### Verificar Compliance

```python
from nexo_bolivia.reports.audit.compliance_checker import generate_compliance_report

report = generate_compliance_report(
    company='Acme Bolivia S.A.',
    period='01/2024'
)

if report['overall_status'] == 'COMPLIANT':
    print("✅ Cumplimiento: OK")
else:
    print(f"❌ Issues encontrados: {report['total_issues']}")
    for issue in report['checks']['iva']['issues']:
        print(f"  - {issue['message']}")
```

---

## Tests

Cada módulo incluye suite completa de tests:

```bash
# Tests unitarios
cd /path/to/nexo
bench run-tests --module nexo_bolivia.reports.libro_ventas_iva
bench run-tests --module nexo_bolivia.reports.audit.audit_trail
bench run-tests --module nexo_bolivia.reports.exporters

# Cobertura
bench run-tests --coverage
```

---

## Normativa

- **Resolución Normativa 10-0001-07**: Libros de Ventas y Compras IVA
- **Formulario 200**: Declaración Jurada IVA (SIN)
- **Formulario 500**: Declaración Jurada IUE (SIN)
- **Ley 843**: Sistema Tributario Boliviano
- **Manual Sistema da Vinci**: Formatos de importación SIN

---

## Soporte

Para reportar issues o solicitar mejoras, contactar:
- Email: admin@aero.bo
- Repositorio: [Nexo ERP GitHub]

---

**Última actualización**: Diciembre 2024
**Versión**: 1.0.0
**Estado**: Producción
