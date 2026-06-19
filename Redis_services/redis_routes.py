from fastapi import APIRouter
from redis_connectors import RedisConnector
import time

redis_connector = RedisConnector()
redis_router = APIRouter(prefix="/redis", tags=["Redis Connectors"])

@redis_router.post("/store_json")
async def time_calculation(key: str, json_data: str):
    start_time = time.time()
    # Simulate storing JSON data in Redis
    await redis_connector.store_json(key, json_data)
    end_time = time.time()
    elapsed_time = end_time - start_time
    return {"message": f"JSON data stored under key: {key}", "elapsed_time": elapsed_time}

@redis_router.get("/retrieve_json")
async def time_calculation_retrieve_all():
    start_time = time.time()
    # Simulate retrieving JSON data from Redis
    json_collection = await redis_connector.retrieve_json_all()
    end_time = time.time()
    elapsed_time = end_time - start_time
    if json_collection:
        return {"message": "All JSON data retrieved", "json_data": json_collection, "elapsed_time": elapsed_time}
    else:
        return {"message": "No data found", "elapsed_time": elapsed_time}