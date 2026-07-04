from fastapi import FastAPI
import uvicorn
from MySQL_Services.mysql_replica import mysql_router
#from MySQL_Replica.mysql_sharding.mysql_shard import mysql_router as shard_router
from Redis_services.redis_routes import redis_router


app = FastAPI()
app.include_router(mysql_router)
#app.include_router(shard_router)
app.include_router(redis_router)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)