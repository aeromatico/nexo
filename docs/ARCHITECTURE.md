# Arquitectura Técnica - Nexo ERP

**Documentación de Arquitectura del Sistema**

---

## Tabla de Contenidos

1. [Overview](#overview)
2. [Stack Tecnológico](#stack-tecnológico)
3. [Arquitectura Multi-tenant](#arquitectura-multi-tenant)
4. [Componentes del Sistema](#componentes-del-sistema)
5. [Flujo de Datos](#flujo-de-datos)
6. [Base de Datos](#base-de-datos)
7. [Seguridad](#seguridad)
8. [Escalabilidad](#escalabilidad)

---

## Overview

Nexo ERP es una plataforma SaaS multi-tenant construida sobre Frappe Framework y ERPNext, diseñada específicamente para el mercado boliviano.

### Principios de Diseño

- **Multi-tenancy**: Aislamiento completo de datos por tenant
- **Modularidad**: Apps independientes y reutilizables
- **Escalabilidad**: Diseño horizontal y vertical
- **Compliance**: Cumplimiento normativo boliviano
- **Performance**: Cache distribuido y procesamiento asíncrono

---

## Stack Tecnológico

### Backend Stack

```
┌─────────────────────────────────────┐
│     Frappe Framework (Python)       │
│  ├── ORM & Database Abstraction     │
│  ├── REST & WebSocket APIs          │
│  ├── Background Jobs (RQ)           │
│  └── Authentication & Permissions   │
└─────────────────────────────────────┘
              ▼
┌─────────────────────────────────────┐
│          ERPNext Base               │
│  ├── Accounting                     │
│  ├── Sales & Purchase               │
│  ├── Inventory                      │
│  └── HR & Payroll                   │
└─────────────────────────────────────┘
              ▼
┌─────────────────────────────────────┐
│       Custom Apps (Nexo)            │
│  ├── nexo_core (Multi-tenant)       │
│  └── nexo_bolivia (Localization)    │
└─────────────────────────────────────┘
```

### Frontend Stack

```
┌─────────────────────────────────────┐
│         Frappe UI (Vue 3)           │
│  ├── Components Library             │
│  ├── State Management               │
│  └── Routing                        │
└─────────────────────────────────────┘
              ▼
┌─────────────────────────────────────┐
│       Custom Frontends              │
│  ├── Admin Dashboard                │
│  ├── Tenant Portal                  │
│  └── Website Builder                │
└─────────────────────────────────────┘
```

### Infrastructure Stack

```
┌────────────────┐
│  Docker Host   │
└───────┬────────┘
        │
   ┌────▼─────────────────────────┐
   │   Docker Compose             │
   ├──────────────────────────────┤
   │  ├── Nginx (Frontend)        │
   │  ├── Frappe (Backend)        │
   │  ├── MariaDB (Database)      │
   │  ├── Redis (Cache/Queue)     │
   │  ├── Workers (BG Jobs)       │
   │  └── Scheduler (Cron)        │
   └──────────────────────────────┘
```

---

## Arquitectura Multi-tenant

### Modelo de Multi-tenancy

Nexo implementa **multi-tenancy a nivel de base de datos** donde cada tenant tiene:

- Su propia base de datos MariaDB
- Sitio Frappe independiente
- Datos completamente aislados
- Configuración personalizable

```
┌─────────────────────────────────────────────────────────┐
│                    Nginx Load Balancer                  │
│  (SSL Termination + Routing por subdomain)              │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┬────────────┐
        │            │            │            │
    ┌───▼───┐   ┌───▼───┐   ┌───▼───┐   ┌───▼───┐
    │Tenant1│   │Tenant2│   │Tenant3│   │Tenant4│
    │.nexo  │   │.nexo  │   │.nexo  │   │.nexo  │
    │ .bo   │   │ .bo   │   │ .bo   │   │ .bo   │
    └───┬───┘   └───┬───┘   └───┬───┘   └───┬───┘
        │           │           │           │
        └───────────┴───────────┴───────────┘
                     │
        ┌────────────▼────────────────────────┐
        │    Frappe Bench (Multi-site)        │
        │                                     │
        │  ├── site: tenant1.nexo.bo          │
        │  │   └── DB: tenant1_db             │
        │  │                                  │
        │  ├── site: tenant2.nexo.bo          │
        │  │   └── DB: tenant2_db             │
        │  │                                  │
        │  ├── site: tenant3.nexo.bo          │
        │  │   └── DB: tenant3_db             │
        │  │                                  │
        │  └── site: tenant4.nexo.bo          │
        │      └── DB: tenant4_db             │
        └─────────────────────────────────────┘
                     │
        ┌────────────▼────────────────────────┐
        │         MariaDB Server              │
        │                                     │
        │  Database per Tenant:               │
        │  ├── tenant1_db                     │
        │  ├── tenant2_db                     │
        │  ├── tenant3_db                     │
        │  └── tenant4_db                     │
        └─────────────────────────────────────┘
```

### Provisioning de Tenants

Proceso automático de creación de tenants:

```python
# nexo_core/utils.py
def create_tenant(tenant_name, admin_email, admin_password):
    # 1. Validar nombre de tenant
    # 2. Crear nueva base de datos
    # 3. Crear sitio Frappe
    # 4. Instalar apps necesarias
    # 5. Configurar datos iniciales Bolivia
    # 6. Crear usuario administrador
    # 7. Configurar DNS/subdomain
    # 8. Provisionar SSL certificate
```

---

## Componentes del Sistema

### 1. Frontend (Nginx)

**Puerto**: 8080 (HTTP), 443 (HTTPS en producción)

Responsabilidades:
- Reverse proxy a backend Frappe
- SSL termination
- Routing por subdomain
- Servir archivos estáticos
- Load balancing (producción)
- Rate limiting
- Compresión gzip

Configuración:
```nginx
server {
    listen 8080;
    server_name *.nexo.bo;

    location / {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Frappe-Site-Name $host;
    }
}
```

### 2. Backend (Frappe)

**Puerto**: 8000 (interno)

Responsabilidades:
- API REST
- Lógica de negocio
- ORM & Database access
- Autenticación & autorización
- Renderizado de templates
- Hooks & Events

### 3. Database (MariaDB)

**Puerto**: 3306

Responsabilidades:
- Almacenamiento persistente
- Una DB por tenant
- Transacciones ACID
- Backups automáticos

Schema por tenant:
- Tablas Frappe core (~150 tablas)
- Tablas ERPNext (~400 tablas)
- Tablas custom apps

### 4. Cache (Redis)

**3 Instancias Redis**:

#### redis-cache (Puerto 6379)
- Cache de queries
- Session storage
- TTL: variable

#### redis-queue (Puerto 6379)
- Cola de trabajos background
- Job results
- Persistencia: sí

#### redis-socketio (Puerto 6379)
- Pub/sub para real-time
- WebSocket connections
- Persistencia: no

### 5. Queue Workers

Procesan trabajos en background:
- Envío de emails
- Generación de reportes
- Sincronización SIN
- Backups
- Procesamiento masivo

### 6. Scheduler

Ejecuta tareas programadas:
- Cron jobs diarios/horarios
- Limpieza de sesiones
- Actualización de métricas
- Sincronización automática

### 7. SocketIO Server

**Puerto**: 9000

Comunicación real-time:
- Notificaciones en vivo
- Updates de documentos
- Chat interno
- Colaboración multi-usuario

---

## Flujo de Datos

### Request Flow

```
1. Usuario → 2. Nginx → 3. Frappe Backend → 4. MariaDB
                ↓                              ↑
           5. Redis Cache ←────────────────────┘
                ↓
           6. Response → Usuario
```

**Paso a paso**:

1. **Usuario**: Hace request HTTP/HTTPS
2. **Nginx**:
   - Identifica tenant por subdomain
   - Aplica SSL
   - Rate limiting
   - Forward a Frappe
3. **Frappe Backend**:
   - Autentica usuario
   - Identifica sitio/tenant
   - Verifica permisos
   - Procesa lógica de negocio
4. **MariaDB**:
   - Query a DB del tenant
   - Retorna datos
5. **Redis Cache**:
   - Cache hit/miss
   - Store results
6. **Response**: JSON/HTML al cliente

### Background Job Flow

```
API Request → Queue Job → Redis Queue → Worker → Process → DB → Result
```

### Real-time Communication Flow

```
Client A → SocketIO Server → Redis Pub/Sub → SocketIO Server → Client B
```

---

## Base de Datos

### Esquema Multi-tenant

Cada tenant tiene su propia base de datos:

```sql
-- Database per tenant
CREATE DATABASE `tenant1_nexo_bo`;
CREATE DATABASE `tenant2_nexo_bo`;
CREATE DATABASE `tenant3_nexo_bo`;

-- Tables dentro de cada DB
-- Frappe Core tables (~150)
-- ERPNext tables (~400)
-- Custom app tables (~50)
```

### Tablas Principales

#### nexo_core

- `tabTenant` - Información de tenants
- `tabTenantPlan` - Planes de suscripción
- `tabTenantUsage` - Métricas de uso
- `tabTenantInvoice` - Facturación SaaS

#### nexo_bolivia

- `tabSINConfig` - Configuración SIN
- `tabElectronicInvoice` - Facturas electrónicas
- `tabTaxBolivia` - Configuración impuestos
- `tabBolivianHolidays` - Días festivos

### Backups

**Estrategia de Backup**:
- Full backup diario (2 AM)
- Incremental cada 6 horas
- Retención: 30 días
- Almacenamiento: S3/MinIO
- Encriptación: AES-256

---

## Seguridad

### Autenticación

- Session-based auth
- JWT tokens para API
- OAuth 2.0 (opcional)
- 2FA (Two-Factor Auth)

### Autorización

Modelo de permisos Frappe:
- Role-based access control (RBAC)
- Document-level permissions
- Field-level permissions
- API rate limiting

### Aislamiento de Datos

- Base de datos separada por tenant
- No shared tables entre tenants
- Queries siempre con tenant filter
- Logs auditables por tenant

### Encriptación

- SSL/TLS en tránsito
- Passwords hasheados (bcrypt)
- Datos sensibles encriptados
- Backups encriptados

### Compliance Bolivia

- Cumplimiento normativa SIN
- Protección datos personales
- Logs de auditoría fiscal
- Retención de facturas 7 años

---

## Escalabilidad

### Escalamiento Horizontal

**Backend**:
```yaml
backend:
  deploy:
    replicas: 3  # Múltiples instancias
```

**Workers**:
```yaml
queue-worker:
  deploy:
    replicas: 5  # Más workers para jobs
```

### Escalamiento Vertical

- Más CPU/RAM por contenedor
- Optimización de queries
- Índices en DB
- Cache agresivo

### Database Scaling

- Read replicas
- Connection pooling
- Query optimization
- Particionamiento por tenant

### Cache Strategy

**3-tier caching**:

1. **Browser cache**: Assets estáticos
2. **Redis cache**: Queries frecuentes
3. **DB query cache**: MariaDB built-in

### CDN (Producción)

- Archivos estáticos en CDN
- Imágenes optimizadas
- JS/CSS minificados
- Geo-distribution

---

## Monitoreo

### Métricas Clave

- Response time
- Error rate
- Database connections
- Queue length
- Memory usage
- CPU usage
- Disk I/O

### Logs

- Application logs
- Access logs
- Error logs
- Audit logs (Bolivia compliance)

### Alertas

- Downtime detection
- High resource usage
- Failed jobs
- Security events

---

## Diagrama Completo

```
┌────────────────────────────────────────────────────────────┐
│                      INTERNET                              │
└─────────────────────┬──────────────────────────────────────┘
                      │
                ┌─────▼─────┐
                │    CDN    │ (Producción)
                └─────┬─────┘
                      │
         ┌────────────▼────────────┐
         │   Load Balancer (Nginx) │
         │   *.nexo.bo             │
         └────────────┬────────────┘
                      │
    ┌─────────────────┼─────────────────┐
    │                 │                 │
┌───▼───┐        ┌───▼───┐        ┌───▼───┐
│Backend│        │Backend│        │Backend│
│   #1  │        │   #2  │        │   #3  │
└───┬───┘        └───┬───┘        └───┬───┘
    │                │                │
    └────────────────┼────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
   ┌────▼───┐   ┌───▼────┐  ┌───▼─────┐
   │MariaDB │   │ Redis  │  │ MinIO   │
   │ Master │   │Cluster │  │ Storage │
   └────┬───┘   └────────┘  └─────────┘
        │
   ┌────▼───┐
   │MariaDB │
   │ Slave  │
   └────────┘
```

---

## Conclusión

La arquitectura de Nexo ERP está diseñada para:

✅ **Escalabilidad**: Soportar miles de tenants
✅ **Performance**: Respuestas < 200ms
✅ **Seguridad**: Aislamiento completo
✅ **Compliance**: Normativa boliviana
✅ **Mantenibilidad**: Código modular
✅ **Costos**: Optimización de recursos

---

**Autor**: Aero
**Versión**: 1.0
**Última actualización**: Diciembre 2024
