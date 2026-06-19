import os
from dotenv import load_dotenv
import redis.asyncio as redis

load_dotenv()

class RedisConnector:
    def __init__(self, host=None, port=None, db=None):
        self.host = host or os.getenv('REDIS_HOST', '127.0.0.1')
        self.port = int(port or os.getenv('REDIS_PORT', '6379'))
        self.db = int(db or os.getenv('REDIS_DB', '1'))
        max_connections = 5
        pool = redis.ConnectionPool(
            host=self.host,
            port=self.port,
            db=self.db,
            max_connections=max_connections,
        )
        self.connection = redis.Redis(connection_pool=pool)
        print(f"Configured Redis at {self.host}:{self.port}, DB: {self.db}")

    async def store_json(self, key, json_data):
        if not self.connection:
            raise redis.exceptions.ConnectionError("Redis connection is not configured")

        try:
            await self.connection.set(key, json_data)
            print(f"Stored JSON data under key: {key}")
        except redis.exceptions.ConnectionError as exc:
            print(f"Redis connection failed during set: {exc}")
            raise

    async def retrieve_json_all(self):
        if not self.connection:
            raise redis.exceptions.ConnectionError("Redis connection is not configured")

        try:
            json_collection = []
            keys = await self.connection.keys('*')
            if not keys:
                return json_collection

            values = await self.connection.mget(keys)
            for key, value in zip(keys, values):
                key_str = key.decode('utf-8') if isinstance(key, (bytes, bytearray)) else str(key)
                if value is None:
                    value_str = None
                else:
                    value_str = value.decode('utf-8') if isinstance(value, (bytes, bytearray)) else str(value)
                json_collection.append({key_str: value_str})
            return json_collection
        except redis.exceptions.ConnectionError as exc:
            print(f"Redis connection failed during retrieval: {exc}")
            raise

        

        
    
            
            
        


