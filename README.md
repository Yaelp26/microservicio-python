# Microservicio Python - Analytics Service

Servicio de análisis y estadísticas de ocupación con FastAPI, RabbitMQ y JWT.

## Iniciar

```bash
cd python-analytics-service
docker compose up -d
```

## Endpoints

**Protegidos (requieren JWT de admin):**
- `GET /analytics/occupancy` - Estadísticas generales
- `GET /analytics/occupancy/hotel/{id}` - Estadísticas por hotel

**Públicos:**
- `GET /` - Info del servicio
- `GET /health` - Health check

## Servicios

- Python Analytics: http://localhost:8000
- PHP Laravel: http://localhost:8082
- RabbitMQ UI: http://localhost:15672
- Adminer: http://localhost:8081
- PostgreSQL: localhost:5432
