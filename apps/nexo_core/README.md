# Nexo Core

**Módulo Multi-tenant SaaS de Nexo ERP**

**Versión**: 1.0.0
**Estado**: Completado ✅
**Licencia**: GNU General Public License (v3)

## Descripción

`nexo_core` es el módulo principal que proporciona funcionalidades completas de **multi-tenancy** y gestión de tenants para la plataforma SaaS Nexo ERP. Implementa provisioning automático, APIs REST, métricas en tiempo real y dashboards administrativos.

## Características Principales

✅ **Creación Automática de Tenants**: Provisioning completo y automático de nuevos sites Frappe
✅ **Gestión de Planes**: Soporte para múltiples planes de suscripción (Basic, Professional, Enterprise)
✅ **Control de Cuotas**: Límites de usuarios, almacenamiento y recursos por plan
✅ **Métricas en Tiempo Real**: Recolección y seguimiento de uso de recursos
✅ **APIs REST Completas**: 15+ endpoints para gestión programática
✅ **Dashboards Intuitivos**: Dashboards para admin y tenants individuales
✅ **Tests Exhaustivos**: 45+ tests con cobertura > 75%
✅ **Aislamiento Total**: Separación completa de datos entre tenants
✅ **Localización Bolivia**: Configuración automática para Bolivia

## Estructura

```
nexo_core/
├── nexo_core/
│   ├── doctype/                    # Tipos de documento
│   │   ├── tenant/                 # DocType principal de Tenant
│   │   ├── subscription_plan/      # Planes de suscripción
│   │   ├── tenant_usage/           # Métricas de uso
│   │   └── tenant_app/             # Child table de apps
│   ├── provisioning/               # Módulo de provisioning automático
│   │   ├── site_creator.py         # Creación de sites
│   │   ├── dns_manager.py          # Gestión DNS
│   │   ├── app_installer.py        # Instalación de apps
│   │   └── config_manager.py       # Configuración inicial
│   ├── api/                        # REST API endpoints
│   │   ├── tenant_api.py           # APIs de tenants
│   │   ├── provisioning_api.py     # APIs de provisioning
│   │   ├── metrics_api.py          # APIs de métricas
│   │   └── tests/                  # Tests de APIs
│   ├── dashboard/                  # Dashboards
│   │   ├── admin_dashboard.py      # Dashboard para admin
│   │   └── tenant_dashboard.py     # Dashboard para tenants
│   ├── tasks/                      # Tareas programadas
│   │   ├── daily.py                # Tareas diarias
│   │   └── hourly.py               # Tareas cada hora
│   ├── fixtures/                   # Datos iniciales
│   │   └── subscription_plans.json # Planes predefinidos
│   ├── hooks.py                    # Configuración de hooks
│   └── utils.py                    # Funciones utilitarias
├── README.md                       # Este archivo
└── docs/
    └── FASE3_MULTITENANT.md        # Documentación detallada
```

## Instalación Rápida

### Prerrequisitos

- Frappe Framework >= 15.0
- ERPNext >= 15.0
- nexo_bolivia app instalada
- Python >= 3.8

### Pasos

```bash
# 1. Obtener la app
cd /path/to/bench
bench get-app /path/to/nexo_core

# 2. Instalar en el site
bench --site sitename install-app nexo_core

# 3. Crear planes de suscripción (automático via fixtures)
bench --site sitename migrate

# 4. Habilitar scheduler para tareas automáticas
bench --site sitename enable-scheduler

# 5. Iniciar los workers
bench start
```

## Uso Básico

### Crear un Nuevo Tenant (UI)

1. Ir a: `Setup > Tenant > + New`
2. Completar formulario:
   - **Tenant Name**: `empresa1`
   - **Subdomain**: `empresa1`
   - **Company Name**: `Empresa Ltda`
   - **NIT**: `1234567890123`
   - **Admin Email**: `admin@empresa.com`
   - **Password**: `SecurePassword123`
   - **Plan**: `Professional`
3. Guardar
4. El provisioning se dispara automáticamente
5. Esperar a que el status cambie a "Active"

### Crear Tenant vía API

```bash
curl -X POST http://localhost:8000/api/method/nexo_core.api.provisioning_api.provision_new_tenant \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_name": "empresa1",
    "subdomain": "empresa1",
    "company_name": "Empresa Ltda",
    "nit": "1234567890123",
    "admin_email": "admin@empresa.com",
    "admin_password": "SecurePassword123",
    "subscription_plan": "Professional"
  }'
```

### Crear Tenant vía Python

```python
import frappe

# Crear documento
tenant = frappe.new_doc("Tenant")
tenant.tenant_name = "empresa1"
tenant.subdomain = "empresa1"
tenant.company_name = "Empresa Ltda"
tenant.nit = "1234567890123"
tenant.admin_email = "admin@empresa.com"
tenant.admin_password = "SecurePassword123"
tenant.subscription_plan = "Professional"

# Guardar e iniciar provisioning
tenant.insert()
# El provisioning se dispara automáticamente en background
```

## APIs Principales

### Tenants

