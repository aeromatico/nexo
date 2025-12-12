# Guía de Instalación - Nexo ERP v1.0.0

Guía paso a paso para instalar Nexo ERP en tu entorno local o producción.

---

## Tabla de Contenidos

1. [Requisitos del Sistema](#requisitos-del-sistema)
2. [Instalación con Docker (Recomendado)](#instalación-con-docker-recomendado)
3. [Instalación Manual](#instalación-manual)
4. [Configuración Inicial](#configuración-inicial)
5. [Crear Primer Tenant](#crear-primer-tenant)
6. [Verificación y Pruebas](#verificación-y-pruebas)
7. [Troubleshooting](#troubleshooting)
8. [Producción](#producción)

---

## Requisitos del Sistema

### Hardware Mínimo
- **CPU**: 2 cores
- **RAM**: 4 GB
- **Almacenamiento**: 20 GB (mínimo), 50+ GB recomendado

### Hardware Recomendado
- **CPU**: 4+ cores
- **RAM**: 8+ GB
- **Almacenamiento**: 100+ GB SSD
- **Ancho de banda**: 10+ Mbps

### Software Requerido

#### Para Docker (Opción 1 - Recomendada)
- Docker 20.10+ ([Instalar Docker](https://docs.docker.com/get-docker/))
- Docker Compose 1.29+ ([Instalar Docker Compose](https://docs.docker.com/compose/install/))
- Git 2.25+
- 6 GB de espacio libre en disco

#### Para Instalación Manual (Opción 2)
- Python 3.10+
- Node.js 18+
- MySQL/MariaDB 10.6+
- Redis 7+
- Git 2.25+
- pip y npm

### Sistemas Operativos Soportados
- Linux (Ubuntu 20.04+, CentOS 8+, Debian 11+)
- macOS (12+)
- Windows 10+ (WSL2 recomendado)

---

## Instalación con Docker (Recomendado)

### Paso 1: Clonar el Repositorio

```bash
# Clonar repositorio
git clone https://github.com/aeromatico/nexo.git
cd nexo

# O con SSH (si tienes configurado)
git clone git@github.com:aeromatico/nexo.git
cd nexo
```

### Paso 2: Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar configuración
nano .env  # o usa tu editor favorito
```

**Configuración mínima en `.env`:**

```bash
# Frappe Bench
FRAPPE_VERSION=15
ERPNEXT_VERSION=15

# Database
DB_PASSWORD=your_secure_password_here
DB_ROOT_PASSWORD=your_root_password_here

# Redis
REDIS_PASSWORD=your_redis_password

# Sitio principal
SITE_NAME=nexo.local
ADMIN_PASSWORD=admin123

# Email (opcional pero recomendado)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# SSL (dejar vacío para desarrollo)
SSL_CERT_PATH=
SSL_KEY_PATH=

# Domain
DOMAIN=nexo.local  # o tu dominio real
```

### Paso 3: Construir y Levantar Servicios

```bash
# Construir imágenes Docker
docker-compose build

# Levantar servicios en background
docker-compose up -d

# Verificar servicios
docker-compose ps
```

**Salida esperada:**
```
NAME                  STATUS              PORTS
nexo-backend          Up 2 minutes        0.0.0.0:8000->8000/tcp
nexo-frontend         Up 2 minutes        0.0.0.0:8765->8080/tcp
nexo-socketio         Up 2 minutes        0.0.0.0:9000->9000/tcp
nexo-mariadb          Up 2 minutes        3306/tcp
nexo-redis-cache      Up 2 minutes        6379/tcp
nexo-redis-queue      Up 2 minutes        6379/tcp
nexo-redis-socketio   Up 2 minutes        6379/tcp
nexo-worker           Up 2 minutes
nexo-scheduler        Up 2 minutes
```

### Paso 4: Esperar a que Servicios Inicien

```bash
# Ver logs
docker-compose logs -f backend

# Esperar hasta ver este mensaje:
# "Starting Frappe development server on port 8000"
# (Presionar Ctrl+C para salir)

# O esperar 2-3 minutos y verificar acceso
sleep 120
curl http://localhost:8765
```

### Paso 5: Crear Sitio Principal

```bash
# Crear sitio nexo.local
docker-compose exec backend bench new-site nexo.local \
  --db-root-password=your_root_password_here \
  --admin-password=admin123

# Instalar ERPNext
docker-compose exec backend bench --site nexo.local install-app erpnext

# Instalar apps Nexo
docker-compose exec backend bench --site nexo.local install-app nexo_core
docker-compose exec backend bench --site nexo.local install-app nexo_bolivia

# Establecer como sitio default
docker-compose exec backend bench use nexo.local
```

### Paso 6: Acceder a Nexo ERP

Abre tu navegador y accede a:

```
http://localhost:8765
```

**Credenciales por defecto:**
- Usuario: `Administrator`
- Contraseña: `admin123` (la que configuraste)

---

## Instalación Manual

### Paso 1: Preparar Sistema Operativo

#### Ubuntu/Debian:
```bash
# Actualizar paquetes
sudo apt update && sudo apt upgrade -y

# Instalar dependencias
sudo apt install -y python3.10 python3.10-dev python3.10-venv \
  mariadb-server mysql-client redis-server nodejs npm git \
  build-essential libssl-dev libffi-dev python3-pip curl

# Iniciar servicios
sudo systemctl start mariadb
sudo systemctl start redis-server
```

#### CentOS/RHEL:
```bash
sudo yum install -y python310 python310-devel mariadb-server redis \
  nodejs npm git gcc openssl-devel
```

### Paso 2: Instalar Frappe Bench

```bash
# Crear directorio
mkdir -p ~/frappe && cd ~/frappe

# Crear entorno virtual
python3.10 -m venv bench-venv

# Activar entorno virtual
source bench-venv/bin/activate

# Instalar frappe-bench
pip install frappe-bench

# Inicializar bench
bench init frappe-bench --frappe-branch version-15
cd frappe-bench
```

### Paso 3: Obtener Apps

```bash
# ERPNext
bench get-app erpnext --branch version-15

# Nexo (clonar repositorio)
cd apps
git clone https://github.com/aeromatico/nexo.git nexo_repo
cp -r nexo_repo/apps/nexo_core .
cp -r nexo_repo/apps/nexo_bolivia .
cd ..

# Actualizar dependencias
bench setup requirements
```

### Paso 4: Crear Sitio

```bash
# Crear sitio
bench new-site nexo.local \
  --db-root-password=root_password \
  --admin-password=admin123

# Instalar apps
bench --site nexo.local install-app erpnext
bench --site nexo.local install-app nexo_core
bench --site nexo.local install-app nexo_bolivia

# Establecer como default
bench use nexo.local

# Iniciar servidor
bench start
```

**Acceso:**
```
http://localhost:8000
```

---

## Configuración Inicial

### Paso 1: Configuración de Empresa

1. Ir a: **Configuración > Empresa**
2. Editar empresa principal:
   - **País**: Bolivia
   - **Moneda**: BOB (Bolivianos)
   - **Zona Horaria**: America/La_Paz

### Paso 2: Configuración de Impuestos Bolivia

1. Ir a: **Nexo > Bolivia > Configuración SIN**
2. Configurar credenciales SIAT:
   - **NIT Empresa**: Tu NIT
   - **Razón Social**: Tu razón social
   - **Usuario SIAT**: Tu usuario
   - **Contraseña SIAT**: Tu contraseña
   - **Ambiente**: Test o Producción

### Paso 3: Configuración de Plan Contable

1. Ir a: **Nexo > Bolivia > Plan Cuentas Bolivia**
2. Hacer clic en **Sincronizar con ERPNext**
3. Verificar que las 75+ cuentas se crearon correctamente

### Paso 4: Configuración de Nómina

1. Ir a: **Nexo > Bolivia > Configuración Nómina**
2. Establecer:
   - **Salario Mínimo Vigente**: (consultar SBC)
   - **AFP**: 12.71%
   - **RC-IVA**: Habilitar si aplica
   - **Año Fiscal**: 2024 (o el año actual)

### Paso 5: Configuración de E-commerce (Opcional)

1. Ir a: **Nexo > E-commerce > Configuración E-commerce**
2. Configurar:
   - **Nombre Tienda**: Tu nombre
   - **Descripción**: Descripción de tu tienda
   - **Logo**: URL o archivo
   - **Pasarelas de Pago**:
     - Agregar Stripe (si usas)
     - Agregar QR Simple (si usas)
     - Agregar otros métodos

### Paso 6: Usuarios y Permisos

```bash
# Crear usuario administrativo
bench execute frappe.client.insert --args '{
  "doctype": "User",
  "email": "admin@miempresa.bo",
  "first_name": "Admin",
  "last_name": "Usuario",
  "password": "secure_password"
}'

# Asignar roles
bench execute frappe.client.insert --args '{
  "doctype": "User Role",
  "parenttype": "User",
  "parent": "admin@miempresa.bo",
  "role": "System Manager"
}'
```

---

## Crear Primer Tenant

Si instalaste con Docker:

```bash
# Acceder a backend
docker-compose exec backend bash

# Ejecutar API de creación de tenant
bench execute frappe.client.insert --args '{
  "doctype": "Tenant",
  "company_name": "Mi Primera Empresa",
  "subdomain": "empresa1",
  "plan": "professional",
  "country": "Bolivia"
}'
```

O vía API REST:

```bash
curl -X POST http://localhost:8000/api/method/nexo_core.api.create_tenant \
  -H "Authorization: token ADMIN_TOKEN:SECRET" \
  -H "Content-Type: application/json" \
  -d '{
    "subdomain": "empresa1",
    "company_name": "Mi Primera Empresa",
    "admin_email": "admin@empresa1.bo",
    "admin_password": "SecurePass123",
    "plan": "professional",
    "country_code": "BO",
    "nit": "9999999999"
  }'
```

---

## Verificación y Pruebas

### Verificar Instalación

```bash
# 1. Verificar acceso web
curl -I http://localhost:8765

# 2. Verificar base de datos
docker-compose exec mariadb mysql -u root -p$DB_ROOT_PASSWORD -e "SHOW DATABASES;"

# 3. Verificar Redis
docker-compose exec redis-cache redis-cli ping

# 4. Verificar health
docker-compose exec backend curl http://localhost:8000/health
```

### Ejecutar Tests

```bash
# Unit tests
docker-compose exec backend pytest apps/nexo_core/tests/
docker-compose exec backend pytest apps/nexo_bolivia/tests/

# E2E tests
docker-compose exec backend pytest tests/e2e/

# Todos los tests
docker-compose exec backend pytest tests/ -v --cov=apps
```

### Pruebas Manuales

1. **Crear factura de venta:**
   - Ir a: Ventas > Nueva Factura
   - Completar datos
   - Verificar cálculo de IVA automático
   - Guardar y enviar

2. **Verificar facturación SIN:**
   - Ir a: Factura de Venta
   - Buscar factura creada
   - Verificar que tenga CUF y QR
   - Descargar PDF

3. **Probar e-commerce:**
   - Acceder a: http://localhost:8765/store
   - Agregar producto al carrito
   - Proceder al checkout
   - Completar pago de prueba

---

## Troubleshooting

### Problema: "Connection refused" al acceder

```bash
# Verificar servicios
docker-compose ps

# Si algún servicio está down, reiniciar
docker-compose restart backend

# Ver logs
docker-compose logs -f
```

### Problema: Database error

```bash
# Reiniciar MariaDB
docker-compose restart mariadb

# Ver logs de DB
docker-compose logs mariadb

# Si persiste, verificar credenciales en .env
grep DB_PASSWORD .env
```

### Problema: Redis error

```bash
# Limpiar Redis
docker-compose exec redis-cache redis-cli FLUSHALL

# Reiniciar
docker-compose restart redis-cache redis-queue redis-socketio
```

### Problema: Assets no cargan

```bash
# Reconstruir assets
docker-compose exec backend bench build

# Limpiar cache
docker-compose exec backend bench clear-cache
```

### Problema: Permisos de archivo

```bash
# Fijar permisos
docker-compose exec backend bash
sudo chown -R frappe:frappe .

# Dentro del contenedor:
chown -R frappe:frappe /home/frappe
```

### Problema: Sitio no carga

```bash
# Verificar sitio existe
docker-compose exec backend bench list-sites

# Crear sitio si falta
docker-compose exec backend bench new-site nexo.local

# Establecer como default
docker-compose exec backend bench use nexo.local

# Migrar
docker-compose exec backend bench migrate
```

---

## Producción

### Requisitos Adicionales
- SSL/TLS (certificados Let's Encrypt)
- Backups automáticos
- Monitoring (Prometheus/Grafana)
- Load balancer (opcional)
- CDN para assets (opcional)

### Instalación de Producción

```bash
# 1. Clonar repositorio en directorio de producción
git clone https://github.com/aeromatico/nexo.git /opt/nexo
cd /opt/nexo

# 2. Configurar archivo .env para producción
cp .env.example .env
nano .env

# 3. Generar certificado SSL
docker-compose exec backend certbot certonly \
  --standalone \
  -d yourdomain.com \
  -d *.yourdomain.com \
  -m admin@yourdomain.com \
  --agree-tos

# 4. Levantar servicios
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 5. Backup automático
docker-compose exec backend bash scripts/backup.sh
```

### Checklist de Producción

- [ ] SSL/TLS configurado
- [ ] Backups automáticos programados
- [ ] Monitoring configurado
- [ ] Logs centralizados
- [ ] Firewall configurado
- [ ] Usuarios fuertes y roles asignados
- [ ] Rate limiting habilitado
- [ ] CORS configurado
- [ ] Email SMTP funcionando
- [ ] Health checks pasando
- [ ] Tests unitarios pasando
- [ ] Performance baseline establecido

---

## Actualización

Para actualizar a una nueva versión:

```bash
# 1. Backup
docker-compose exec backend bash scripts/backup.sh

# 2. Descargar código actualizado
git pull origin main

# 3. Reconstruir imágenes
docker-compose build

# 4. Migrar
docker-compose exec backend bench migrate

# 5. Reiniciar
docker-compose up -d

# 6. Verificar
docker-compose exec backend curl http://localhost:8000/health
```

---

## Soporte y Recursos

- **Documentación**: https://docs.nexo.bo
- **GitHub**: https://github.com/aeromatico/nexo
- **Issues**: https://github.com/aeromatico/nexo/issues
- **Email**: support@nexo.bo
- **Community**: https://community.nexo.bo

---

**Última actualización**: 12 de Diciembre, 2024
**Versión**: 1.0.0
