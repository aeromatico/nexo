#!/bin/bash
# Nexo ERP - Backup Script
# Author: Aero

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo -e "${BLUE}💾 Iniciando backup de Nexo ERP...${NC}"

# Crear directorio de backups
mkdir -p ${BACKUP_DIR}

# Obtener lista de sitios
echo -e "${BLUE}[1/3] Obteniendo lista de sitios...${NC}"
SITES=$(docker-compose exec -T backend bench --site all list-sites 2>/dev/null | grep -v "Installed" || echo "nexo.local")

for SITE in $SITES; do
    if [ ! -z "$SITE" ]; then
        echo -e "${BLUE}[2/3] Haciendo backup de ${SITE}...${NC}"

        # Backup con bench
        docker-compose exec -T backend bench --site ${SITE} backup \
            --backup-path /home/frappe/frappe-bench/sites/${SITE}/private/backups

        # Copiar backup al host
        docker cp nexo-backend:/home/frappe/frappe-bench/sites/${SITE}/private/backups \
            ${BACKUP_DIR}/${SITE}_${TIMESTAMP}

        echo -e "${GREEN}✓ Backup de ${SITE} completado${NC}"
    fi
done

# Backup de la base de datos completa
echo -e "${BLUE}[3/3] Backup completo de MariaDB...${NC}"
docker-compose exec -T mariadb mysqldump -uroot -pnexo_admin_2024 --all-databases \
    > ${BACKUP_DIR}/full_db_${TIMESTAMP}.sql

echo -e "${GREEN}✓ Backup de MariaDB completado${NC}"

echo ""
echo -e "${GREEN}✅ ¡Backup completado exitosamente!${NC}"
echo -e "${BLUE}Ubicación: ${BACKUP_DIR}/${NC}"
echo ""
