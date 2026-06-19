from fastapi import APIRouter, Depends, HTTPException
from MySQL_Replica.utils import connect_to_database
from pydantic import BaseModel
import time
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

mysql_connector = APIRouter(prefix="/mysql_connectors", tags=["MySQL Connectors"])


class JsonStructure(BaseModel):
    name: str
    age: int | None = None
    email: str | None = None
    job: str | None = None


class OutputData(BaseModel):
    message: str
    elapsed_time: float
    json_data: list[JsonStructure] | None = None


def get_db():
    db = connect_to_database(
        os.environ["MYSQL_HOST"],
        os.environ["MYSQL_USER"],
        os.environ["MYSQL_PASSWORD"],
        3306,
        database="compare_redis",
    )
    try:
        yield db
    finally:
        try:
            db.close()
        except Exception:
            pass


@mysql_connector.post("/store_json", response_model=OutputData)
def time_store_json(payload: JsonStructure, db=Depends(get_db)):
    start_time = time.time()
    cursor = None
    try:
        query = "INSERT INTO json_data (name, age, email, job) VALUES (%s, %s, %s, %s)"
        cursor = db.cursor()
        cursor.execute(query, (payload.name, payload.age, payload.email, payload.job))
        db.commit()
        elapsed = time.time() - start_time
        return OutputData(message="JSON data stored successfully!", elapsed_time=elapsed)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cursor:
            try:
                cursor.close()
            except Exception:
                pass


@mysql_connector.get("/retrieve_json", response_model=OutputData)
def time_retrieve_json(db=Depends(get_db)):
    start_time = time.time()
    cursor = None
    try:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM json_data")
        rows = cursor.fetchall()
        elapsed = time.time() - start_time
        result = [JsonStructure(id=r[0], name=r[1], age=r[2], email=r[3], job=r[4]) for r in rows]
        if result:
            return OutputData(message="All JSON data retrieved", elapsed_time=elapsed)
        else:
            return OutputData(message="No data found", elapsed_time=elapsed, json_data=None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cursor:
            try:
                cursor.close()
            except Exception:
                pass
        

    