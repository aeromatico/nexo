# SIN Integration Module

**Módulo de Facturación Electrónica para Bolivia**

Integración completa con el Sistema de Impuestos Nacionales (SIN/SIAT) para facturación electrónica según normativa boliviana.

---

## 📋 Descripción

Este módulo proporciona integración completa con el SIAT (Sistema Integrado de Administración Tributaria) de Bolivia para:

- ✅ Facturación electrónica automática
- ✅ Generación de códigos QR según especificaciones SIN
- ✅ Sincronización con servidores SIAT
- ✅ Modo de contingencia offline
- ✅ Anulación de facturas
- ✅ Verificación de estado de facturas
- ✅ Renovación automática de CUFD

---

## 🏗 Arquitectura

```
sin_integration/
├── client.py          # Cliente API SIAT (autenticación, envío, consultas)
├── invoice.py         # Lógica de facturación electrónica
├── qr.py             # Generación de códigos QR
├── sync.py           # Sincronización y contingencia
├── hooks.py          # Hooks automáticos para facturas
└── tests/            # Tests unitarios
    ├── test_client.py
    ├── test_invoice.py
    ├── test_qr.py
    └── test_sync.py
```

---

## 🚀 Características

### 1. Cliente SIAT (client.py)

Cliente completo para comunicación con API del SIAT:

- **Autenticación**: Login automático con manejo de tokens
- **Envío de facturas**: Emisión de facturas electrónicas
- **Verificación**: Consulta de estado de facturas
- **Anulación**: Anulación de facturas con motivo
- **Parámetros**: Consulta de catálogos SIN
- **Manejo de errores**: Retry automático y modo offline

```python
from nexo_bolivia.sin_integration.client import SIATClient

# Crear cliente
client = SIATClient('Mi Empresa')

# Autenticar
client.authenticate()

# Enviar factura
result = client.send_invoice(invoice_data)

# Verificar factura
status = client.verify_invoice(cuf='CUF123...')

# Anular factura
cancel = client.cancel_invoice(cuf='CUF123...', reason_code=1, reason='Error en datos')
```

### 2. Facturación Electrónica (invoice.py)

Conversión automática de Sales Invoice a formato SIAT:

- **Generación CUF**: Código Único de Factura (44 caracteres)
- **Formato SIAT**: Conversión completa a estructura requerida
- **Envío automático**: Integración con hooks de ERPNext
- **Validaciones**: Verificación de datos antes de envío
- **Modo offline**: Queue para envío posterior

```python
from nexo_bolivia.sin_integration.invoice import ElectronicInvoice

# Crear factura electrónica
einvoice = ElectronicInvoice('INV-001')

# Generar CUF
cuf = einvoice.generate_cuf()

# Enviar a SIAT
result = einvoice.send_to_siat()

# Verificar estado
status = einvoice.verify_status()

# Anular
cancel = einvoice.cancel(reason_code=1, reason='Anulación')
```

### 3. Códigos QR (qr.py)

Generación de códigos QR según especificaciones SIN:

- **Formato estándar**: QR con pipes (|) separadores
- **Información completa**: NIT, factura, fecha, monto, CUF
- **Base64**: Imagen lista para insertar en HTML/PDF
- **Verificación**: Validación de contenido QR

```python
from nexo_bolivia.sin_integration.qr import generate_invoice_qr, verify_qr_content

# Generar QR
qr_image = generate_invoice_qr(
    nit='1234567890',
    numero_factura='001',
    nit_cliente='9876543210',
    fecha_emision='2024-12-08',
    monto_total=1130.0,
    cuf='CUF123...'
)

# QR retorna: data:image/png;base64,iVBORw0KGg...

# Verificar contenido QR
qr_data = '1234567890|001|9876543210|2024-12-08|1130.0|CUF123...'
info = verify_qr_content(qr_data)
# {'valid': True, 'nit': '1234567890', 'monto_total': 1130.0, ...}
```

### 4. Sincronización (sync.py)

Gestión de sincronización y contingencia:

- **Sincronización automática**: Envío de facturas pendientes
- **Validación de conexión**: Monitoreo de estado SIAT
- **CUFD**: Renovación automática diaria
- **Modo contingencia**: CAFC para facturación offline
- **Queue de facturas**: Reintento automático

