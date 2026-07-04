import os
import json
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

    @staticmethod
    def _normalize_json_data(json_data):
        if isinstance(json_data, str):
            try:
                return json.loads(json_data)
            except json.JSONDecodeError as exc:
                raise ValueError("json_data must be a valid JSON object, array, or JSON string") from exc

        if isinstance(json_data, (dict, list)):
            return json_data

        if json_data is None:
            return {}

        raise ValueError("json_data must be a JSON object, array, or JSON string")

    @staticmethod
    def _extract_name(payload):
        if isinstance(payload, dict):
            return payload.get("name")

        if isinstance(payload, list):
            for item in payload:
                if isinstance(item, dict) and item.get("name"):
                    return item["name"]

        return None

    async def store_json(self, key_id, json_data):
        if not self.connection:
            raise redis.exceptions.ConnectionError("Redis connection is not configured")

        payload = self._normalize_json_data(json_data)
        if not isinstance(payload, (dict, list)):
            raise ValueError("json_data must be a JSON object or array")

        name = self._extract_name(payload)
        if not name:
            raise ValueError("json_data must include a 'name' field")

        # Prefix key to avoid collision with index sets
        key = f"user:{key_id}"
        try:
            # FIX: Added "$" root path argument required by RedisJSON
            await self.connection.json().set(key, "$", payload)
            print(f"Stored JSON data under key: {key}")

            # Indexing by name using a Set
            await self.connection.sadd(f"name:{name}", key)
        except redis.exceptions.ConnectionError as exc:
            print(f"Redis connection failed during set: {exc}")
            raise

    async def retrieve_json_all(self):
        if not self.connection:
            raise redis.exceptions.ConnectionError("Redis connection is not configured")

        try:
            json_collection = []
            # FIX: Only look for user JSON data keys, avoiding the 'name:*' Set keys
            keys = await self.connection.keys('user:*')
            if not keys:
                return json_collection

            # For RedisJSON, we should use json().mget() instead of standard mget()
            values = await self.connection.json().mget(keys, "$")
            
            for key, value in zip(keys, values):
                key_str = key.decode('utf-8') if isinstance(key, bytes) else str(key)
                # json().mget returns a list representing the path matching (e.g., [data_dict])
                actual_value = value[0] if value else None 
                json_collection.append({key_str: actual_value})
                
            return json_collection
        except redis.exceptions.ConnectionError as exc:
            print(f"Redis connection failed during retrieval: {exc}")
            raise
        
    async def retrieve_json_by_name(self, name: str):
        if not self.connection:
            raise redis.exceptions.ConnectionError("Redis connection is not configured")

        try:
            # Gets all keys associated with this name
            keys = await self.connection.smembers(f"name:{name}")
            if not keys:
                return []
            
            users = []
            for key in keys:
                # FIX: redis-py handles decoding natively for json().get()
                user_data = await self.connection.json().get(key)
                if user_data:
                    users.append(user_data)
                    print(user_data)
            
            # FIX: Return the structured list of dictionaries rather than trying to decode a set
            return users
        except redis.exceptions.ConnectionError as exc:
            print(f"Redis connection failed during retrieval by name: {exc}")
            raise