from fastapi import APIRouter
from pydantic import BaseModel

from MySQL_Replica.utils import connect_to_database

class Shard(BaseModel):
    name: str
    nickname: str = None

mysql_router = APIRouter(prefix="/sharding", tags=["MySQL Sharding"])
shard_db1 = connect_to_database("localhost", "api_user", "Arcsaber@0001", 3306, database="shard1")
shard_db2 = connect_to_database("localhost", "api_user", "Arcsaber@0001", 3307, database="shard2")
    

@mysql_router.post("/add_shard")
def add_shard(shard: Shard):
    # Connect to the specific database that holds the `shards` table
    
    try:
        if not shard.name or not shard.name.strip():
            return {"message": "Invalid shard name. Must be a non-empty string starting with A-Z."}

        first = shard.name.strip()[0].lower()
        if "a" <= first <= "m":
            cursor = shard_db1.cursor()
            cursor.execute(
                "INSERT INTO sharded_names (name, nickname) VALUES (%s, %s)",
                (shard.name, shard.nickname),
            )
            shard_db1.commit()
            return {"message": f"Shard '{shard.name}' added to shard_db1!"}
        elif "n" <= first <= "z":
            cursor = shard_db2.cursor()
            cursor.execute(
                "INSERT INTO sharded_names (name, nickname) VALUES (%s, %s)",
                (shard.name, shard.nickname),
            )
            shard_db2.commit()
            return {"message": f"Shard '{shard.name}' added to shard_db2!"}
        else:
            return {"message": "Invalid shard name. Must start with a letter between A-M or N-Z."}
    except Exception as e:
        return {"message": f"An error occurred: {e}"}
    finally:
        shard_db1.close()
        shard_db2.close()
    
    
    