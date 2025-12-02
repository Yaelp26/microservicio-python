# Python Analytics Service

Servicio de análisis y estadísticas de ocupación para el sistema de reservas hoteleras. Implementado con **FastAPI** y **RabbitMQ**.

## Descripción

Este servicio genera reportes sobre ocupación y uso del sistema de reservas, cumpliendo con los siguientes requerimientos:

### Caso de Uso
Obtener estadísticas de ocupación

### Actores
- Admin
- Servicio Python (Analytics)

### Flujo Principal
1. El admin envía GET `/analytics/occupancy`
2. Python procesa la información de la base de datos
3. Genera estadísticas de ocupación
4. Devuelve los resultados al cliente

### Precondición
Datos de reservas existentes en la base de datos

### Post-condición
El sistema muestra estadísticas actualizadas

## Arquitectura

```
┌─────────────┐      HTTP GET      ┌──────────────────┐
│   Admin     │ ──────────────────> │  FastAPI Service │
│   Client    │                     │  (Python)        │
└─────────────┘                     └──────────────────┘
                                            │
                                            │ SQL Query
                                            ▼
                                    ┌──────────────────┐
                                    │   PostgreSQL     │
                                    │   (booking_db)   │
                                    └──────────────────┘
                                            │
                                            │ Events
                                            ▼
                                    ┌──────────────────┐
                                    │    RabbitMQ      │
                                    │   (Message Bus)  │
                                    └──────────────────┘
```

## Características

- API RESTful con FastAPI
- Conexión a base de datos PostgreSQL (compartida con Laravel)
- Integración con RabbitMQ para mensajería asíncrona
- Estadísticas detalladas de ocupación:
  - Total de reservaciones
  - Reservaciones activas/completadas/canceladas
  - Tasa de ocupación
  - Estadísticas por hotel
  - Estadísticas por tipo de habitación
  - Estadísticas por estado
- Health checks
- Documentación automática (Swagger UI)
- Logging detallado
- Dockerizado

## Requisitos

- Python 3.11+
- PostgreSQL
- RabbitMQ
- Docker y Docker Compose (opcional)

## Instalación

### Opción 1: Con Docker (Recomendado)

```bash
cd python-analytics-service
docker-compose up -d
```

### Opción 2: Local

1. Crear entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

4. Ejecutar servicio:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Endpoints

### Health Check
```http
GET /health
```

### Obtener Estadísticas de Ocupación
```http
GET /analytics/occupancy
```

**Respuesta exitosa:**
```json
{
  "success": true,
  "message": "Estadísticas de ocupación obtenidas exitosamente",
  "data": {
    "total_reservations": 150,
    "active_reservations": 45,
    "completed_reservations": 80,
    "cancelled_reservations": 25,
    "occupancy_rate": 30.0,
    "by_hotel": [
      {
        "hotel_id": 1,
        "total_reservations": 75,
        "active_reservations": 25,
        "occupancy_rate": 33.33
      }
    ],
    "by_room_type": [
      {
        "room_type": "deluxe",
        "total_reservations": 50,
        "active_reservations": 15
      }
    ],
    "by_status": [
      {
        "status": "confirmed",
        "count": 45,
        "percentage": 30.0
      }
    ]
  },
  "timestamp": "2025-12-02T10:30:00"
}
```

### Obtener Ocupación de un Hotel Específico
```http
GET /analytics/occupancy/hotel/{hotel_id}
```

## Configuración

### Variables de Entorno

```env
# Database
DB_HOST=postgres
DB_PORT=5432
DB_NAME=booking_db
DB_USER=booking_user
DB_PASSWORD=booking_password

# RabbitMQ
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
RABBITMQ_QUEUE=analytics_queue

# Service
SERVICE_PORT=8000
```

## RabbitMQ

El servicio publica eventos en RabbitMQ cuando se generan estadísticas:

**Ejemplo de mensaje:**
```json
{
  "event": "occupancy_stats_generated",
  "timestamp": "2025-12-02T10:30:00",
  "data": {
    "total_reservations": 150,
    "active_reservations": 45,
    "occupancy_rate": 30.0
  }
}
```

