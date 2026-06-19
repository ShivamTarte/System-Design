from fastapi import APIRouter
from redis_connectors import RedisConnector
import time
from pydantic import BaseModel

redis_connector = RedisConnector()
redis_router = APIRouter(prefix="/redis", tags=["Redis Connectors"])

class RedisJsonStructure(BaseModel):
    key: str
    json_data: str
    
class RedisResponse(BaseModel):
    message: str
    elapsed_time: float
    json_data: list[RedisJsonStructure] | None = None

@redis_router.post("/store_json",response_model=RedisResponse)
async def time_calculation(payload: RedisJsonStructure):
    start_time = time.time()
    # Simulate storing JSON data in Redis
    await redis_connector.store_json(payload.key, payload.json_data)
    end_time = time.time()
    elapsed_time = end_time - start_time
    return RedisResponse(message=f"JSON data stored under key: {payload.key}", elapsed_time=elapsed_time)

@redis_router.get("/retrieve_json", response_model=RedisResponse)
async def time_calculation_retrieve_all():
    start_time = time.time()
    # Simulate retrieving JSON data from Redis
    json_collection = await redis_connector.retrieve_json_all()
    end_time = time.time()
    elapsed_time = end_time - start_time
    if json_collection:
        result = [RedisJsonStructure(key=key, json_data=value) for item in json_collection for key, value in item.items()]
        return RedisResponse(message="All JSON data retrieved", json_data=result, elapsed_time=elapsed_time)
    else:
        return RedisResponse(message="No data found", elapsed_time=elapsed_time)