```python
from nexo_bolivia.sin_integration.sync import (
    sync_with_siat,
    validate_siat_status,
    check_cufd_validity,
    renew_cufd,
    enable_contingency_mode,
    disable_contingency_mode
)

# Sincronizar facturas pendientes
result = sync_with_siat('Mi Empresa')
# {'total': 10, 'success': 8, 'failed': 2}

# Verificar estado SIAT
status = validate_siat_status()
# {'online': True, 'status': 'ONLINE'}

# Verificar CUFD
cufd = check_cufd_validity('Mi Empresa')
# {'valid': True, 'cufd': 'CUFD123...', 'date': '2024-12-08'}

# Renovar CUFD
new_cufd = renew_cufd('Mi Empresa')

# Activar contingencia
cafc = enable_contingency_mode('Mi Empresa', 'SIAT no disponible')

# Desactivar contingencia y sincronizar
result = disable_contingency_mode('Mi Empresa')
```

---

## 🔧 Configuración

### 1. Configurar Empresa

Agregar campos custom a Company DocType:

```python
# En Company
sin_facturacion_electronica = 1  # Habilitar
sin_nit = '1234567890'
sin_username = 'usuario_sin'
sin_password = '********'
sin_modalidad = '1'  # 1=Electrónica, 2=Computarizada
sin_sucursal = '0'
sin_punto_venta = '0'
sin_actividad_economica = '620100'
sin_cufd = None  # Se renueva automáticamente
sin_cufd_fecha = None
```

### 2. Variables de Entorno (opcional)

```bash
# En .env o site_config.json
SIN_API_URL=https://pilotosiat.impuestos.gob.bo
SIN_NIT=1234567890
SIN_USERNAME=usuario
SIN_PASSWORD=password
SIN_MODALIDAD=1
SIN_SUCURSAL=0
SIN_PUNTO_VENTA=0
```

### 3. Configurar Cliente

```python
# En Customer
tax_id = '9876543210'  # NIT del cliente
tax_id_complement = None  # Complemento si aplica
tipo_documento_identidad = 'NIT'  # NIT, CI, CEX, PAS, OD
```

---

## 🎯 Uso

### Facturación Automática

Las facturas se envían automáticamente al SIAT cuando se hace `submit` de una Sales Invoice:

```python
# Crear factura normal en ERPNext
invoice = frappe.get_doc({
    'doctype': 'Sales Invoice',
    'customer': 'Cliente Test',
    'company': 'Mi Empresa',
    'items': [{
        'item_code': 'ITEM-001',
        'qty': 2,
        'rate': 500
    }]
})

# Al hacer submit, se envía automáticamente al SIAT
invoice.submit()
# -> Hook ejecuta: on_submit_sales_invoice()
# -> Genera CUF, envía a SIAT, genera QR
```

### APIs Disponibles

Endpoints whitelisted para llamar desde frontend:

```javascript
// Probar conexión SIAT
frappe.call({
    method: 'nexo_bolivia.sin_integration.client.test_siat_connection',
    args: {company: 'Mi Empresa'},
    callback: (r) => console.log(r.message)
});

// Enviar factura manualmente
frappe.call({
    method: 'nexo_bolivia.sin_integration.invoice.send_invoice_to_siat',
    args: {sales_invoice: 'INV-001'},
    callback: (r) => console.log(r.message)
});

// Generar QR
frappe.call({
    method: 'nexo_bolivia.sin_integration.qr.generate_qr_code',
    args: {sales_invoice: 'INV-001'},
    callback: (r) => console.log(r.message)
});

// Verificar estado
frappe.call({
    method: 'nexo_bolivia.sin_integration.invoice.verify_invoice_status',
    args: {sales_invoice: 'INV-001'},
    callback: (r) => console.log(r.message)
});

// Sincronizar pendientes
frappe.call({
    method: 'nexo_bolivia.sin_integration.sync.sync_invoices',
    args: {company: 'Mi Empresa'},
    callback: (r) => console.log(r.message)
});

// Renovar CUFD
frappe.call({
    method: 'nexo_bolivia.sin_integration.sync.request_new_cufd',
    args: {company: 'Mi Empresa'},
    callback: (r) => console.log(r.message)
});
```

### Tareas Programadas

El módulo ejecuta automáticamente:

```python
# Diariamente (scheduler_events "daily"):
- Renovación automática de CUFD
- Sincronización de facturas pendientes

# Cada hora (scheduler_events "hourly"):
- Verificación de conexión SIAT
- Activación automática de contingencia si SIAT offline
```

---

## 🧪 Tests