### Consumidor de Mensajes

Para ejecutar el consumidor de RabbitMQ:

```bash
python consumer.py
```

## Documentación Interactiva

Una vez iniciado el servicio, accede a:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Logging

Los logs incluyen:
- Conexiones a base de datos
- Consultas SQL ejecutadas
- Mensajes de RabbitMQ publicados/consumidos
- Errores y excepciones
- Estadísticas generadas

## Testing

### Opción 1: Dashboard HTML Interactivo (Más Fácil)

Abre el archivo `test_api.html` en tu navegador:

```bash
open test_api.html  # macOS
# o simplemente arrastra el archivo a tu navegador
```

Este dashboard te permite:
- Verificar el health check
- Ver estadísticas en tiempo real
- Consultar hoteles específicos
- Visualización interactiva de datos

### Opción 2: Tests con cURL

```bash
# Health check
curl http://localhost:8000/health

# Estadísticas generales
curl http://localhost:8000/analytics/occupancy

# Estadísticas de hotel específico
curl http://localhost:8000/analytics/occupancy/hotel/1
```

### Opción 3: Tests con Python

```bash
# Instalar dependencias de testing
pip install pytest pytest-asyncio httpx

# Ejecutar tests
pytest
```

### Opción 4: Postman/Insomnia

1. Importa la colección desde: `http://localhost:8000/docs`
2. O crea requests manualmente con las URLs de arriba

---

## Conectar con Frontend

Revisa la guía completa en [`API_CONFIG.md`](./API_CONFIG.md) que incluye:
- Documentación completa de endpoints
- Ejemplos en JavaScript/Fetch
- Ejemplos en React
- Ejemplos con Axios
- Auto-actualización
- Visualización de datos
- Configuración de seguridad

### Quick Start para Frontend

```javascript
// Obtener estadísticas
const response = await fetch('http://localhost:8000/analytics/occupancy');
const data = await response.json();

console.log('Ocupación:', data.data.occupancy_rate + '%');
console.log('Activas:', data.data.active_reservations);
```

---

## Testing

```bash
# Instalar dependencias de testing
pip install pytest pytest-asyncio httpx

# Ejecutar tests
pytest
```

## Monitoreo

### Health Check
```bash
curl http://localhost:8000/health
```

### Verificar Conexión a RabbitMQ
Accede a la interfaz web de RabbitMQ:
```
http://localhost:15672
Usuario: guest
Password: guest
```

## Docker Compose Completo

Para integrar con el servicio PHP Laravel, actualiza el `docker-compose.yml` principal:

```yaml
services:
  # ... servicios existentes ...

  # Servicio Python Analytics
  python-analytics:
    build: ./python-analytics-service
    container_name: python-analytics-service
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - rabbitmq
    networks:
      - microservices-network
    restart: unless-stopped

  # RabbitMQ
  rabbitmq:
    image: rabbitmq:3-management
    container_name: rabbitmq-service
    ports:
      - "5672:5672"
      - "15672:15672"
    environment:
      RABBITMQ_DEFAULT_USER: guest
      RABBITMQ_DEFAULT_PASS: guest
    networks:
      - microservices-network
    restart: unless-stopped
```

## Integración con Laravel

El servicio Laravel puede consumir este API:

```php
use Illuminate\Support\Facades\Http;

$response = Http::get('http://python-analytics:8000/analytics/occupancy');
$stats = $response->json();
```

## Notas

- El servicio comparte la base de datos con Laravel (booking_db)
- Los modelos SQLAlchemy reflejan las tablas de Laravel
- RabbitMQ permite comunicación asíncrona entre servicios
- El servicio es stateless y escalable horizontalmente

## Troubleshooting

### Error de conexión a PostgreSQL
```bash
# Verificar que PostgreSQL esté corriendo
docker ps | grep postgres

# Verificar logs
docker logs php-auth-booking-db
```

### Error de conexión a RabbitMQ
```bash
# Verificar que RabbitMQ esté corriendo
docker ps | grep rabbitmq

# Verificar logs
docker logs rabbitmq-service
```

## Licencia

MIT License

## Autor

Sistema de Microservicios - Reservas Hoteleras
