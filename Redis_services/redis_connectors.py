import redis

class RedisConnector:
    def __init__(self, host='localhost', port=6379, db=1):
        self.host = host
        self.port = port
        self.db = db
        self.connection = None
        max_connections=5
        pool=redis.ConnectionPool(host=self.host, port=self.port, db=self.db, max_connections=max_connections)
        connection = redis.Redis(connection_pool=pool)
        self.connection = connection
        print(f"Connected to Redis at {self.host}:{self.port}, DB: {self.db}")
        self.keys = self.connection.keys('*')
        print(f"Existing keys in Redis: {self.keys}")

    async def store_json(self, key, json_data):
        if self.connection:
            await self.connection.set(key, json_data)
            print(f"Stored JSON data under key: {key}")
        else:
            print("No Redis connection established.")
            
    async def retrieve_json(self, key):
        json_collection = await self.connection.get(key)
        if json_collection:
            print(f"Retrieved JSON data for key: {key}")
            return json_collection
        else:
            print(f"No data found for key: {key}")
            return None
        

        
    
            
            
        


