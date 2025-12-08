# Nexo ERP

**Plataforma SaaS Multi-tenant de ERP Empresarial para Bolivia**

![Version](https://img.shields.io/badge/version-0.1.0-blue)
![License](https://img.shields.io/badge/license-GPL%20v3-green)
![Bolivia](https://img.shields.io/badge/localización-Bolivia-red)

---

## 🚀 Descripción

**Nexo** es una plataforma ERP SaaS multi-tenant desarrollada sobre Frappe Framework y ERPNext, completamente adaptada para Bolivia. Permite a empresas gestionar sus operaciones empresariales con:

- ✅ **Multi-tenancy**: Múltiples empresas en una sola instalación
- ✅ **Facturación Electrónica SIN**: Integración completa con Sistema de Impuestos Nacionales
- ✅ **ERP Completo**: Contabilidad, Ventas, Inventario, RRHH, CRM
- ✅ **Website Builder**: Sitios web integrados por tenant
- ✅ **E-commerce**: Tiendas online con catálogo integrado
- ✅ **Compliance Bolivia**: Impuestos, nómina y reportes según normativa boliviana

---

## 📋 Tabla de Contenidos

- [Stack Tecnológico](#-stack-tecnológico)
- [Arquitectura](#-arquitectura)
- [Módulos](#-módulos)
- [Inicio Rápido](#-inicio-rápido)
- [Documentación](#-documentación)
- [Desarrollo](#-desarrollo)
- [Roadmap](#-roadmap)
- [Licencia](#-licencia)

---

## 🛠 Stack Tecnológico

### Backend
- **Frappe Framework** v15+ (Python 3.10+)
- **ERPNext** v15+ (ERP base)
- **MariaDB** 10.6+ (Base de datos)
- **Redis** 7+ (Cache, Queue, SocketIO)

### Frontend
- **Frappe UI** (Vue 3)
- **Tailwind CSS** (Estilos)
- **JavaScript/ES6+**

### Infraestructura
- **Docker** & Docker Compose
- **Nginx** (Reverse proxy + SSL)
- **Let's Encrypt** (Certificados SSL automáticos)

### DevOps
- **GitHub Actions** (CI/CD)
- **Restic** (Backups)
- **MinIO/S3** (Almacenamiento)

---

## 🏗 Arquitectura

### Arquitectura Multi-tenant

```
┌─────────────────────────────────────────┐
│   Nginx Reverse Proxy + SSL            │
│   *.nexo.bo                             │
└─────────────┬───────────────────────────┘
              │
    ┌─────────┴──────────┬─────────────┐
    │                    │             │
┌───▼────┐         ┌────▼───┐    ┌────▼───┐
│tenant1 │         │tenant2 │    │tenant3 │
│.nexo.bo│         │.nexo.bo│    │.nexo.bo│
└───┬────┘         └────┬───┘    └────┬───┘
    │                   │             │
┌───▼────────────────────▼─────────────▼───┐
│   Frappe Bench (Multi-site)              │
│   ├── site1.nexo.bo                      │
│   ├── site2.nexo.bo                      │
│   └── site3.nexo.bo                      │
└──────────────────┬───────────────────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
┌───▼───┐      ┌──▼──┐       ┌──▼──┐
│MariaDB│      │Redis│       │MinIO│
│ DB per│      │Cache│       │Files│
│tenant │      │     │       │     │
└───────┘      └─────┘       └─────┘
```

### Stack de Servicios

```
nexo/
├── frontend (Nginx)         # Puerto 8765
├── backend (Frappe)         # Puerto 8000
├── socketio                 # Puerto 9000
├── mariadb                  # Puerto 3306
├── redis-cache              # Puerto 6379
├── redis-queue              # Puerto 6379
├── redis-socketio           # Puerto 6379
├── queue-worker             # Background jobs
└── scheduler                # Cron jobs
```

---

## 📦 Módulos

### 1. nexo_core
**Módulo Core de Multi-tenancy**

- Gestión de tenants
- Provisioning automático de sitios
- Control de cuotas y recursos
- Dashboard administrativo
- Métricas y analytics

[📖 Documentación nexo_core](./apps/nexo_core/README.md)

### 2. nexo_bolivia
**Localización para Bolivia**

- ✅ **Plan Contable Boliviano** (75+ cuentas implementadas)
- ✅ **Tax Engine**: IVA 13%, IT 3%, IUE 25% (cálculos automáticos, hooks y validaciones)
- ✅ **Facturación Electrónica SIN**: Integración completa con SIAT (CUF, QR, sincronización, contingencia)
- 🚧 Nómina según código laboral (pendiente)
- ✅ Formatos de documentos oficiales
- ✅ 9 departamentos de Bolivia
- ✅ Días festivos Bolivia

**Módulos implementados:**
- `Plan Cuentas Bolivia` - DocType con 75+ cuentas, validaciones y sincronización ERPNext
- `Tax Engine` - Motor de cálculo automático de impuestos (IVA, IT, IUE) con hooks en facturas
- `SIN Integration` - Facturación electrónica SIAT con QR, sincronización y modo contingencia

[📖 Documentación nexo_bolivia](./apps/nexo_bolivia/README.md) | [📊 Plan Contable](./apps/nexo_bolivia/nexo_bolivia/nexo_bolivia/doctype/plan_cuentas_bolivia/README.md) | [💰 Tax Engine](./apps/nexo_bolivia/nexo_bolivia/tax_engine/README.md) | [📄 SIN Integration](./apps/nexo_bolivia/nexo_bolivia/sin_integration/README.md)

---

## 🚀 Inicio Rápido

### Prerrequisitos

- Docker & Docker Compose
- Git
- 4GB RAM mínimo
- 20GB espacio en disco

### Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/aero/nexo.git
cd nexo

# 2. Copiar variables de entorno
cp .env.example .env

# 3. Editar .env con tus configuraciones
nano .env

# 4. Levantar los servicios
docker-compose up -d

# 5. Esperar a que los servicios inicien (2-3 minutos)
docker-compose logs -f backend

# 6. Crear el primer sitio
docker-compose exec backend bench new-site nexo.local \
  --admin-password admin \
  --install-app erpnext \
  --install-app nexo_core \
  --install-app nexo_bolivia

# 7. Configurar el sitio como default
docker-compose exec backend bench use nexo.local

# 8. Acceder a la aplicación
# http://localhost:8765
# Usuario: Administrator
# Contraseña: admin
```

### Desarrollo Local

```bash
# Ver logs
docker-compose logs -f

# Acceder al contenedor backend
docker-compose exec backend bash

# Ejecutar comandos bench
docker-compose exec backend bench migrate
docker-compose exec backend bench clear-cache
docker-compose exec backend bench console

# Reiniciar servicios
docker-compose restart backend
```

---

## 📚 Documentación

### Documentación Completa

- [Arquitectura Técnica](./docs/ARCHITECTURE.md)
- [Guía de Desarrollo](./docs/DEVELOPMENT.md)
- [Deployment en Producción](./docs/DEPLOYMENT.md)
- [API Reference](./docs/API.md)
- [Integración SIN Bolivia](./docs/SIN_INTEGRATION.md)

### Scripts Disponibles

```bash
# Inicialización
./scripts/init.sh              # Inicializar proyecto
./scripts/create-tenant.sh     # Crear nuevo tenant
./scripts/backup.sh            # Backup manual

# Desarrollo
./scripts/dev-setup.sh         # Setup entorno desarrollo
./scripts/run-tests.sh         # Ejecutar tests
```

---

## 💻 Desarrollo

### Estructura del Proyecto

```
nexo/
├── apps/
│   ├── nexo_core/          # Multi-tenancy core
│   └── nexo_bolivia/       # Localización Bolivia
├── docker/                 # Configuraciones Docker
├── scripts/               # Scripts de utilidad
├── docs/                  # Documentación
├── .github/
│   └── workflows/         # CI/CD pipelines
├── docker-compose.yml     # Orquestación Docker
├── .env.example          # Variables de entorno
└── README.md             # Este archivo
```

### Crear una Nueva App

```bash
docker-compose exec backend bench new-app nexo_custom
docker-compose exec backend bench get-app /home/frappe/frappe-bench/apps/nexo_custom
docker-compose exec backend bench --site nexo.local install-app nexo_custom
```

### Testing

```bash
# Unit tests
docker-compose exec backend bench run-tests --app nexo_core

# Specific test
docker-compose exec backend bench run-tests nexo_core.tests.test_tenant
```

---

## 🗺 Roadmap

### Fase 1: Fundación ✅ (En Progreso)
- [x] Setup inicial Docker
- [x] Módulo nexo_core base
- [x] Módulo nexo_bolivia base
- [x] Documentación inicial
- [ ] Tests unitarios básicos

### Fase 2: Módulos Core (Semanas 3-4)
- [ ] Contabilidad + Plan contable Bolivia
- [ ] Facturación con IVA 13%
- [ ] Inventario básico
- [ ] RRHH + Nómina Bolivia

### Fase 3: SaaS Features (Semanas 5-6)
- [ ] Portal administración tenants
- [ ] Auto-provisioning de sitios
- [ ] Website builder por tenant
- [ ] Backups automatizados

### Fase 4: Compliance Bolivia (Semanas 7-8)
- [ ] Facturación electrónica SIN
- [ ] Reportes fiscales automáticos
- [ ] Integración bancaria Bolivia
- [ ] Testing compliance completo

### Fase 5: E-commerce & Avanzado
- [ ] Tienda online por tenant
- [ ] Pasarelas de pago Bolivia
- [ ] App móvil (React Native)
- [ ] Dashboard analytics avanzado

---

## 🇧🇴 Características Bolivia

### Impuestos Configurados
- **IVA**: 13% (Impuesto al Valor Agregado)
- **IT**: 3% (Impuesto a las Transacciones)
- **IUE**: 25% (Impuesto sobre Utilidades)

### Facturación Electrónica
- Integración con SIAT (Sistema Impuestos Nacionales)
- Generación automática de QR en facturas
- Sincronización en tiempo real
- Anulación de facturas online

### Nómina Boliviana
- Cálculo de aguinaldo y prima
- Aportes AFP (12.71%)
- RC-IVA automático
- Finiquitos según código laboral

### Regional
- 9 Departamentos de Bolivia
- Calendario con días festivos
- Formato boliviano de números y fechas
- Timezone America/La_Paz

---

## 👥 Contribuir

¡Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea tu feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add: AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto está bajo la licencia **GNU General Public License v3.0**

Ver [LICENSE](LICENSE) para más detalles.

---

## 🙋 Soporte

**Autor**: Aero
**Email**: admin@aero.bo
**Website**: https://nexo.bo

### Reportar Issues
Si encuentras un bug o tienes una sugerencia:
- [Abrir un Issue](https://github.com/aero/nexo/issues)

### Comunidad
- [Documentación](https://docs.nexo.bo)
- [Foro de la Comunidad](https://community.nexo.bo)

---

## 🙏 Agradecimientos

Este proyecto está construido sobre:
- [Frappe Framework](https://frappeframework.com)
- [ERPNext](https://erpnext.com)
- La comunidad open-source

---

**Hecho con ❤️ en Bolivia 🇧🇴**
