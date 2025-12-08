# Guía de Desarrollo para Claude Code Haiku

**Instrucciones completas para continuar el desarrollo de Nexo ERP**

---

## 📋 CONTEXTO DEL PROYECTO

Estás trabajando en **Nexo ERP**, una plataforma SaaS multi-tenant basada en Frappe Framework y ERPNext, completamente adaptada para Bolivia.

### Información del Proyecto
- **Nombre**: Nexo ERP
- **Autor**: Aero
- **Versión actual**: 0.1.0
- **Stack**: Frappe v15+, ERPNext v15+, Docker, MariaDB, Redis
- **Localización**: Bolivia (facturación SIN, impuestos, nómina)
- **Arquitectura**: Multi-tenant con base de datos separada por tenant

---

## 🎯 OBJETIVO PRINCIPAL

Desarrollar un ERP SaaS multi-tenant modular que permita:
1. Gestionar múltiples empresas (tenants) en una sola instalación
2. Generar sitios web integrados para cada tenant
3. Cumplir con normativa boliviana (SIN, impuestos, nómina)
4. Proveer funcionalidades completas de ERP

---

## 📁 ESTRUCTURA DEL PROYECTO

```
nexo/
├── apps/
│   ├── nexo_core/              # Multi-tenancy y SaaS core
│   │   ├── nexo_core/
│   │   │   ├── hooks.py       # Hooks de Frappe
│   │   │   ├── utils.py       # Funciones utilitarias
│   │   │   ├── tasks/         # Tareas programadas
│   │   │   ├── api/           # REST API endpoints
│   │   │   └── config/        # Configuraciones
│   │   ├── setup.py
│   │   └── README.md
│   │
│   └── nexo_bolivia/           # Localización Bolivia
│       ├── nexo_bolivia/
│       │   ├── hooks.py       # Hooks Bolivia
│       │   ├── utils.py       # Utils Bolivia
│       │   ├── config/        # Configs Bolivia (impuestos, etc)
│       │   ├── sin_integration/ # Integración SIN
│       │   └── tax_engine/    # Motor de impuestos
│       ├── setup.py
│       └── README.md
│
├── docker-compose.yml          # Orquestación Docker
├── .env.example               # Variables de entorno
├── scripts/                   # Scripts de utilidad
├── docs/                      # Documentación
│   └── ARCHITECTURE.md        # Arquitectura técnica
└── README.md                  # Documentación principal
```

---

## 🚀 ROADMAP DE DESARROLLO

### ✅ FASE 1: FUNDACIÓN (COMPLETADA)
- [x] Setup Docker inicial
- [x] Estructura de apps (nexo_core, nexo_bolivia)
- [x] Documentación base
- [x] Configuraciones iniciales

### 🎯 FASE 2: MÓDULOS CORE (EN PROGRESO)

#### ✅ 2.1 Contabilidad Bolivia (COMPLETADO)
**Prioridad**: ALTA
**Estado**: ✅ Completado

Tareas:
- [x] Crear DocType "Plan de Cuentas Bolivia"
- [x] Implementar plan contable boliviano
- [x] Configurar cuentas por defecto
- [x] Crear fixtures para plan contable (75+ cuentas)
- [x] Tests unitarios (15 tests, cobertura 90%+)

Archivos creados:
```
apps/nexo_bolivia/nexo_bolivia/nexo_bolivia/doctype/
├── plan_cuentas_bolivia/
│   ├── plan_cuentas_bolivia.py          # 300 líneas
│   ├── plan_cuentas_bolivia.js          # 250 líneas
│   ├── plan_cuentas_bolivia.json        # DocType definition
│   ├── test_plan_cuentas_bolivia.py     # 15 tests
│   └── README.md                         # Documentación completa
apps/nexo_bolivia/nexo_bolivia/fixtures/
└── plan_cuentas_bolivia.json            # 75+ cuentas fixtures
```

**Código de ejemplo**:
```python
# plan_cuentas_bolivia.py
import frappe
from frappe.model.document import Document

class PlanCuentasBolivia(Document):
    def validate(self):
        # Validar estructura de cuenta
        # Formato: 1111 (4 dígitos)
        pass

    def before_insert(self):
        # Auto-asignar parent según jerarquía
        pass
```

