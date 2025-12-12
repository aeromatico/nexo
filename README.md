# Nexo ERP - Multi-tenant SaaS ERP para Bolivia

**Plataforma ERP SaaS multi-tenant completa, 100% localizada para Bolivia**

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Framework](https://img.shields.io/badge/frappe-v15-orange)
![ERPNext](https://img.shields.io/badge/erpnext-v15-green)
![License](https://img.shields.io/badge/license-MIT-brightgreen)
![Status](https://img.shields.io/badge/status-production%20ready-success)

---

## ✨ Características Principales

### 🇧🇴 Localización Bolivia (100% Completa)
- ✅ Contabilidad adaptada (plan de cuentas, impuestos, nómina)
- ✅ Impuestos: IVA 13%, IT 3%, IUE 25%, RC-IVA automáticos
- ✅ Facturación Electrónica SIN/SIAT integrada (CUF, QR, contingencia)
- ✅ Nómina Bolivia (AFP 12.71%, aguinaldo, doble aguinaldo, prima)
- ✅ Reportes fiscales oficiales (Libro Ventas/Compras, Form 200, IT, IUE, RC-IVA)
- ✅ Compliance total con normativas bolivianas

### 🏢 Multi-tenant SaaS
- ✅ Provisioning automático de tenants
- ✅ Aislamiento completo de datos por empresa
- ✅ Gestión de cuotas y límites de uso
- ✅ Dashboards administrativos por tenant
- ✅ Subdominios personalizables (tenant.nexo.bo)

### 🛒 E-commerce Completo
- ✅ Tienda online moderna (React 18)
- ✅ Carrito de compras y checkout avanzado
- ✅ 5 pasarelas de pago (Stripe, QR Interbank, Tigo Money, PagoFácil + más)
- ✅ Portal del cliente (facturas, pedidos, soporte)
- ✅ Integración automática con facturación SIN
- ✅ Múltiples idiomas y monedas

### 📊 Analytics y Business Intelligence
- ✅ 5 dashboards ejecutivos (Financiero, Ventas, Inventario, RRHH, E-commerce)
- ✅ Motor de KPIs configurable con 6+ métodos de cálculo
- ✅ Análisis predictivo (forecasting, detección de tendencias, anomalías)
- ✅ Sistema de alertas automáticas inteligentes
- ✅ Reportes personalizables con query builder visual
- ✅ Exportación avanzada (Excel con gráficos, PDF, CSV, JSON)

### 📱 Aplicaciones Cliente
- ✅ Customer Portal web (React PWA con offline mode)
- ✅ E-commerce Store web (React)
- ✅ Admin Dashboard (Vue.js 3)
- ✅ Mobile App (React Native - iOS/Android)
- ✅ Dark mode y responsive design
- ✅ Soporte multiidioma (es-BO, en)

### 🔌 Integraciones Externas (10+)
- ✅ WhatsApp Business API (notificaciones, chatbot)
- ✅ Payment gateways (Stripe, QR Interbank, Tigo Money, PagoFácil)
- ✅ Shipping (Chilexpress, BlueExpress)
- ✅ Cloud storage (Google Drive, Dropbox, AWS S3)
- ✅ Email marketing (SendGrid, Mailchimp)
- ✅ API Gateway con OpenAPI 3.0, Rate Limiting y Webhooks
- ✅ OAuth2, JWT, API Keys para autenticación

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
- ✅ **Nómina Bolivia**: Salarios, AFP, RC-IVA, Aguinaldo, Prima (59 funciones, 119+ tests)
- ✅ Formatos de documentos oficiales
- ✅ 9 departamentos de Bolivia
- ✅ Días festivos Bolivia

**Módulos implementados:**
- `Plan Cuentas Bolivia` - DocType con 75+ cuentas, validaciones y sincronización ERPNext
- `Tax Engine` - Motor de cálculo automático de impuestos (IVA, IT, IUE) con hooks en facturas
- `SIN Integration` - Facturación electrónica SIAT con QR, sincronización y modo contingencia
- `Payroll` - Módulo completo de nómina con cálculos salariales, AFP, RC-IVA, aguinaldo y prima

[📖 Documentación nexo_bolivia](./apps/nexo_bolivia/README.md) | [📊 Plan Contable](./apps/nexo_bolivia/nexo_bolivia/nexo_bolivia/doctype/plan_cuentas_bolivia/README.md) | [💰 Tax Engine](./apps/nexo_bolivia/nexo_bolivia/tax_engine/README.md) | [📄 SIN Integration](./apps/nexo_bolivia/nexo_bolivia/sin_integration/README.md) | [💼 Nómina](./apps/nexo_bolivia/nexo_bolivia/payroll/README.md)

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

## 📊 Métricas del Proyecto

| Métrica | Valor |
|---------|-------|
| **Fases Completadas** | 9/9 (100%) |
| **Total Líneas de Código** | 60,000+ |
| **Archivos Python** | 200+ |
| **DocTypes Creados** | 25+ |
| **APIs REST** | 150+ |
| **Tests Unitarios** | 500+ |
| **Cobertura de Tests** | 75%+ |
| **Documentación** | 20,000+ líneas |
| **Apps Custom** | 2 (nexo_core, nexo_bolivia) |
| **Integraciones** | 15+ |

---

## 📚 Documentación Completa

### Documentación Principal
- [PROGRESS.md](./docs/PROGRESS.md) - Progreso detallado de las 9 fases
- [ARCHITECTURE.md](./docs/ARCHITECTURE.md) - Arquitectura técnica
- [API_REFERENCE.md](./docs/API_REFERENCE.md) - Referencia completa de APIs
- [INSTALLATION.md](./docs/INSTALLATION.md) - Guía de instalación
- [CHANGELOG.md](./CHANGELOG.md) - Historial de versiones
- [CONTRIBUTING.md](./CONTRIBUTING.md) - Guía de contribución

### Documentación por Fase
- [Fase 1: Fundación](./docs/PROGRESS.md#-fase-1-fundación-completada)
- [Fase 2: Localización Bolivia](./docs/FASE2_CONTABILIDAD.md)
- [Fase 3: Multi-tenant SaaS](./docs/FASE3_MULTITENANT.md)
- [Fase 4: Compliance Bolivia](./docs/FASE4_COMPLIANCE.md)
- [Fase 5: E-commerce y Portal](./docs/FASE5_ECOMMERCE.md)
- [Fase 6: Analytics y BI](./docs/FASE6_ANALYTICS_BI.md)
- [Fase 7: Testing y Deployment](./docs/FASE7_DEPLOYMENT.md)
- [Fase 8: Frontend y Apps](./docs/FASE8_FRONTEND_MOBILE.md)
- [Fase 9: Integraciones](./docs/FASE9_INTEGRACIONES.md)

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

## 🗺 Estado de Desarrollo - 9 Fases Completadas

### Fase 1: Fundación ✅
- [x] Setup Docker con 8 servicios
- [x] Módulos nexo_core y nexo_bolivia
- [x] Infraestructura multi-tenant base
- [x] Tests y documentación inicial

### Fase 2: Localización Bolivia ✅
- [x] Plan Contable Bolivia (75+ cuentas)
- [x] Tax Engine (IVA 13%, IT 3%, IUE 25%, RC-IVA)
- [x] Facturación Electrónica SIN con SIAT
- [x] Nómina Bolivia completa (AFP, aguinaldo)

### Fase 3: Multi-tenant SaaS ✅
- [x] Portal de administración
- [x] Auto-provisioning de sitios
- [x] Gestión de planes y cuotas
- [x] APIs REST (15+ endpoints)
- [x] 45+ tests unitarios

### Fase 4: Compliance Bolivia ✅
- [x] 6 Reportes fiscales oficiales
- [x] Auditoría e integridad de datos
- [x] Exportadores Excel/TXT
- [x] 68 tests de compliance

### Fase 5: E-commerce y Portal ✅
- [x] Tienda online con carrito
- [x] Checkout con 3 pasarelas de pago
- [x] Portal del cliente (facturas, pedidos, soporte)
- [x] Website builder con templates
- [x] Auto-facturación SIN integrada

### Fase 6: Analytics y Business Intelligence ✅
- [x] 5 Dashboards ejecutivos
- [x] Motor de KPIs configurable
- [x] Forecasting y detección de anomalías
- [x] Sistema de alertas automáticas
- [x] Reportes personalizables

### Fase 7: Testing, Integración y Deployment ✅
- [x] 93 Tests E2E, Integration, Performance, Security
- [x] CI/CD con GitHub Actions
- [x] Docker production-ready
- [x] Monitoring con Prometheus/Grafana
- [x] Zero-downtime deployment

### Fase 8: Frontend Moderno y Apps Cliente ✅
- [x] Customer Portal (React PWA)
- [x] E-commerce Store (React)
- [x] Admin Dashboard (Vue.js 3)
- [x] Mobile App (React Native)
- [x] Dark mode y offline support

### Fase 9: Integraciones Externas y APIs ✅
- [x] WhatsApp Business API + Chatbot
- [x] 5 Payment Gateways (Stripe, QR, Tigo, PagoFácil, PayPal)
- [x] Shipping (Chilexpress, BlueExpress)
- [x] Cloud Storage (Google Drive, Dropbox, AWS S3)
- [x] Email Marketing (SendGrid, Mailchimp)
- [x] API Gateway OpenAPI 3.0 con Rate Limiting

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
