# Apache Kafka Quickstart Summary (Steps 1 to 6)

## Step 1: Get Kafka
- Download the Kafka package and extract it to a local folder.
- Command:
  ```bash
  tar -xzf kafka_2.13-4.3.1.tgz
  cd kafka_2.13-4.3.1
  ```

## Step 2: Start the Kafka environment
- Generate a unique cluster ID for the Kafka setup.
- Command:
  ```bash
  KAFKA_CLUSTER_ID="$(bin/kafka-storage.sh random-uuid)"
  ```
- Format the log directories before starting Kafka.
- Command:
  ```bash
  bin/kafka-storage.sh format --standalone -t $KAFKA_CLUSTER_ID -c config/server.properties
  ```
- Start the Kafka server so the broker is ready to use.
- Command:
  ```bash
  bin/kafka-server-start.sh config/server.properties
  ```

## Step 3: Create a topic
- Create a topic to store the events you want to send.
- Command:
  ```bash
  bin/kafka-topics.sh --create --topic quickstart-events --bootstrap-server localhost:9092
  ```
- Use the topic name to organize and manage your data stream.

## Step 4: Write events into the topic
- Use the console producer to send sample messages into the topic.
- Command:
  ```bash
  bin/kafka-console-producer.sh --topic quickstart-events --bootstrap-server localhost:9092
  ```
- Each line entered becomes a separate event.

## Step 5: Read the events
- Use the console consumer to read the messages from the topic.
- Command:
  ```bash
  bin/kafka-console-consumer.sh --topic quickstart-events --from-beginning --bootstrap-server localhost:9092
  ```
- This shows that Kafka stores and delivers events reliably.

## Step 6: Import and export data with Kafka Connect
- Use Kafka Connect to move data between Kafka and external systems.
- Command to add plugin path:
  ```bash
  echo "plugin.path=libs/connect-file-4.3.1.jar" >> config/connect-standalone.properties
  ```
- Create sample input data:
  ```bash
  echo -e "foo\nbar" > test.txt
  ```
- Start the connectors:
  ```bash
  bin/connect-standalone.sh config/connect-standalone.properties config/connect-file-source.properties config/connect-file-sink.properties
  ```
- It can read data from files into Kafka and write Kafka data back to files.
- eg. write in test.txt , you would able to see that events occur and test.sink.txt
- you can change configuration file(config/connect-file-source.properties) to change from test file to another file eg os.txt, change topic name then change also in file(config/connect-file-sink.properties) and give same topic name which changed in previous configuration file
- you can use consumer command given in Step 6 to see all events in topics to check.


