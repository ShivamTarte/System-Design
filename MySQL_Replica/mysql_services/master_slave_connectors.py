import mysql.connector
from fastapi import APIRouter


mysql_router = APIRouter(prefix="/read_replicas", tags=["MySQL Replication Connectors"])

def connect_to_database(host, user, passwd, port):
    db = mysql.connector.connect(
    host = host,                # Localhost for local connection
    user = user,
    passwd = passwd,
        port = port
    )
    return db
    
    
@mysql_router.get("/connect_master")
def connect_master():
    master_db = connect_to_database("localhost", "api_user", "Arcsaber@0001", 3306)
    try:
        if master_db.is_connected():
            return {"message": "Successfully connected to the master database!"}
    except Exception as e:
        return {"message": f"An error occurred: {e}"}
    finally:
        master_db.close()
        
@mysql_router.get("/connect_replica")
def connect_replica():
    replica_db = connect_to_database("localhost", "api_user", "Arcsaber@0001", 3307)
    try:
        if replica_db.is_connected():
            return {"message": "Successfully connected to the replica database!"}
    except Exception as e:
        return {"message": f"An error occurred: {e}"}
    finally:
        replica_db.close()
    