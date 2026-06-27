import pika
import time
import sys

connection= pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))

def main():
    try:
        channel=connection.channel()
        # This line declares a queue named 'hello' with the durable flag set to True, which means that the queue will survive a broker restart. The arguments parameter is used to specify additional properties for the queue, in this case, setting the queue type to 'quorum'.
        channel.queue_declare(queue='hello',durable=True,arguments={'x-queue-type':'quorum'})

        def callback(ch, method, properties, body):
            print(" [x] Received %r" % body)
            time.sleep(body.count(b'.')*5)
            print(" [x] Done")
            
            # This line sends an acknowledgment to RabbitMQ that the message has been processed successfully. The delivery_tag is a unique identifier for the message, and it is used to acknowledge the specific message that was received. This is important for ensuring that messages are not lost and that they are only removed from the queue once they have been successfully processed.
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        #For fair dispatch, we need to set prefetch_count=1. This tells RabbitMQ not to give more than one message to a worker at a time. Or, in other words, don't dispatch a new message to a worker until it has processed and acknowledged the previous one. Instead, it will dispatch it to the next worker that is not still busy.
        channel.basic_qos(prefetch_count=1)
        # This tells RabbitMQ that this particular callback function is going to be used to process messages from the queue named 'hello'. When a message is received, the callback function will be called with the message as an argument.
        channel.basic_consume(queue='hello', on_message_callback=callback)

        print(' [*] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()
    except Exception as e:
        print(f"Error occurred: {e}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        sys.exit(0) 