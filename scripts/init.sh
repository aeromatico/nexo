#!/bin/bash
# Nexo ERP - Initialization Script
# Author: Aero

set -e

echo "🚀 Inicializando Nexo ERP..."

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. Verificar Docker
echo -e "${BLUE}[1/7] Verificando Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker no está instalado${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker encontrado${NC}"

# 2. Verificar Docker Compose
echo -e "${BLUE}[2/7] Verificando Docker Compose...${NC}"
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose no está instalado${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker Compose encontrado${NC}"

# 3. Copiar .env si no existe
echo -e "${BLUE}[3/7] Configurando variables de entorno...${NC}"
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${GREEN}✓ Archivo .env creado${NC}"
    echo -e "${BLUE}⚠️  Por favor edita .env con tus configuraciones${NC}"
else
    echo -e "${GREEN}✓ Archivo .env ya existe${NC}"
fi

# 4. Levantar servicios
echo -e "${BLUE}[4/7] Levantando servicios Docker...${NC}"
docker-compose up -d
echo -e "${GREEN}✓ Servicios levantados${NC}"

# 5. Esperar a que MariaDB esté listo
echo -e "${BLUE}[5/7] Esperando a que MariaDB esté listo...${NC}"
sleep 10
until docker-compose exec -T mariadb mysqladmin ping -h localhost --silent; do
    echo "Esperando MariaDB..."
    sleep 2
done
echo -e "${GREEN}✓ MariaDB listo${NC}"

# 6. Crear primer sitio
echo -e "${BLUE}[6/7] Creando sitio inicial nexo.local...${NC}"
docker-compose exec -T backend bench new-site nexo.local \
    --admin-password admin \
    --mariadb-root-password nexo_admin_2024 \
    --install-app erpnext || echo "Sitio ya existe o error al crear"

# Instalar apps custom
echo -e "${BLUE}Instalando nexo_core...${NC}"
docker-compose exec -T backend bench get-app /home/frappe/frappe-bench/apps/nexo_core || true
docker-compose exec -T backend bench --site nexo.local install-app nexo_core || echo "App ya instalada"

echo -e "${BLUE}Instalando nexo_bolivia...${NC}"
docker-compose exec -T backend bench get-app /home/frappe/frappe-bench/apps/nexo_bolivia || true
docker-compose exec -T backend bench --site nexo.local install-app nexo_bolivia || echo "App ya instalada"

# 7. Set default site
echo -e "${BLUE}[7/7] Configurando sitio por defecto...${NC}"
docker-compose exec -T backend bench use nexo.local

echo ""
echo -e "${GREEN}✅ ¡Nexo ERP inicializado exitosamente!${NC}"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}📍 Accede a: http://localhost:8080${NC}"
echo -e "${GREEN}👤 Usuario: Administrator${NC}"
echo -e "${GREEN}🔑 Contraseña: admin${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}Comandos útiles:${NC}"
echo "  docker-compose logs -f          # Ver logs"
echo "  docker-compose exec backend bash # Acceder al contenedor"
echo "  docker-compose restart          # Reiniciar servicios"
echo ""
