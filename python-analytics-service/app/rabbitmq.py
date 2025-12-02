"""
Configuración y utilidades de RabbitMQ
"""
import pika
import json
import logging
import time
from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class RabbitMQClient:
    """Cliente de RabbitMQ para publicar y consumir mensajes con reintentos automáticos"""
    
    def __init__(self, max_retries=3, retry_delay=2):
        self.connection = None
        self.channel = None
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
    def connect(self):
        """Establecer conexión con RabbitMQ con reintentos"""
        for attempt in range(self.max_retries):
            try:
                credentials = pika.PlainCredentials(
                    settings.rabbitmq_user,
                    settings.rabbitmq_password
                )
                parameters = pika.ConnectionParameters(
                    host=settings.rabbitmq_host,
                    port=settings.rabbitmq_port,
                    credentials=credentials,
                    heartbeat=600,
                    blocked_connection_timeout=300,
                    connection_attempts=3,
                    retry_delay=2
                )
                self.connection = pika.BlockingConnection(parameters)
                self.channel = self.connection.channel()
                self.channel.queue_declare(queue=settings.rabbitmq_queue, durable=True)
                logger.info(f"✓ Conectado a RabbitMQ en {settings.rabbitmq_host}:{settings.rabbitmq_port}")
                return True
            except Exception as e:
                logger.warning(f"Intento {attempt + 1}/{self.max_retries} fallido: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"Error al conectar con RabbitMQ después de {self.max_retries} intentos")
                    raise
        return False
    
    def _ensure_connection(self):
        """Asegurar que la conexión está activa, reconectar si es necesario"""
        if not self.connection or self.connection.is_closed:
            logger.info("Reconectando a RabbitMQ...")
            self.connect()
        if not self.channel or self.channel.is_closed:
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue=settings.rabbitmq_queue, durable=True)
    
    def publish_message(self, message: dict, retry=True):
        """Publicar mensaje en la cola con reintentos automáticos"""
        for attempt in range(self.max_retries if retry else 1):
            try:
                self._ensure_connection()
                
                self.channel.basic_publish(
                    exchange='',
                    routing_key=settings.rabbitmq_queue,
                    body=json.dumps(message),
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # Hacer mensaje persistente
                        content_type='application/json'
                    )
                )
                logger.info(f"✓ Mensaje publicado exitosamente: {message.get('event', 'unknown')}")
                return True
            except Exception as e:
                logger.error(f"Error en intento {attempt + 1}/{self.max_retries}: {e}")
                if attempt < self.max_retries - 1 and retry:
                    time.sleep(self.retry_delay)
                    try:
                        self.connect()
                    except:
                        pass
                else:
                    logger.error(f"Error al publicar mensaje después de {self.max_retries} intentos", exc_info=True)
                    raise
        return False
    
    def consume_messages(self, callback):
        """Consumir mensajes de la cola"""
        try:
            if not self.channel:
                self.connect()
                
            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(
                queue=settings.rabbitmq_queue,
                on_message_callback=callback
            )
            logger.info("Esperando mensajes...")
            self.channel.start_consuming()
        except Exception as e:
            logger.error(f"Error al consumir mensajes: {e}")
            raise
    
    def close(self):
        """Cerrar conexión"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("Conexión a RabbitMQ cerrada")


# Instancia global del cliente
rabbitmq_client = RabbitMQClient()
