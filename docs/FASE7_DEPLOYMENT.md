# Fase 7: Testing End-to-End, Integración y Deployment

## Descripción General

Fase 7 implementa la infraestructura completa de testing, integración continua, deployment y monitoreo para preparar Nexo para producción. Incluye tests E2E, integración, performance y seguridad, CI/CD pipelines, Docker production-ready, deployment scripts automatizados y monitoring completo.

## Contenidos

1. [Testing](#testing)
2. [CI/CD Pipeline](#cicd-pipeline)
3. [Docker & Containers](#docker--containers)
4. [Deployment](#deployment)
5. [Monitoring & Observability](#monitoring--observability)
6. [Troubleshooting](#troubleshooting)

---

## Testing

### Estructura de Tests

```
tests/
├── e2e/                          # End-to-End tests
│   ├── test_purchase_to_payment.py
│   ├── test_sin_integration.py
│   ├── test_ecommerce_flow.py
│   ├── test_multi_tenant.py
│   └── test_tenant_provisioning.py
│
├── integration/                  # Integration tests
│   ├── test_tax_engine_integration.py
│   ├── test_payroll_integration.py
│   ├── test_reporting_integration.py
│   └── test_api_integration.py
│
├── performance/                  # Performance tests
│   └── test_load.py
│
├── security/                     # Security tests
│   └── test_authentication_authorization.py
│
└── conftest.py                   # Pytest configuration
```

### Ejecutar Tests

```bash
# Tests unitarios (Frappe)
cd frappe-bench
bench --site test_site run-tests --app nexo_core
bench --site test_site run-tests --app nexo_bolivia

# Tests E2E
pytest tests/e2e/ -v

# Tests de integración
pytest tests/integration/ -v

# Tests de performance
pytest tests/performance/ -v

# Tests de seguridad
pytest tests/security/ -v

# Todos los tests
pytest tests/ -v
```

### Fixtures Disponibles

```python
# Fixtures en conftest.py
@pytest.fixture
def test_company()          # Compañía de prueba
def test_supplier()         # Proveedor de prueba
def test_customer()         # Cliente de prueba
def test_item()             # Artículo de prueba
def create_purchase_invoice  # Factory para crear PO
def create_sales_invoice     # Factory para crear SI
def mock_siat_api()          # Mock API de SIAT
```

---

## CI/CD Pipeline

### GitHub Actions Workflows

#### 1. Tests (`.github/workflows/tests.yml`)

Se ejecuta en:
- Push a `main` y `develop`
- Pull requests a `main` y `develop`

Pasos:
1. Setup Python 3.10
2. Instalar Frappe Bench
3. Instalar apps (ERPNext, nexo_core, nexo_bolivia)
4. Crear site de prueba
5. Ejecutar tests unitarios
6. Ejecutar E2E tests
7. Ejecutar integration tests
8. Ejecutar performance tests
9. Ejecutar security tests
10. Generar coverage report
11. Upload a Codecov

#### 2. Deploy Staging (`.github/workflows/deploy-staging.yml`)

Se ejecuta en:
- Push a `develop` branch

Pasos:
1. Conexión SSH a servidor staging
2. Backup automático
3. Git pull de develop
4. Ejecutar deploy.sh
5. Smoke tests
6. Notificación Slack

#### 3. Deploy Production (`.github/workflows/deploy-prod.yml`)

Se ejecuta en:
- Release publicado
- Workflow dispatch manual

Pasos:
1. Verificar que tests pasaron
2. Crear backup de producción
3. Blue-Green deployment
4. Health checks
5. Smoke tests
6. Rollback automático si falla
7. Notificación Slack
8. Crear GitHub release notes
9. Crear issue si falla

### Requisitos para CI/CD

GitHub Secrets requeridos:
- `STAGING_HOST` - Host del servidor staging
- `STAGING_USER` - Usuario SSH para staging
- `PROD_HOST` - Host del servidor de producción
- `PROD_USER` - Usuario SSH para producción
- `SSH_KEY` - Clave SSH privada
- `SLACK_WEBHOOK_URL` - URL para notificaciones Slack

---

## Docker & Containers

### Dockerfile Production

```dockerfile
FROM frappe/erpnext:v15

# Copia Nexo apps
COPY apps/nexo_core /home/frappe/frappe-bench/apps/nexo_core
COPY apps/nexo_bolivia /home/frappe/frappe-bench/apps/nexo_bolivia

# Instala apps
RUN bench get-app nexo_core && \
    bench get-app nexo_bolivia && \
    bench build

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:8000/api/method/ping || exit 1

EXPOSE 8000 8001
```

### Docker Compose Production

Servicios incluidos:

1. **mariadb** - Base de datos principal
2. **redis-cache** - Cache en memoria
3. **redis-queue** - Cola de trabajos
4. **redis-socketio** - WebSockets
5. **erpnext** - Aplicación Frappe/ERPNext
6. **erpnext-worker** - Worker para background jobs
7. **erpnext-scheduler** - Scheduler para tareas programadas
8. **nginx** - Reverse proxy con SSL/TLS
9. **prometheus** - Monitoring
10. **grafana** - Dashboards

### Levantar Stack Production

```bash
# Copiar .env.example a .env
cp .env.example .env

# Configurar variables
export DB_PASSWORD=securepassword
export ADMIN_PASSWORD=adminpassword
export GRAFANA_ADMIN_PASSWORD=grafanapassword

# Levantar servicios
cd deployment/docker
docker-compose -f docker-compose.prod.yml up -d

# Ver logs
docker-compose -f docker-compose.prod.yml logs -f

# Verificar salud
docker-compose -f docker-compose.prod.yml ps
```

### Configuración SSL/TLS

```bash
# Crear directorio SSL
mkdir -p deployment/docker/ssl

# Copiar certificados (Let's Encrypt o similar)
cp /etc/letsencrypt/live/nexo.bo/fullchain.pem deployment/docker/ssl/cert.pem
cp /etc/letsencrypt/live/nexo.bo/privkey.pem deployment/docker/ssl/key.pem

# Permisos
chmod 600 deployment/docker/ssl/key.pem
```

---

## Deployment

### Deployment Scripts

#### 1. deploy.sh

Script principal de deployment.

```bash
# Deployment a staging
./deployment/scripts/deploy.sh staging

# Deployment a producción
./deployment/scripts/deploy.sh production
```

Pasos:
1. Pre-deployment checks
2. Backup
3. Git pull
4. Update dependencies
5. Database migrations
6. Build assets
7. Restart services
8. Health checks

#### 2. backup.sh

Crea backups automáticos.

```bash
# Backup manual
./deployment/scripts/backup.sh manual

# Backup automático (parte del deploy)
./deployment/scripts/backup.sh staging
```

Backup incluye:
- Base de datos
- Sites (files, configuraciones)
- Applications
- SSL certificates

#### 3. restore.sh

Restaura desde backup.

```bash
# Restaurar últimos backup
./deployment/scripts/restore.sh staging

# Restaurar backup específico
./deployment/scripts/restore.sh staging nexo_backup_staging_20240101_120000
```

#### 4. migrate.sh

Ejecuta migraciones de base de datos.

```bash
./deployment/scripts/migrate.sh staging
./deployment/scripts/migrate.sh production
```

#### 5. health_check.sh

Verifica salud del sistema.

```bash
# Verificar todos
./deployment/scripts/health_check.sh all

# Verificar staging
./deployment/scripts/health_check.sh staging

# Verificar producción
./deployment/scripts/health_check.sh production
```

Chequea:
- HTTP/HTTPS connectivity
- API endpoints
- Database
- Redis services
- Disk space
- Memory
- Docker containers
- SIN integration
- E-commerce module
- Payroll module

### Estrategias de Deployment

#### Blue-Green Deployment

```bash
# Mantener dos ambientes: Blue (actual) y Green (nuevo)
# 1. Deploy a Green
# 2. Test Green
# 3. Switch traffic Blue -> Green
# 4. Green se vuelve Blue

./deployment/scripts/deploy.sh production  # Usa blue-green internamente
```

#### Rolling Deployment

```bash
# Actualizar servidores uno a uno
# Útil para clusters multi-node

# Ver docker-compose.prod.yml:
# services:
#   erpnext:
#     deploy:
#       replicas: 3
#       update_config:
#         parallelism: 1
#         delay: 10s
```

### Variables de Entorno

`.env` required:

```bash
# Database
DB_HOST=mariadb
DB_NAME=nexo
DB_USER=frappe
DB_PASSWORD=securepassword
DB_ROOT_PASSWORD=rootpassword

# Application
SITE_NAME=nexo.local
ADMIN_PASSWORD=adminpassword
FRAPPE_PORT=8000

# Redis
REDIS_CACHE=redis-cache:6379/1
REDIS_QUEUE=redis-queue:6379/1
REDIS_SOCKETIO=redis-socketio:6379/1

# Monitoring
GRAFANA_ADMIN_PASSWORD=grafanapassword

# Optional
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=user@example.com
SMTP_PASSWORD=password
```

---

## Monitoring & Observability

### Prometheus

**Ubicación:** `deployment/monitoring/prometheus/prometheus.yml`

Scrapers configurados:
- Prometheus itself
- ERPNext (8000)
- MariaDB exporter (9104)
- Redis exporters
- Node exporter (system metrics)
- Nginx
- cAdvisor (Docker stats)

Acceder a Prometheus:
```
http://localhost:9090
```

### Alert Rules

**Ubicación:** `deployment/monitoring/prometheus/alert_rules.yml`

Alertas configuradas para:
- Service availability
- Database status
- CPU/Memory/Disk usage
- Database replication lag
- Slow queries
- HTTP error rates
- API latency
- Container restarts
- SSL certificate expiry
- Backup failures

### Grafana

**Ubicación:** `deployment/monitoring/grafana/`

Credenciales por defecto:
- Usuario: `admin`
- Password: Definida en `GRAFANA_ADMIN_PASSWORD`

Acceder a Grafana:
```
http://localhost:3000
```

#### Dashboards Incluidos

1. **System Metrics**
   - CPU usage
   - Memory usage
   - Disk usage
   - Network traffic
   - Disk I/O
   - System load

2. **Application Metrics**
   - Request rate
   - Response time (p95)
   - HTTP error rate
   - Database connections
   - Queries per second
   - Cache hit rate
   - Redis memory usage
   - Queue depth
   - Exception rate
   - Document operations

### Logging

Logs disponibles en:

```bash
# Docker logs
docker-compose -f deployment/docker/docker-compose.prod.yml logs erpnext
docker-compose -f deployment/docker/docker-compose.prod.yml logs -f mariadb

# Archivos
./logs/error.log       # Logs de errores
./logs/access.log      # Logs de acceso Nginx

# Frappe logs
sites/nexo/logs/
```

### Métricas Custom

Para agregar métricas custom en Frappe:

```python
# En tu app
from prometheus_client import Counter, Histogram
import time

document_created = Counter(
    'document_created_total',
    'Total documents created',
    ['doctype']
)

document_create_duration = Histogram(
    'document_create_duration_seconds',
    'Time to create document',
    ['doctype']
)

@frappe.hook
def on_document_created(doc):
    document_created.labels(doctype=doc.doctype).inc()
```

---

## Troubleshooting

### Health Check Falló

```bash
# 1. Revisar logs
docker-compose -f deployment/docker/docker-compose.prod.yml logs

# 2. Verificar servicios
docker-compose -f deployment/docker/docker-compose.prod.yml ps

# 3. Restart service
docker-compose -f deployment/docker/docker-compose.prod.yml restart erpnext

# 4. Check connectivity
curl -f http://localhost:8000/api/method/ping

# 5. Verificar database
docker-compose -f deployment/docker/docker-compose.prod.yml exec -T mariadb \
  mysqladmin -u frappe -p<password> ping
```

### Database Errors

```bash
# Conectar a database
docker-compose -f deployment/docker/docker-compose.prod.yml exec -T mariadb \
  mysql -u frappe -p<password> nexo

# Verificar integridad
CHECK TABLE tabSales_Invoice;

# Optimize tables
OPTIMIZE TABLE tabSales_Invoice;

# Ejecutar migrations
./deployment/scripts/migrate.sh production
```

### Memory Leaks

```bash
# Verificar memoria
free -h

# Ver uso por container
docker stats

# Restart container que consume mucho
docker-compose -f deployment/docker/docker-compose.prod.yml restart erpnext-worker
```

### Deployment Falló - Rollback

```bash
# Rollback automático en deploy
./deployment/scripts/deploy.sh production  # Si falla, revierte automáticamente

# Rollback manual
./deployment/scripts/restore.sh production nexo_backup_production_20240101_120000
```

### Performance Issues

```bash
# Revisar Prometheus
http://localhost:9090

# Revisar Grafana
http://localhost:3000

# Verificar queries lentas
docker-compose -f deployment/docker/docker-compose.prod.yml exec -T mariadb \
  mysql -u frappe -p<password> nexo -e "SHOW VARIABLES LIKE 'slow_query_log%';"

# Verificar Redis
docker-compose -f deployment/docker/docker-compose.prod.yml exec -T redis-cache \
  redis-cli INFO stats
```

### SSL Certificate Issues

```bash
# Verificar certificado
openssl x509 -in deployment/docker/ssl/cert.pem -text -noout

# Renovar (Let's Encrypt)
certbot renew --nginx

# Copiar nuevos certificados
cp /etc/letsencrypt/live/nexo.bo/fullchain.pem deployment/docker/ssl/cert.pem
cp /etc/letsencrypt/live/nexo.bo/privkey.pem deployment/docker/ssl/key.pem

# Reload Nginx
docker-compose -f deployment/docker/docker-compose.prod.yml exec nginx nginx -s reload
```

---

## Recursos

- [Frappe Deployment Guide](https://frappeframework.com/docs/user/en/deployment)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)

## Contacto & Soporte

Para preguntas o issues, contactar al equipo de desarrollo de Nexo.
