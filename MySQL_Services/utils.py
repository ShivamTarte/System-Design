import mysql.connector

def connect_to_database(host, user, passwd, port, database=None):
    params = {
        'host': host,
        'user': user,
        'passwd': passwd,
        'port': port,
    }
    if database:
        params['database'] = database

    db = mysql.connector.connect(**params)
    return db