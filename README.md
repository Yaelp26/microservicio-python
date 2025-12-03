# Microservicio Python - Analytics Service

Servicio de análisis y estadísticas de ocupación con FastAPI y RabbitMQ integrado con microservicio PHP Laravel.

## Arquitectura

```
┌─────────────────┐      Events        ┌──────────────────┐
│  PHP Laravel    │ ─────────────────> │    RabbitMQ      │
│  (Reservas)     │   (publish)        │  (Message Bus)   │
└─────────────────┘                    └──────────────────┘
        │                                       │
        │                                       │ (consume)
        ▼                                       ▼
┌─────────────────────────────────────────────────────────┐
│              PostgreSQL (booking_db)                    │
│              Compartida entre ambos servicios           │
└─────────────────────────────────────────────────────────┘
        │
        │ Query
        ▼
┌─────────────────┐
│ Python FastAPI  │  GET /analytics/occupancy
│  (Analytics)    │  ← Admin (con JWT)
└─────────────────┘
```

## Inicio Rápido

### Opción 1: Script Automático (Recomendado)

```bash
cd /Users/andrescruzortiz/Documents/GitHub/microservicio-python
./setup-integration.sh
```

### Opción 2: Manual

```bash
cd python-analytics-service
docker compose up -d
```

## Configurar PHP para Publicar Eventos

**Sigue las instrucciones en:** `INTEGRACION_PHP_RABBITMQ.md`

Resumen rápido:
1. Instalar dependencia: `composer require php-amqplib/php-amqplib`
2. El archivo `RabbitMQService.php` ya está creado
3. Actualizar `BookingController.php` para publicar eventos
4. El Python consumirá automáticamente

## Estructura

```
python-analytics-service/
├── app/
│   ├── main.py                  # API FastAPI con JWT
│   ├── config.py                # Configuración (JWT, DB, RabbitMQ)
│   ├── database.py              # Conexión PostgreSQL
│   ├── models.py                # Modelos SQLAlchemy
│   ├── schemas.py               # Validación Pydantic
│   ├── rabbitmq.py              # Cliente RabbitMQ
│   ├── auth.py                  # Autenticación JWT
│   └── services/
│       └── analytics_service.py # Lógica de negocio
├── consumer.py                  # Consumidor RabbitMQ
├── docker-compose.yml           # Orquestación completa
└── INTEGRACION_PHP_RABBITMQ.md  # Guía de configuración PHP
```

## Endpoints

### Protegidos (requieren JWT de admin)
- `GET /analytics/occupancy` - Estadísticas generales
- `GET /analytics/occupancy/hotel/{id}` - Estadísticas por hotel

### Públicos
- `GET /` - Info del servicio
- `GET /health` - Health check

## Servicios

- **PHP Laravel**: http://localhost:8082
- **Python Analytics**: http://localhost:8000
- **Docs API**: http://localhost:8000/docs
- **RabbitMQ UI**: http://localhost:15672 (guest/guest)
- **Adminer**: http://localhost:8081
- **PostgreSQL**: localhost:5432

## Eventos RabbitMQ

El PHP publica estos eventos que el Python consume:

- `reservation_created` - Nueva reserva
- `reservation_updated` - Reserva actualizada
- `reservation_cancelled` - Reserva cancelada

## Autenticación

Usa JWT compatible con Laravel:
```bash
Authorization: Bearer {token_jwt_de_laravel}
```

Configuración en `.env`:
- `JWT_SECRET`: Mismo que Laravel
- `JWT_ISS`: travelink-laravel
- `JWT_AUD`: travelink-api

## Comandos Útiles

```bash
# Ver logs
docker compose logs -f python-analytics
docker compose logs -f php-auth-booking
docker compose logs -f rabbitmq

# Reiniciar servicios
docker compose restart

# Detener todo
docker compose down

# Ejecutar consumer manualmente
docker compose exec python-analytics python consumer.py
```