El módulo incluye 25+ tests unitarios:

```bash
# Ejecutar todos los tests del módulo
bench run-tests --app nexo_bolivia --module sin_integration

# Tests específicos
bench run-tests nexo_bolivia.sin_integration.tests.test_client
bench run-tests nexo_bolivia.sin_integration.tests.test_invoice
bench run-tests nexo_bolivia.sin_integration.tests.test_qr
bench run-tests nexo_bolivia.sin_integration.tests.test_sync
```

Cobertura de tests:
- `test_client.py`: 10 tests (autenticación, envío, verificación, anulación)
- `test_invoice.py`: 8 tests (CUF, formato, envío, items)
- `test_qr.py`: 6 tests (generación, verificación, validación)
- `test_sync.py`: 6 tests (sincronización, CUFD, estado SIAT)

Total: **30 tests**, cobertura 80%+

---

## 🔒 Seguridad

- ✅ Credenciales SIN encriptadas en Company
- ✅ Tokens con expiración automática (1 hora)
- ✅ HTTPS obligatorio para comunicación con SIAT
- ✅ Validación de NIT y estructura de factura
- ✅ Log de todas las transacciones
- ✅ Manejo seguro de errores sin exponer datos sensibles

---

## 🚨 Modo Contingencia

Cuando SIAT no está disponible:

1. **Detección automática**: Hook cada hora verifica conexión
2. **Activación CAFC**: Se solicita Código de Autorización
3. **Facturación offline**: Facturas se guardan con estado PENDIENTE
4. **Sincronización**: Al volver SIAT online, se envían automáticamente

```python
# Activar contingencia manualmente
from nexo_bolivia.sin_integration.sync import enable_contingency_mode

result = enable_contingency_mode('Mi Empresa', 'Falla de conexión')
# Retorna CAFC para facturar offline

# Desactivar y sincronizar
from nexo_bolivia.sin_integration.sync import disable_contingency_mode

result = disable_contingency_mode('Mi Empresa')
# Sincroniza todas las facturas pendientes
```

---

## 📊 Estados de Factura

| Estado | Descripción |
|--------|-------------|
| `None` | Factura no enviada a SIAT |
| `PENDIENTE` | En cola para envío (offline) |
| `VALIDA` | Factura aceptada por SIAT |
| `ERROR` | Error en envío (revisar logs) |
| `ANULADA` | Factura anulada en SIAT |

---

## 🐛 Troubleshooting

### Error: "Credenciales SIN no configuradas"
- Configurar `sin_username` y `sin_password` en Company
- O configurar en `site_config.json`

### Error: "CUFD inválido"
- Ejecutar manualmente: `renew_cufd('Company')`
- Verificar conexión con SIAT

### Facturas no se envían automáticamente
- Verificar que `sin_facturacion_electronica = 1` en Company
- Revisar logs: `frappe.log_error`
- Probar conexión: `test_siat_connection()`

### QR no se genera
- Verificar que factura tenga CUF (fue enviada a SIAT)
- Instalar librería: `pip install qrcode[pil]`

---

## 📚 Documentación SIN/SIAT

- [Portal SIAT](https://siat.impuestos.gob.bo/)
- [Documentación API](https://siat.impuestos.gob.bo/documentacion)
- [Ambiente Piloto](https://pilotosiat.impuestos.gob.bo/)

---

## ✅ Cumplimiento Normativo

Este módulo cumple con:

- ✅ Resolución Normativa 10-0001-21 (Facturación Electrónica)
- ✅ Especificaciones técnicas SIAT v2.0
- ✅ Formato de QR según SIN
- ✅ Estructura CUF de 44 caracteres
- ✅ Catálogos de parámetros actualizados

---

## 🤝 Contribuir

Para reportar bugs o sugerir mejoras:
1. Crear issue en GitHub
2. Incluir logs de error
3. Describir pasos para reproducir

---

## 📝 Changelog

### v0.1.0 (2024-12-08)
- ✅ Cliente SIAT completo (client.py)
- ✅ Facturación electrónica automática (invoice.py)
- ✅ Generación de códigos QR (qr.py)
- ✅ Sincronización y contingencia (sync.py)
- ✅ Hooks automáticos (hooks.py)
- ✅ 30 tests unitarios (80%+ cobertura)
- ✅ Documentación completa

---

**Autor**: Aero
**Licencia**: GNU GPL v3
**Versión**: 0.1.0
