import pika
import json

def start_consumer():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost")
    )
    channel = connection.channel()
    channel.queue_declare(queue="events")

    def callback(ch, method, properties, body):
        event = json.loads(body)
        print("Evento recibido:", event)

    channel.basic_consume(queue="events", on_message_callback=callback, auto_ack=True)
    print("Esperando eventos...")
    channel.start_consuming()
