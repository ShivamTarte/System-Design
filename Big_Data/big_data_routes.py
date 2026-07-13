import asyncio
import json

from fastapi import APIRouter
from kafka import KafkaProducer
from pydantic import BaseModel

from .kafka_consumer import collect_blog_messages

router = APIRouter(prefix="/big_data", tags=["Big_Data"])


class DataRequest(BaseModel):
    user: str
    blog_title: str
    content: str | None = None


async def _run_consumer():
    try:
        collect_blog_messages(limit=5)
    except Exception as exc:
        print(f"Kafka consumer task failed: {exc}")


@router.post("/kafka_publish")
async def push_events(event: DataRequest):
    producer = None
    try:
        producer = KafkaProducer(
            bootstrap_servers="localhost:9092",
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        payload = event.model_dump()
        producer.send("blog_published", value=payload)
        producer.flush()

        asyncio.create_task(_run_consumer())
        return {"status": "published"}
    except Exception as e:
        print(f"Error occurred at: {e}")
        return {"status": "failed", "error": str(e)}
    finally:
        if producer is not None:
            producer.close()

