from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from redis.exceptions import RedisError

from .redis_connectors import RedisConnector
import time

redis_connector = RedisConnector()
redis_router = APIRouter(prefix="/redis", tags=["Redis Connectors"])

class RedisJsonStructure(BaseModel):
    key: str
    json_data: Any
    
class RedisResponse(BaseModel):
    message: str
    elapsed_time: float
    json_data: list[RedisJsonStructure] | None = None

@redis_router.post("/store_json", response_model=RedisResponse)
async def time_calculation(payload: RedisJsonStructure):
    start_time = time.time()
    try:
        await redis_connector.store_json(payload.key, payload.json_data)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RedisError as exc:
        raise HTTPException(status_code=503, detail="Redis service unavailable") from exc
    end_time = time.time()
    elapsed_time = end_time - start_time
    return RedisResponse(message=f"JSON data stored under key: {payload.key}", elapsed_time=elapsed_time)

@redis_router.get("/retrieve_json", response_model=RedisResponse)
async def time_calculation_retrieve_all():
    start_time = time.time()
    try:
        json_collection = await redis_connector.retrieve_json_all()
    except RedisError as exc:
        raise HTTPException(status_code=503, detail="Redis service unavailable") from exc
    end_time = time.time()
    elapsed_time = end_time - start_time
    if json_collection:
        result = [RedisJsonStructure(key=key, json_data=value) for item in json_collection for key, value in item.items()]
        return RedisResponse(message="All JSON data retrieved", elapsed_time=elapsed_time)
    else:
        return RedisResponse(message="No data found", elapsed_time=elapsed_time)
    
@redis_router.get("/retrieve_json/{name}", response_model=RedisResponse)
async def time_calculation_retrieve_name(name: str):
    start_time = time.time()
    try:
        value = await redis_connector.retrieve_json_by_name(name)
        if value is None:
            raise HTTPException(status_code=404, detail=f"No data found for name: {name}")
        json_data = value.decode('utf-8') if isinstance(value, (bytes, bytearray)) else str(value)
    except RedisError as exc:
        raise HTTPException(status_code=503, detail="Redis service unavailable") from exc
    end_time = time.time()
    elapsed_time = end_time - start_time
    return RedisResponse(message=f"JSON data retrieved for name: {name}", elapsed_time=elapsed_time, json_data=[RedisJsonStructure(key=name, json_data=json_data)])