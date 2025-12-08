#!/bin/bash
# Nexo ERP - Create Tenant Script
# Author: Aero

set -e

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Verificar argumentos
if [ $# -lt 2 ]; then
    echo -e "${RED}Uso: $0 <tenant-name> <admin-email> [admin-password]${NC}"
    echo ""
    echo "Ejemplo:"
    echo "  $0 cliente1 admin@cliente1.com mypassword"
    exit 1
fi

TENANT_NAME=$1
ADMIN_EMAIL=$2
ADMIN_PASSWORD=${3:-admin123}
SITE_NAME="${TENANT_NAME}.nexo.bo"

echo -e "${BLUE}🚀 Creando nuevo tenant: ${SITE_NAME}${NC}"

# 1. Crear sitio
echo -e "${BLUE}[1/5] Creando sitio Frappe...${NC}"
docker-compose exec backend bench new-site ${SITE_NAME} \
    --admin-password ${ADMIN_PASSWORD} \
    --mariadb-root-password nexo_admin_2024 \
    --install-app erpnext \
    --install-app nexo_core \
    --install-app nexo_bolivia

echo -e "${GREEN}✓ Sitio creado${NC}"

# 2. Configurar país Bolivia
echo -e "${BLUE}[2/5] Configurando datos para Bolivia...${NC}"
docker-compose exec backend bench --site ${SITE_NAME} console << EOF
frappe.db.set_default("country", "Bolivia")
frappe.db.set_default("currency", "BOB")
frappe.db.set_default("time_zone", "America/La_Paz")
frappe.db.commit()
EOF

echo -e "${GREEN}✓ Configuración Bolivia aplicada${NC}"

# 3. Crear empresa
echo -e "${BLUE}[3/5] Creando empresa...${NC}"
docker-compose exec backend bench --site ${SITE_NAME} console << EOF
from frappe import get_doc

company = get_doc({
    "doctype": "Company",
    "company_name": "${TENANT_NAME}",
    "abbr": "${TENANT_NAME:0:3}",
    "country": "Bolivia",
    "default_currency": "BOB"
})
company.insert()
frappe.db.commit()
print(f"Empresa creada: {company.name}")
EOF

echo -e "${GREEN}✓ Empresa creada${NC}"

# 4. Migrar
echo -e "${BLUE}[4/5] Ejecutando migraciones...${NC}"
docker-compose exec backend bench --site ${SITE_NAME} migrate

echo -e "${GREEN}✓ Migraciones completadas${NC}"

# 5. Clear cache
echo -e "${BLUE}[5/5] Limpiando cache...${NC}"
docker-compose exec backend bench --site ${SITE_NAME} clear-cache

echo -e "${GREEN}✓ Cache limpiado${NC}"

echo ""
echo -e "${GREEN}✅ ¡Tenant creado exitosamente!${NC}"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}📍 Sitio: ${SITE_NAME}${NC}"
echo -e "${GREEN}👤 Usuario: Administrator${NC}"
echo -e "${GREEN}📧 Email: ${ADMIN_EMAIL}${NC}"
echo -e "${GREEN}🔑 Contraseña: ${ADMIN_PASSWORD}${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}Acceso:${NC}"
echo "  En desarrollo: http://localhost:8080"
echo "  (Asegúrate de configurar el host header: ${SITE_NAME})"
echo ""