```bash
# Crear tenant
POST /api/method/nexo_core.api.tenant_api.create_tenant

# Obtener información
GET /api/method/nexo_core.api.tenant_api.get_tenant_info?tenant_name=empresa1

# Listar todos
GET /api/method/nexo_core.api.tenant_api.get_all_tenants

# Suspender
POST /api/method/nexo_core.api.tenant_api.suspend_tenant

# Activar
POST /api/method/nexo_core.api.tenant_api.activate_tenant

# Eliminar
POST /api/method/nexo_core.api.tenant_api.delete_tenant

# Actualizar plan
POST /api/method/nexo_core.api.tenant_api.upgrade_plan

# Obtener métricas
GET /api/method/nexo_core.api.tenant_api.get_tenant_metrics?tenant_name=empresa1

# Obtener planes disponibles
GET /api/method/nexo_core.api.tenant_api.get_available_plans
```

### Provisioning

```bash
# Provisionar nuevo tenant
POST /api/method/nexo_core.api.provisioning_api.provision_new_tenant

# Verificar subdominio disponible
GET /api/method/nexo_core.api.provisioning_api.check_subdomain_available?subdomain=empresa1

# Obtener estado de provisioning
GET /api/method/nexo_core.api.provisioning_api.get_provisioning_status?tenant_name=empresa1

# Reintentar provisioning fallido
POST /api/method/nexo_core.api.provisioning_api.retry_provisioning
```

### Métricas

```bash
# Métricas globales de plataforma
GET /api/method/nexo_core.api.metrics_api.get_platform_metrics

# Reporte de uso de tenant
GET /api/method/nexo_core.api.metrics_api.get_tenant_usage_report?tenant_name=empresa1

# Estado de cuota
GET /api/method/nexo_core.api.metrics_api.get_tenant_quota_status?tenant_name=empresa1

# Top tenants por métrica
GET /api/method/nexo_core.api.metrics_api.get_top_tenants?metric=storage&limit=10
```

## Planes de Suscripción

| Plan | Usuarios | Storage | Precio/mes | Features |
|------|----------|---------|-----------|----------|
| **Basic** | 5 | 1 GB | Bs. 29 | Facturación, Contabilidad |
| **Professional** | 15 | 5 GB | Bs. 79 | + Inventario, Nómina, SIN |
| **Enterprise** | Ilimitado | 20 GB | Bs. 199 | + Apps personalizadas |

## Dashboards

### Dashboard Admin
**URL**: `/app/tenant`

Información:
- Total de tenants (activos, trial, suspendidos)
- Revenue mensual
- Almacenamiento utilizado
- Top 10 tenants por uso
- Alertas y eventos

### Dashboard de Tenant
**URL**: Acceso automático en cada site

Información:
- Cuotas vs límites del plan
- Métricas de uso
- Historial de uso
- Alertas y recomendaciones

## Tests

Ejecutar tests:

```bash
# Todos los tests
bench test-app nexo_core

# Con verbosidad
bench test-app nexo_core -v

# Test específico
bench test-app nexo_core -p test_tenant

# Con cobertura
coverage run -m frappe.bench test-app nexo_core
coverage report
```

**Resumen**:
- Total: 45+ tests
- Cobertura: > 75%
- Módulos: DocTypes, APIs, Provisioning, Dashboards

## Documentación Completa

Para documentación detallada, ver:
- [`docs/FASE3_MULTITENANT.md`](../docs/FASE3_MULTITENANT.md) - Documentación técnica completa (800+ líneas)

## Troubleshooting

### Provisioning Falla

```bash
# Ver logs
tail -f logs/error.log

# Verificar que bench existe
bench --version

# Reintentar
curl -X POST http://localhost:8000/api/method/nexo_core.api.provisioning_api.retry_provisioning \
  -d "tenant_name=empresa1"
```

### Site No Accesible

```bash
# Verificar que el site existe
bench list-sites

# Verificar DNS
nslookup empresa1.nexo.bo

# Recrear el site (si es necesario)
# 1. Eliminar el tenant
# 2. Esperar cleanup
# 3. Crear el tenant nuevamente
```

### Métricas No Se Actualizan

```bash
# Habilitar scheduler
bench --site sitename enable-scheduler

# Ejecutar manualmente
bench execute nexo_core.doctype.tenant_usage.tenant_usage.collect_metrics
```

## Desarrollo

### Estructura de Código

```
# Convención de nombres
- DocTypes: PascalCase (Tenant, SubscriptionPlan)
- Funciones: snake_case (get_tenant_info)
- Constantes: UPPER_CASE (MAX_USERS)

# Type hints
def get_tenant_info(tenant_name: str) -> dict:

# Docstrings
def provision_tenant_site(tenant_name):
    """
    Provision a complete site for a new tenant

    Args:
        tenant_name: Name of the tenant
    """
```

### Agregar Nuevas APIs

```python
# En api/tenant_api.py
@frappe.whitelist(methods=['GET'])
def my_new_endpoint(param):
    """
    Description of the endpoint

    GET /api/method/nexo_core.api.tenant_api.my_new_endpoint?param=value
    """
    return {
        "success": True,
        "data": {}
    }
```

### Agregar Tests

```python
# En test_tenant_api.py
def test_my_new_endpoint(self):
    """Test the new endpoint"""
    result = my_new_endpoint("test_value")

    self.assertTrue(result["success"])
```

## Contribuir

Para contribuir al proyecto:

1. Crear rama desde `main`
2. Implementar cambios
3. Escribir tests (cobertura > 75%)
4. Crear pull request
5. Pasar review y tests

## Licencia

GNU General Public License (v3) - Ver LICENSE

## Autor

**Aero**
Email: admin@aero.bo
Web: https://aero.bo

---

**Última actualización**: Diciembre 2024
**Versión**: 1.0.0
**Estado**: Producción ✅
