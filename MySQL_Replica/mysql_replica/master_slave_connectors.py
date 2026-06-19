import os
from fastapi import APIRouter
from MySQL_Replica.utils import connect_to_database
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

mysql_router = APIRouter(prefix="/read_replicas", tags=["MySQL Replication Connectors"])


master_db = connect_to_database(
    os.environ["MYSQL_HOST"],
    os.environ["MYSQL_USER"],
    os.environ["MYSQL_PASSWORD"],
    3306
)
replica_db = connect_to_database(
    os.environ["MYSQL_REPLICA_HOST"],
    os.environ["MYSQL_USER"],
    os.environ["MYSQL_PASSWORD"],
    3307
)

@mysql_router.get("/connect_master")
def connect_master():
    try:
        if master_db.is_connected():
            return {"message": "Successfully connected to the master database!"}
    except Exception as e:
        return {"message": f"An error occurred: {e}"}
    finally:
        master_db.close()
        
@mysql_router.get("/connect_replica")
def connect_replica():
    try:
        if replica_db.is_connected():
            return {"message": "Successfully connected to the replica database!"}
    except Exception as e:
        return {"message": f"An error occurred: {e}"}
    finally:
        replica_db.close()
    