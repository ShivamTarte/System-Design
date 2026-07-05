import asyncio
from time import time

import redis
import os

class PubSubConnector:
    def __init__(self, host=None, port=None, db=None):
        self.host = host or os.getenv('REDIS_HOST')
        self.port= port or int(os.getenv('REDIS_PORT'))
        self.redis_client= redis.Redis(host=self.host, port=self.port, decode_responses=True)
        self.pub_client = self.redis_client.pubsub()
        self.sub_client = self.redis_client.pubsub()
        self.channel=["news"]
        
    def custom_handler(self,message):
        print(f"Received message: {message['data']} on channel: {message['channel']}")
        
    async def subscribe(self, channel):
        [self.pub_client.subscribe(**{ch: self.custom_handler}) for ch in channel]
        print(f"Subscribed to channel: {channel}")
        worker_thread=self.pub_client.run_in_thread(sleep_time=0.001)
        
        async for _ in range(3):
            print("Main script processing separate tasks...")
            await asyncio.sleep(1)

            # Clean up and stop the thread when finished
            worker_thread.stop()
            
    async def publish(self, channel, message):
        
        
        
        
        