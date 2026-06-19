from fastapi import FastAPI
import uvicorn
from MySQL_Replica.mysql_replica.master_slave_connectors import mysql_router
from MySQL_Replica.mysql_sharding.mysql_shard import mysql_router as shard_router
from Redis_services.redis_connectors import redis_router
from MySQL_Replica.mysql_replica.mysql_connectors import mysql_connector


app = FastAPI()
app.include_router(mysql_router)
app.include_router(shard_router)
app.include_router(mysql_connector)
app.include_router(redis_router)

def main():
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()