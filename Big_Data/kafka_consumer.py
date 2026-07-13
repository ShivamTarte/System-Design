import json
import os
from datetime import datetime

from kafka import KafkaConsumer
from pyspark.sql import SparkSession

try:
    from .fetch_data import fetch_data
except ImportError:  # pragma: no cover - fallback for direct execution
    from Big_Data.fetch_data import fetch_data


def get_spark_session():
    spark = (
        SparkSession.builder
        .master("local[*]")
        .appName("KafkaBlogConsumer")
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")
    return spark


def collect_blog_messages(topic="blog_published", limit=10, bootstrap_servers="localhost:9092"):
    spark = None
    try:
        spark = get_spark_session()
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=bootstrap_servers,
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            group_id="read_user_request",
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        )

        blog_data = []
        print(f"Waiting for messages on topic: {topic}...")

        for message in consumer:
            user = message.get("user")
            result = fetch_data(user) if user else None

            blog_record = {
                "user": user,
                "blog_title": message.get("blog_title"),
                "content": message.get("content"),
                "user_details": result,
                "processed_timestamp": datetime.now().isoformat(),
            }
            blog_data.append(blog_record)

            if len(blog_data) >= limit:
                break

        if blog_data:
            df = spark.createDataFrame(blog_data)
            output_dir = os.path.join("results", "kafka_blogs")
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"blogs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            df.write.mode("overwrite").json(output_path)
            print(f"Blog data saved to JSON: {output_path}")
            print(f"Total records processed: {len(blog_data)}")
            df.show(5, truncate=False)
        else:
            output_path = None
            print("No messages received")

        return blog_data, output_path
    except Exception as exc:
        print(f"PySpark consumer failed: {exc}")
        return [], None
    finally:
        if spark is not None:
            spark.stop()
