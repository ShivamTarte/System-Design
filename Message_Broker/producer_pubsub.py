import pika
import sys

connection=pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
try:
    channel=connection.channel()
    
    # This line declares a queue named 'hello' with the durable flag set to True, which means that the queue will survive a broker restart. The arguments parameter is used to specify additional properties for the queue, in this case, setting the queue type to 'quorum'.
    channel.exchange_declare(exchange='notifications', exchange_type='fanout')

    message=".".join(sys.argv[1:]) or "Hello World!"
    
    # This line publishes a message to the queue named 'hello'. The exchange parameter is set to an empty string, which means that the default exchange will be used. The routing_key parameter specifies the name of the queue to which the message should be sent. The body parameter contains the actual message content. The properties parameter is used to set additional properties for the message, in this case, setting the delivery_mode to Persistent, which means that the message will be saved to disk and will survive a broker restart.
    channel.basic_publish(exchange='notifications',routing_key='',body=message,properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent))
    print(" [x] Sent %r" % message)
except Exception as e:
    print(f"Error occurred: {e}")
    sys.exit(1)
finally:
    connection.close()

