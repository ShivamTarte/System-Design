from kafka import KafkaProducer
import json


# Before running this script, ensure that the Kafka server is running and the topic "python-test-topic" exists.
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)
try:
    for i in range(11,20):
        message = {
            "id": i,
            "name": f"User-{i}"
        }
        producer.send("python-test-topic", value=message)

    producer.flush()
except Exception as e:
    print(f"Error occurred while sending messages: {e}")
finally:
    producer.close()

print("Messages sent successfully!")