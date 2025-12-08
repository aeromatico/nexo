# Nexo Core

**Módulo Core de Multi-tenancy para Nexo ERP**

## Descripción

`nexo_core` es el módulo principal que proporciona funcionalidades de multi-tenancy y gestión de tenants para la plataforma SaaS Nexo ERP.

## Características

- **Multi-tenancy**: Gestión de múltiples tenants en una sola instalación
- **Provisioning Automático**: Creación automática de sitios para nuevos tenants
- **Gestión de Recursos**: Control de cuotas y límites por tenant
- **Métricas y Analytics**: Seguimiento de uso y facturación
- **API REST**: Endpoints para gestión programática de tenants

## Estructura

```
nexo_core/
├── api/                 # REST API endpoints
├── config/             # Configuraciones
├── fixtures/           # Datos iniciales
├── hooks/              # Hooks de Frappe
├── public/             # Archivos estáticos
├── tasks/              # Tareas programadas
│   ├── daily.py       # Tareas diarias
│   └── hourly.py      # Tareas por hora
├── templates/          # Templates web
├── www/                # Páginas web
├── hooks.py           # Configuración de hooks
└── utils.py           # Funciones utilitarias
```

## Instalación

```bash
# Dentro del contenedor Frappe
bench get-app /home/frappe/frappe-bench/apps/nexo_core
bench --site [sitename] install-app nexo_core
```

## Uso

### Crear un Nuevo Tenant

```python
from nexo_core.utils import create_tenant

tenant = create_tenant(
    tenant_name="cliente1",
    admin_email="admin@cliente1.com",
    admin_password="secure_password"
)
```

### Obtener Información de Tenant

```python
from nexo_core.utils import get_tenant_info

info = get_tenant_info("cliente1")
```

## Desarrollo

Autor: **Aero**
Versión: 0.1.0
Licencia: GNU GPL v3
