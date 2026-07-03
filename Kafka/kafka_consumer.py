from kafka import KafkaConsumer
import json

# Before running this script, ensure that the Kafka server is running and the topic "python-test-topic" exists.
consumer = KafkaConsumer(
    "python-test-topic",
    bootstrap_servers="localhost:9092",
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id="python-group",
    value_deserializer=lambda m: json.loads(m.decode("utf-8"))
)

print("Waiting for messages...")

for message in consumer:
    print(message.value)