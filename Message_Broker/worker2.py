import pika
import time
import sys

connection= pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))

def main():
    try:
        channel=connection.channel()
        channel.queue_declare(queue='hello',durable=True,arguments={'x-queue-type':'quorum'})

        def callback(ch, method, properties, body):
            print(" [x] Received %r" % body)
            time.sleep(body.count(b'.')*5)
            print(" [x] Done")
            ch.basic_ack(delivery_tag=method.delivery_tag)
        
        channel.basic_qos(prefetch_count=1)
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