#### ✅ 2.2 Impuestos Bolivia (COMPLETADO)
**Prioridad**: ALTA
**Estado**: ✅ Completado

Tareas:
- [x] Crear Tax Templates para IVA 13%, IT 3%, IUE 25%
- [x] Implementar cálculos automáticos en facturas
- [x] Balance IVA (Crédito Fiscal vs Débito Fiscal)
- [x] Cálculo IT sobre transacciones
- [x] Cálculo IUE con compensación IT
- [x] Validaciones en Purchase/Sales Invoice
- [x] Tests unitarios (32 tests, cobertura 85%+)

Archivos creados:
```
apps/nexo_bolivia/nexo_bolivia/tax_engine/
├── __init__.py                  # Module exports
├── iva.py                       # Lógica IVA (350 líneas)
├── it.py                        # Lógica IT (280 líneas)
├── iue.py                       # Lógica IUE (320 líneas)
├── validators.py                # Validaciones (200 líneas)
├── README.md                    # Documentación completa
└── tests/
    ├── __init__.py
    ├── test_iva.py              # 12 tests IVA
    ├── test_it.py               # 10 tests IT
    └── test_iue.py              # 10 tests IUE
apps/nexo_bolivia/nexo_bolivia/fixtures/
└── tax_templates.json           # Cuentas fiscales
```

**Hooks configurados**:
```python
# hooks.py
doc_events = {
    "Sales Invoice": {
        "validate": [
            "nexo_bolivia.tax_engine.validators.validate_invoice_for_bolivia",
            "nexo_bolivia.tax_engine.iva.apply_iva_to_invoice",
            "nexo_bolivia.tax_engine.it.apply_it_to_invoice",
        ],
    },
    "Purchase Invoice": {
        "validate": [
            "nexo_bolivia.tax_engine.validators.validate_invoice_for_bolivia",
            "nexo_bolivia.tax_engine.iva.apply_iva_to_invoice",
        ],
    },
    "Payment Entry": {
        "on_submit": "nexo_bolivia.tax_engine.it.apply_it_to_payment",
    },
}
```

#### 2.3 Facturación Electrónica SIN
**Prioridad**: ALTA
**Estado**: ⏸️ PRÓXIMO MÓDULO A DESARROLLAR

Tareas:
- [ ] Crear DocType "Factura Electrónica SIN"
- [ ] Implementar conexión API SIN (piloto)
- [ ] Generar código QR en facturas
- [ ] Sincronización con SIAT
- [ ] Manejo de errores y reintentos

Archivos a crear:
```
apps/nexo_bolivia/nexo_bolivia/sin_integration/
├── __init__.py
├── client.py           # Cliente API SIN
├── invoice.py          # Lógica facturas
├── qr.py              # Generación QR
└── sync.py            # Sincronización
```

**Código de ejemplo**:
```python
# sin_integration/client.py
import requests
from frappe import _

class SINClient:
    def __init__(self):
        self.base_url = frappe.conf.get("sin_api_url")
        self.nit = frappe.conf.get("sin_nit")
        self.token = frappe.conf.get("sin_token")

    def send_invoice(self, invoice_data):
        """Enviar factura a SIN"""
        endpoint = f"{self.base_url}/api/v1/factura"
        response = requests.post(
            endpoint,
            json=invoice_data,
            headers={"Authorization": f"Bearer {self.token}"}
        )
        return response.json()
```

#### 2.4 Nómina Bolivia
**Prioridad**: MEDIA

Tareas:
- [ ] Configurar componentes salariales (aguinaldo, prima)
- [ ] Cálculo aportes AFP 12.71%
- [ ] Cálculo RC-IVA
- [ ] Slip de pago boliviano
- [ ] Reportes nómina

### 🎯 FASE 3: MULTI-TENANT SAAS

#### 3.1 Portal Administración Tenants
**Prioridad**: ALTA

Tareas:
- [ ] Crear DocType "Tenant"
- [ ] Dashboard de tenants
- [ ] Métricas por tenant (storage, users, etc)
- [ ] Gestión de planes y facturación

