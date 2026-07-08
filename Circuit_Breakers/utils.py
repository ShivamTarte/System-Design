
import redis.asyncio as redis

#Simulating the profile service working status with a global variable, in circuit breaker pattern, we can use Redis pub/sub to update the status of the profile service across multiple instances of the application inside database. This way, when the profile service is down, all instances of the application will be aware of it and can avoid making requests to the profile service until it is back up and running.
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


