# Configuración de RabbitMQ en PHP Laravel

## 1. Instalar dependencia php-amqplib

En el directorio del microservicio PHP, ejecutar:

```bash
cd /Users/andrescruzortiz/Documents/GitHub/microservicio-php/php-auth-booking
docker compose exec php-auth-booking composer require php-amqplib/php-amqplib
```

## 2. Actualizar .env

Agregar estas líneas al archivo `.env`:

```env
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
RABBITMQ_QUEUE=analytics_queue
```

## 3. El archivo RabbitMQService.php ya está creado

Se encuentra en: `app/Services/RabbitMQService.php`

## 4. Actualizar BookingController.php

Agregar al inicio del archivo:

```php
use App\Services\RabbitMQService;
```

En el constructor, inyectar el servicio:

```php
protected $rabbitmq;

public function __construct(RabbitMQService $rabbitmq)
{
    $this->rabbitmq = $rabbitmq;
}
```

### Método store (crear reserva):

Después de guardar la reserva, agregar:

```php
// Publicar evento de reserva creada
$this->rabbitmq->publish('reservation_created', [
    'reservation_id' => $reservation->id,
    'user_id' => $reservation->user_id,
    'hotel_id' => $reservation->hotel_id,
    'room_type' => $reservation->room_type,
    'status' => $reservation->status,
    'check_in' => $reservation->check_in,
    'check_out' => $reservation->check_out
]);
```

### Método update (actualizar reserva):

Después de actualizar, agregar:

```php
// Publicar evento de reserva actualizada
$this->rabbitmq->publish('reservation_updated', [
    'reservation_id' => $reservation->id,
    'status' => $reservation->status,
    'changes' => $request->only(['status', 'check_in', 'check_out'])
]);
```

### Método destroy (cancelar reserva):

Después de cambiar el estado, agregar:

```php
// Publicar evento de reserva cancelada
$this->rabbitmq->publish('reservation_cancelled', [
    'reservation_id' => $reservation->id,
    'user_id' => $reservation->user_id,
    'hotel_id' => $reservation->hotel_id
]);
```

## 5. Registrar el servicio en AppServiceProvider (opcional)

En `app/Providers/AppServiceProvider.php`:

```php
public function register()
{
    $this->app->singleton(RabbitMQService::class, function ($app) {
        return new RabbitMQService();
    });
}
```

## 6. Ejemplo completo de uso en cualquier controlador:

```php
use App\Services\RabbitMQService;

class BookingController extends Controller
{
    protected $rabbitmq;

    public function __construct(RabbitMQService $rabbitmq)
    {
        $this->rabbitmq = $rabbitmq;
    }

    public function store(Request $request)
    {
        // ... validación y lógica ...
        
        $reservation = Reservation::create($request->all());
        
        // Publicar evento
        $this->rabbitmq->publish('reservation_created', [
            'reservation_id' => $reservation->id,
            'user_id' => $reservation->user_id,
            'hotel_id' => $reservation->hotel_id,
            'room_type' => $reservation->room_type,
            'status' => $reservation->status
        ]);
        
        return response()->json($reservation, 201);
    }
}
```

## 7. Verificar funcionamiento

1. Iniciar servicios:
```bash
cd /Users/andrescruzortiz/Documents/GitHub/microservicio-python/python-analytics-service
docker compose up -d
```

2. Ver logs de RabbitMQ:
```bash
docker compose logs -f rabbitmq
```

3. Crear una reserva desde el PHP y verificar que el evento llegue al Python:
```bash
docker compose logs -f python-analytics
```

## Eventos disponibles:

- `reservation_created` - Cuando se crea una nueva reserva
- `reservation_updated` - Cuando se actualiza una reserva
- `reservation_cancelled` - Cuando se cancela una reserva

El servicio Python ya está configurado para consumir estos eventos.
