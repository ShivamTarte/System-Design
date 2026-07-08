
import redis.asyncio as redis
import asyncio

profile_working = True
PROFILE_WORKING_CHANNEL = "profile_working_channel"


def get_redis_client():
    return redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)


async def message_handler(message):
    global profile_working

    if isinstance(message, dict) and message.get("type") == "message":
        message = message.get("data")

    if isinstance(message, bytes):
        message = message.decode("utf-8")

    if str(message).lower() in {"true", "1", "yes"}:
        profile_working = True
        print("Profile service is now working.")
    else:
        profile_working = False
        print("Profile service is not working.")


async def subscribe_to_profile_working_channel():
    client = get_redis_client()
    pubsub = client.pubsub()
    await pubsub.subscribe(PROFILE_WORKING_CHANNEL)

    async for message in pubsub.listen():
        await message_handler(message)


