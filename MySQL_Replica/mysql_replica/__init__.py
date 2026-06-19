from fastapi import APIRouter
from master_slave_connectors import mysql_router as master_slave_router
from mysql_connectors import mysql_router as connector_router

mysql_router = APIRouter(prefix="/mysql_connectors", tags=["MySQL Connectors"])

mysql_router.include_router(master_slave_router)
mysql_router.include_router(connector_router)
