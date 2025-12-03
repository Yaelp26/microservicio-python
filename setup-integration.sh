#!/bin/bash

echo "🚀 Iniciando integración completa de microservicios..."
echo ""

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Directorio del proyecto Python
PYTHON_DIR="/Users/andrescruzortiz/Documents/GitHub/microservicio-python/python-analytics-service"
PHP_DIR="/Users/andrescruzortiz/Documents/GitHub/microservicio-php/php-auth-booking"

echo -e "${BLUE}📦 Paso 1: Instalando dependencia php-amqplib en PHP...${NC}"
cd "$PHP_DIR"
if [ -f "composer.json" ]; then
    docker compose exec php-auth-booking composer require php-amqplib/php-amqplib
    echo -e "${GREEN}✅ Dependencia instalada${NC}"
else
    echo -e "${YELLOW}⚠️  composer.json no encontrado en PHP${NC}"
fi

echo ""
echo -e "${BLUE}📋 Paso 2: Verificando configuración...${NC}"

# Verificar si .env del PHP tiene las variables de RabbitMQ
if grep -q "RABBITMQ_HOST" "$PHP_DIR/.env"; then
    echo -e "${GREEN}✅ Variables RabbitMQ ya configuradas en PHP${NC}"
else
    echo -e "${YELLOW}⚠️  Agregando variables RabbitMQ al .env de PHP...${NC}"
    echo "" >> "$PHP_DIR/.env"
    echo "# RabbitMQ Configuration" >> "$PHP_DIR/.env"
    echo "RABBITMQ_HOST=rabbitmq" >> "$PHP_DIR/.env"
    echo "RABBITMQ_PORT=5672" >> "$PHP_DIR/.env"
    echo "RABBITMQ_USER=guest" >> "$PHP_DIR/.env"
    echo "RABBITMQ_PASSWORD=guest" >> "$PHP_DIR/.env"
    echo "RABBITMQ_QUEUE=analytics_queue" >> "$PHP_DIR/.env"
    echo -e "${GREEN}✅ Variables agregadas${NC}"
fi

echo ""
echo -e "${BLUE}🐳 Paso 3: Deteniendo contenedores anteriores...${NC}"
cd "$PYTHON_DIR"
docker compose down

echo ""
echo -e "${BLUE}🚀 Paso 4: Iniciando todos los servicios...${NC}"
docker compose up -d

echo ""
echo -e "${BLUE}⏳ Esperando que los servicios estén listos...${NC}"
sleep 10

echo ""
echo -e "${GREEN}✅ Integración completada!${NC}"
echo ""
echo -e "${BLUE}📊 Servicios disponibles:${NC}"
echo -e "  • PHP Laravel:        ${GREEN}http://localhost:8082${NC}"
echo -e "  • Python Analytics:   ${GREEN}http://localhost:8000${NC}"
echo -e "  • Python Docs:        ${GREEN}http://localhost:8000/docs${NC}"
echo -e "  • RabbitMQ UI:        ${GREEN}http://localhost:15672${NC} (guest/guest)"
echo -e "  • Adminer (DB):       ${GREEN}http://localhost:8081${NC}"
echo -e "  • PostgreSQL:         ${GREEN}localhost:5432${NC}"
echo ""
echo -e "${YELLOW}📝 Siguiente paso:${NC}"
echo -e "  Actualiza el ${BLUE}BookingController.php${NC} siguiendo las instrucciones en:"
echo -e "  ${GREEN}INTEGRACION_PHP_RABBITMQ.md${NC}"
echo ""
echo -e "${BLUE}🔍 Ver logs:${NC}"
echo -e "  docker compose logs -f python-analytics"
echo -e "  docker compose logs -f php-auth-booking"
echo -e "  docker compose logs -f rabbitmq"
