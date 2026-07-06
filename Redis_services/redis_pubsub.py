import asyncio
from time import time
import redis
import os
import asyncio
import os
from typing import List, Union, Optional

import redis


class PubSubConnector:
    def __init__(self, host: Optional[str] = None, port: Optional[int] = None, db: Optional[int] = None):
        self.host = host or os.getenv('REDIS_HOST', 'localhost')
        self.port = port or int(os.getenv('REDIS_PORT', '6379'))
        self.db = db

        # Separate clients for publishing and subscribing
        self.publisher = redis.Redis(host=self.host, port=self.port, db=self.db, decode_responses=True)
        self.subscriber = redis.Redis(host=self.host, port=self.port, db=self.db, decode_responses=True)
        self.pubsub = self.subscriber.pubsub()

        # state
        self.sub_channel: List[str] = []
        self.messages: List = []
        self.worker_thread = None

    def custom_handler(self, message: dict):
        # redis-py pubsub handler gets different message types (subscribe/unsubscribe/message)
        if not message:
            return None
        mtype = message.get('type')
        if mtype != 'message':
            return None
        data = message.get('data')
        channel = message.get('channel')
        print(f"Received message: {data} on channel: {channel}")
        self.messages.append(data)
        return data

    async def add_channel(self, channel: Union[str, List[str]]):
        try:
            if isinstance(channel, str):
                self.sub_channel.append(channel)
            else:
                self.sub_channel.extend(channel)
            return self.sub_channel
        except redis.exceptions.ConnectionError as exc:
            print(f"Redis connection error: {exc}")
            raise

    async def subscribe(self):
        """Register subscriptions and start the pubsub background thread."""
        try:
            def subscribe_sync():
                for ch in self.sub_channel:
                    # try to register handler; if not supported, fall back to subscribe without callback
                    try:
                        self.pubsub.subscribe(**{ch: self.custom_handler})
                    except TypeError:
                        self.pubsub.subscribe(ch)

                if self.worker_thread is None:
                    self.worker_thread = self.pubsub.run_in_thread(sleep_time=0.01)

            await asyncio.to_thread(subscribe_sync)
            print(f"Subscribed to channel(s): {self.sub_channel}")
            return self.sub_channel
        except redis.exceptions.ConnectionError as exc:
            print(f"Redis connection error: {exc}")
            raise

    async def unsubscribe(self):
        try:
            def unsubscribe_sync():
                for ch in list(self.sub_channel):
                    self.pubsub.unsubscribe(ch)
                if self.worker_thread is not None:
                    self.worker_thread.stop()
                    self.worker_thread = None
                self.sub_channel.clear()

            await asyncio.to_thread(unsubscribe_sync)
            print("Unsubscribed from all channels")
            return self.sub_channel
        except redis.exceptions.ConnectionError as exc:
            print(f"Redis connection error: {exc}")
            raise

    async def publish(self, channel: Union[str, List[str]], payload) -> tuple[List[str], int]:
        channel_list: List[str] = [channel] if isinstance(channel, str) else list(channel)

        def publish_sync():
            total = 0
            for ch in channel_list:
                total += self.publisher.publish(ch, payload)
            return total

        try:
            delivered = await asyncio.to_thread(publish_sync)
            print(f"Published message: {payload} to channel(s): {channel_list} (delivered={delivered})")
            return channel_list, delivered
        except redis.exceptions.ConnectionError as exc:
            print(f"Redis connection error: {exc}")
            raise




