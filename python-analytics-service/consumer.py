"""
Consumidor de RabbitMQ para procesar eventos de reservas
"""
import json
import logging
from app.rabbitmq import rabbitmq_client
from app.config import get_settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()


def callback(ch, method, properties, body):
    """
    Callback para procesar mensajes de RabbitMQ
    
    Args:
        ch: Canal
        method: Método
        properties: Propiedades
        body: Cuerpo del mensaje
    """
    try:
        message = json.loads(body)
        logger.info(f"Mensaje recibido: {message}")
        
        # Procesar diferentes tipos de eventos
        event_type = message.get('event')
        
        if event_type == 'reservation_created':
            logger.info(f"Nueva reserva creada: {message.get('data')}")
            # Aquí puedes agregar lógica para actualizar estadísticas en tiempo real
            
        elif event_type == 'reservation_updated':
            logger.info(f"Reserva actualizada: {message.get('data')}")
            
        elif event_type == 'reservation_cancelled':
            logger.info(f"Reserva cancelada: {message.get('data')}")
        
        # Confirmar mensaje procesado
        ch.basic_ack(delivery_tag=method.delivery_tag)
        logger.info("Mensaje procesado exitosamente")
        
    except Exception as e:
        logger.error(f"Error al procesar mensaje: {e}")
        # Rechazar mensaje y reencolar
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


if __name__ == '__main__':
    try:
        logger.info("Iniciando consumidor de RabbitMQ...")
        rabbitmq_client.connect()
        rabbitmq_client.consume_messages(callback)
    except KeyboardInterrupt:
        logger.info("Consumidor detenido por el usuario")
        rabbitmq_client.close()
    except Exception as e:
        logger.error(f"Error en el consumidor: {e}")
        rabbitmq_client.close()
