from fastapi import APIRouter
from pydantic import BaseModel
import asyncio
import random
from .post_service import get_post
from .profile_service import get_profile
from . import utils
from .utils import get_redis_client, subscribe_to_profile_working_channel


circuit_breakers_router = APIRouter(prefix="/circuit-breakers", tags=["Circuit Breakers"])

class PostRequest(BaseModel):
    name: str
    
class PostResponse(BaseModel):
    default_post: str
    recommended_post: str | None = None
    error: str | None = None
    

@circuit_breakers_router.get("/{name}/get-post")
async def get_post_route(name: str):
    asyncio.create_task(subscribe_to_profile_working_channel())
    default_post = await get_post()
    if utils.profile_working:
        profile_info = await get_profile(name)
        recommended_post = random.choice(profile_info.get("watches_post", [])) if profile_info else None
        return PostResponse(default_post=default_post, recommended_post=recommended_post)

    return PostResponse(default_post=default_post, error="Profile service is not working. Returning default post.")


@circuit_breakers_router.post("/trigger-profile-working")  
async def trigger_profile_working(trigger: bool):    
    await get_redis_client().publish("profile_working_channel", str(trigger))
    return {"message": "Profile service is updated successfully.","triggered": trigger}

