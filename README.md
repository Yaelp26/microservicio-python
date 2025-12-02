# Microservicio Python - Analytics Service

Servicio de análisis y estadísticas de ocupación con FastAPI y RabbitMQ.

## Estructura

```
python-analytics-service/   # Servicio principal
├── app/
│   ├── main.py            # API FastAPI
│   ├── config.py          # Configuración
│   ├── database.py        # Conexión PostgreSQL
│   ├── models.py          # Modelos SQLAlchemy
│   ├── schemas.py         # Validación Pydantic
│   ├── rabbitmq.py        # Cliente RabbitMQ
│   └── services/
│       └── analytics_service.py  # Lógica de negocio
├── consumer.py            # Consumidor RabbitMQ
├── docker-compose.yml     # Orquestación completa
├── Dockerfile
├── requirements.txt
└── .env.example
```

## Iniciar Servicio

```bash
cd python-analytics-service
docker-compose up -d
```

## Endpoints

- `GET /analytics/occupancy` - Estadísticas generales
- `GET /analytics/occupancy/hotel/{id}` - Estadísticas por hotel
- `GET /health` - Health check

## Acceso

- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- RabbitMQ UI: http://localhost:15672 (guest/guest)
- Adminer: http://localhost:8081
