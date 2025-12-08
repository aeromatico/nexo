#!/bin/bash
# Nexo ERP - Development Environment Setup
# Author: Aero

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔧 Configurando entorno de desarrollo...${NC}"

# 1. Habilitar modo desarrollador
echo -e "${BLUE}[1/4] Habilitando modo desarrollador...${NC}"
docker-compose exec -T backend bench --site nexo.local set-config developer_mode 1
echo -e "${GREEN}✓ Modo desarrollador habilitado${NC}"

# 2. Deshabilitar autenticación de email (desarrollo)
echo -e "${BLUE}[2/4] Configurando autenticación...${NC}"
docker-compose exec -T backend bench --site nexo.local console << EOF
frappe.db.set_value("System Settings", None, "disable_email_auth", 1)
frappe.db.commit()
EOF
echo -e "${GREEN}✓ Autenticación configurada${NC}"

# 3. Instalar apps en modo desarrollo
echo -e "${BLUE}[3/4] Configurando apps en modo desarrollo...${NC}"
docker-compose exec -T backend bench --site nexo.local console << EOF
# Recargar apps
import frappe
frappe.reload_doc("all")
frappe.db.commit()
EOF
echo -e "${GREEN}✓ Apps configuradas${NC}"

# 4. Clear cache
echo -e "${BLUE}[4/4] Limpiando cache...${NC}"
docker-compose exec -T backend bench --site nexo.local clear-cache
docker-compose exec -T backend bench --site nexo.local clear-website-cache
echo -e "${GREEN}✓ Cache limpiado${NC}"

echo ""
echo -e "${GREEN}✅ ¡Entorno de desarrollo configurado!${NC}"
echo ""
echo -e "${BLUE}Comandos útiles para desarrollo:${NC}"
echo "  docker-compose exec backend bench console           # Python console"
echo "  docker-compose exec backend bench mariadb            # MySQL console"
echo "  docker-compose exec backend bench clear-cache        # Limpiar cache"
echo "  docker-compose exec backend bench migrate            # Ejecutar migraciones"
echo "  docker-compose exec backend bench run-tests          # Ejecutar tests"
echo ""
