import pika
import sys

connection=pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
try:
    channel=connection.channel()
    channel.queue_declare(queue='hello',durable=True,arguments={'x-queue-type':'quorum'})

    message=".".join(sys.argv[1:]) or "Hello World!"
    channel.basic_publish(exchange='',routing_key='hello',body=message,properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent))
    print(" [x] Sent %r" % message)
except Exception as e:
    print(f"Error occurred: {e}")
    sys.exit(1)
finally:
    connection.close()