Archivos a crear:
```
apps/nexo_core/nexo_core/nexo_core/doctype/
├── tenant/
│   ├── tenant.py
│   ├── tenant.json
│   ├── tenant.js
│   └── tenant_dashboard.py
```

#### 3.2 Auto-provisioning Tenants
**Prioridad**: ALTA

Tareas:
- [ ] Implementar `create_tenant()` en utils.py
- [ ] Script de creación automática de sitios
- [ ] Setup inicial por tenant
- [ ] Configuración DNS/subdomain automática

**Código de ejemplo**:
```python
# nexo_core/utils.py
def create_tenant(tenant_name, admin_email, admin_password):
    """Crear nuevo tenant automáticamente"""
    import subprocess

    # 1. Crear site
    site_name = f"{tenant_name}.nexo.bo"
    cmd = [
        "bench", "new-site", site_name,
        f"--admin-password={admin_password}",
        "--install-app=erpnext",
        "--install-app=nexo_core",
        "--install-app=nexo_bolivia"
    ]
    subprocess.run(cmd)

    # 2. Configurar datos iniciales Bolivia
    frappe.set_user("Administrator")
    frappe.init(site=site_name)

    # 3. Setup inicial
    company = frappe.get_doc({
        "doctype": "Company",
        "company_name": tenant_name,
        "country": "Bolivia",
        "default_currency": "BOB"
    }).insert()

    # 4. Return tenant info
    return {
        "site": site_name,
        "company": company.name,
        "admin_email": admin_email
    }
```

#### 3.3 Website Builder por Tenant
**Prioridad**: MEDIA

Tareas:
- [ ] Integrar Frappe Website Builder
- [ ] Templates personalizables
- [ ] Integración con catálogo de productos
- [ ] SEO optimization

### 🎯 FASE 4: E-COMMERCE & AVANZADO

#### 4.1 E-commerce
- [ ] Tienda online por tenant
- [ ] Carrito de compras
- [ ] Pasarelas de pago Bolivia
- [ ] Integración con inventario

#### 4.2 Integraciones Bolivia
- [ ] Integración bancaria (BNB, Banco Unión)
- [ ] Pasarelas de pago (Pagosnet, Tigo Money)
- [ ] Envíos (correos Bolivia)

---

## 💻 COMANDOS ÚTILES

### Docker

```bash
# Levantar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f backend

# Acceder al contenedor
docker-compose exec backend bash

# Reiniciar servicios
docker-compose restart backend
```

### Frappe Bench

```bash
# Dentro del contenedor backend
bench --site nexo.local migrate
bench --site nexo.local clear-cache
bench --site nexo.local console

# Crear DocType
bench --site nexo.local new-doctype "Nombre DocType"

# Instalar app
bench --site nexo.local install-app nexo_core

# Tests
bench --site nexo.local run-tests --app nexo_core
```

### Git

```bash
# Crear feature branch
git checkout -b feature/nombre-feature

# Commit
git add .
git commit -m "Add: descripción del cambio"

# Push
git push -u origin feature/nombre-feature
```

---

## 🎨 CONVENCIONES DE CÓDIGO

### Python (Frappe)

```python
# Naming: snake_case
def calculate_iva(amount):
    """
    Docstring descriptivo

    Args:
        amount: Descripción

    Returns:
        float: Descripción
    """
    return amount * 0.13

# DocTypes: PascalCase
class PlanCuentasBolivia(Document):
    pass
```

### JavaScript

```javascript
// Naming: camelCase
function formatCurrency(amount) {
    return `Bs ${amount.toFixed(2)}`;
}

// Frappe client scripts
frappe.ui.form.on('Sales Invoice', {
    refresh: function(frm) {
        // Lógica
    }
});
```

### Commits

```
Add: Nueva funcionalidad
Update: Mejora a existente
Fix: Corrección de bug
Docs: Documentación
Test: Tests
Refactor: Refactorización
```

---

## 🧪 TESTING

### Estructura de Tests

