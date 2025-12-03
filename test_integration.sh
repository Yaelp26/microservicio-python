#!/bin/bash

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🧪 Test de Integración PHP → Python${NC}"
echo ""

# 1. Health Check Python
echo -e "${BLUE}1. Health Check Python Analytics...${NC}"
HEALTH=$(curl -s http://localhost:8000/health)
if echo "$HEALTH" | grep -q "healthy"; then
    echo -e "${GREEN}✅ Python Analytics está saludable${NC}"
    echo "$HEALTH" | python3 -m json.tool
else
    echo -e "${RED}❌ Python Analytics no responde${NC}"
    exit 1
fi

echo ""

# 2. Verificar datos en BD
echo -e "${BLUE}2. Verificando datos en PostgreSQL...${NC}"
RESERVATIONS=$(docker compose exec -T postgres psql -U booking_user -d booking_db -t -c "SELECT COUNT(*) FROM reservations;" 2>/dev/null | tr -d ' ')
echo -e "   Reservas en BD: ${GREEN}$RESERVATIONS${NC}"

echo ""

# 3. Intentar acceder sin token (debe fallar)
echo -e "${BLUE}3. Test sin autenticación (debe fallar)...${NC}"
NO_AUTH=$(curl -s http://localhost:8000/analytics/occupancy)
if echo "$NO_AUTH" | grep -q "Not authenticated"; then
    echo -e "${GREEN}✅ Autenticación JWT funcionando correctamente${NC}"
    echo "   Respuesta: $NO_AUTH"
else
    echo -e "${RED}❌ El endpoint no está protegido${NC}"
fi

echo ""

# 4. Generar token JWT de prueba (simulando Laravel)
echo -e "${BLUE}4. Generando token JWT de prueba...${NC}"
echo -e "${YELLOW}   Nota: En producción, obtendrías este token del endpoint PHP /api/login${NC}"

# Usar Python para generar un token JWT válido
TOKEN=$(python3 << 'END_PYTHON'
import jwt
import datetime

payload = {
    'sub': '1',
    'email': 'admin@travelink.com',
    'role': 'admin',
    'iss': 'travelink-laravel',
    'aud': 'travelink-api',
    'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
}

secret = '7rTsLU4hJE0X80Wau2EYeBL6vp0pg1VWhy7mi7PvXuMozvUelbRFnpGA2yMq2t0A'
token = jwt.encode(payload, secret, algorithm='HS256')
print(token)
END_PYTHON
)

if [ -z "$TOKEN" ]; then
    echo -e "${RED}❌ Error al generar token${NC}"
    echo -e "${YELLOW}   Instalando PyJWT...${NC}"
    pip3 install PyJWT > /dev/null 2>&1
    TOKEN=$(python3 << 'END_PYTHON'
import jwt
import datetime

payload = {
    'sub': '1',
    'email': 'admin@travelink.com',
    'role': 'admin',
    'iss': 'travelink-laravel',
    'aud': 'travelink-api',
    'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
}

secret = '7rTsLU4hJE0X80Wau2EYeBL6vp0pg1VWhy7mi7PvXuMozvUelbRFnpGA2yMq2t0A'
token = jwt.encode(payload, secret, algorithm='HS256')
print(token)
END_PYTHON
)
fi

echo -e "${GREEN}✅ Token generado${NC}"
echo -e "   Token: ${TOKEN:0:50}..."

echo ""

# 5. Test con token válido
echo -e "${BLUE}5. Test con autenticación JWT válida...${NC}"
STATS=$(curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/analytics/occupancy)

if echo "$STATS" | grep -q "success"; then
    echo -e "${GREEN}✅ Estadísticas obtenidas exitosamente!${NC}"
    echo "$STATS" | python3 -m json.tool
else
    echo -e "${RED}❌ Error al obtener estadísticas${NC}"
    echo "$STATS"
fi

echo ""

# 6. Test endpoint por hotel
echo -e "${BLUE}6. Test estadísticas por hotel (ID: 1)...${NC}"
HOTEL_STATS=$(curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/analytics/occupancy/hotel/1)

if echo "$HOTEL_STATS" | grep -q "success"; then
    echo -e "${GREEN}✅ Estadísticas del hotel obtenidas!${NC}"
    echo "$HOTEL_STATS" | python3 -m json.tool
else
    echo -e "${RED}❌ Error al obtener estadísticas del hotel${NC}"
    echo "$HOTEL_STATS"
fi

echo ""
echo -e "${GREEN}✅ Tests completados!${NC}"
echo ""
echo -e "${YELLOW}📝 Para uso en producción:${NC}"
echo -e "   1. Obtén el token desde PHP: ${BLUE}POST http://localhost:8082/api/login${NC}"
echo -e "   2. Usa ese token en Python: ${BLUE}GET http://localhost:8000/analytics/occupancy${NC}"
echo -e "   3. Header: ${BLUE}Authorization: Bearer {token}${NC}"
