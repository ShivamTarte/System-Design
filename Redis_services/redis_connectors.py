import redis.asyncio as redis

class RedisConnector:
    def __init__(self, host='localhost', port=6379, db=1):
        self.host = host
        self.port = port
        self.db = db
        max_connections = 5
        pool = redis.ConnectionPool(host=self.host, port=self.port, db=self.db, max_connections=max_connections)
        self.connection = redis.Redis(connection_pool=pool)
        print(f"Connected to Redis at {self.host}:{self.port}, DB: {self.db}")

    async def store_json(self, key, json_data):
        if self.connection:
            await self.connection.set(key, json_data)
            print(f"Stored JSON data under key: {key}")
        else:
            print("No Redis connection established.")
            
    async def retrieve_json_all(self):
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
        

        
    
            
            
        