```python
# test_plan_cuentas_bolivia.py
import frappe
import unittest

class TestPlanCuentasBolivia(unittest.TestCase):
    def setUp(self):
        # Setup antes de cada test
        pass

    def test_create_account(self):
        """Test creación de cuenta"""
        account = frappe.get_doc({
            "doctype": "Plan Cuentas Bolivia",
            "account_number": "1111",
            "account_name": "Caja"
        }).insert()

        self.assertEqual(account.account_number, "1111")

    def tearDown(self):
        # Cleanup
        frappe.db.rollback()
```

### Ejecutar Tests

```bash
# Todos los tests
bench --site nexo.local run-tests --app nexo_bolivia

# Test específico
bench --site nexo.local run-tests nexo_bolivia.tests.test_plan_cuentas_bolivia
```

---

## 📚 RECURSOS Y REFERENCIAS

### Documentación Frappe
- [Frappe Framework Docs](https://frappeframework.com/docs)
- [ERPNext Developer Guide](https://frappeframework.com/docs/user/en/guides)
- [DocType API](https://frappeframework.com/docs/user/en/api/document)

### Bolivia Compliance
- [SIN - Impuestos Nacionales](https://www.impuestos.gob.bo/)
- [SIAT - Sistema de facturación](https://siat.impuestos.gob.bo/)
- Plan contable: Ver `apps/nexo_bolivia/nexo_bolivia/config/bolivia.py`

### Frappe DocType Structure

```python
{
    "doctype": "DocType",
    "name": "Plan Cuentas Bolivia",
    "fields": [
        {
            "fieldname": "account_number",
            "fieldtype": "Data",
            "label": "Número de Cuenta",
            "reqd": 1
        },
        {
            "fieldname": "account_name",
            "fieldtype": "Data",
            "label": "Nombre de Cuenta",
            "reqd": 1
        }
    ]
}
```

---

## 🔧 TROUBLESHOOTING

### Problemas Comunes

**1. Error: "Site does not exist"**
```bash
# Crear site
docker-compose exec backend bench new-site nexo.local --admin-password admin
```

**2. Error de permisos**
```bash
# Dar permisos
docker-compose exec backend chown -R frappe:frappe /home/frappe/frappe-bench
```

**3. App no aparece**
```bash
# Reinstalar app
docker-compose exec backend bench get-app /home/frappe/frappe-bench/apps/nexo_core
docker-compose exec backend bench --site nexo.local install-app nexo_core
```

**4. Cambios no se reflejan**
```bash
# Clear cache
docker-compose exec backend bench --site nexo.local clear-cache
docker-compose exec backend bench --site nexo.local migrate
```

---

## ✅ CHECKLIST ANTES DE CADA COMMIT

- [ ] Código sigue convenciones
- [ ] Tests pasan
- [ ] Documentación actualizada
- [ ] No hay credenciales hardcodeadas
- [ ] Cambios probados localmente
- [ ] Commit message descriptivo

---

## 🎯 PRÓXIMOS PASOS INMEDIATOS

**Tu trabajo ahora es continuar con la Fase 2**:

1. **Empezar con Contabilidad Bolivia**:
   - Crear DocType "Plan Cuentas Bolivia"
   - Implementar fixtures con plan contable
   - Tests unitarios

2. **Configurar Impuestos**:
   - Tax Templates IVA, IT, IUE
   - Hooks en Sales/Purchase Invoice
   - Cálculos automáticos

3. **Facturación SIN (Base)**:
   - Cliente API SIN (piloto)
   - DocType Factura Electrónica
   - Generación QR básica

**Prioriza en este orden**: Contabilidad → Impuestos → Facturación SIN

---

## 📞 SOPORTE

Si tienes dudas:
1. Revisa documentación en `/docs`
2. Consulta README.md de cada app
3. Ver ARCHITECTURE.md para entender el sistema

---

## 🎉 ¡IMPORTANTE!

- Mantén código limpio y documentado
- Sigue la estructura establecida
- Todos los desarrollos deben funcionar para Bolivia
- Piensa en multi-tenancy en cada feature
- Cumplimiento normativo es CRÍTICO

**¡Adelante con el desarrollo! 🚀🇧🇴**

---

**Autor**: Aero
**Versión**: 1.0
**Fecha**: Diciembre 2024
