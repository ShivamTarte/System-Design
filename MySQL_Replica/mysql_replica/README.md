# MySQL Master-Slave Replication

This module demonstrates **MySQL Master-Slave Replication**, a technique for creating read replicas that distribute read queries and improve overall system scalability.

## 📋 Overview

Master-Slave Replication allows you to:
- Create read-only replicas of your master database
- Distribute read queries across multiple servers
- Maintain automatic data synchronization
- Improve read performance and system availability

## 🏗️ Architecture

```
┌──────────────────┐
│  Master Database │
│   (Write Query)  │
└────────┬─────────┘
         │
         │ Binary Log Replication
         │
    ┌────▼─────────────────────────┐
    │                               │
    │  Replica 1 (Read Query)       │
    │  Replica 2 (Read Query)       │
    │  Replica 3 (Read Query)       │
    │                               │
    └───────────────────────────────┘
```

## 📁 Module Files

### `master_slave_connectors.py`

Handles connections to both master and replica databases with FastAPI routes:

- **Purpose**: Test connectivity and demonstrate basic connection pooling
- **Master Router**: `/read_replicas/connect_master`
- **Replica Router**: `/read_replicas/connect_replica`
- **Connection Strategy**: Creates connections on demand, closes after verification

**Key Components:**
```python
master_db = connect_to_database(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    port=3306  # Default master port
)

replica_db = connect_to_database(
    host=MYSQL_REPLICA_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    port=3307  # Replica port (different host/instance)
)
```

### `mysql_connectors.py`

Demonstrates data operations (insert/read) with performance timing:

- **Purpose**: Store and retrieve JSON data with elapsed time measurement
- **Endpoints**:
  - `POST /mysql_connectors/store_json` - Insert data
  - `GET /mysql_connectors/retrieve_json` - Query data
- **Features**:
  - Automatic connection management (dependency injection)
  - Performance timing for benchmarking
  - Error handling and connection cleanup

**Data Model:**
```python
class JsonStructure(BaseModel):
    name: str
    age: int | None = None
    email: str | None = None
    job: str | None = None
```

## 🔧 Setup & Configuration

### 1. Configure Master Database

```sql
-- Create database
CREATE DATABASE compare_redis;
USE compare_redis;

-- Create table
CREATE TABLE json_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    age INT,
    email VARCHAR(255),
    job VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index
CREATE INDEX idx_name ON json_data(name);
```

### 2. Configure Replica Database

```sql
CREATE DATABASE compare_redis;
USE compare_redis;

-- Same table structure as master
CREATE TABLE json_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    age INT,
    email VARCHAR(255),
    job VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3. Set Up Replication

**On Master:**
```sql
-- Enable binary logging in my.cnf
[mysqld]
server-id=1
log_bin=mysql-bin
binlog_format=ROW

-- Create replication user
CREATE USER 'repl_user'@'%' IDENTIFIED BY 'repl_password';
GRANT REPLICATION SLAVE ON *.* TO 'repl_user'@'%';
FLUSH PRIVILEGES;

-- Check master status
SHOW MASTER STATUS;
-- Note the File and Position values
```

**On Replica:**
```sql
-- Enable relay logging in my.cnf
[mysqld]
server-id=2
relay-log=mysql-relay-bin

-- Configure replication
CHANGE MASTER TO
    MASTER_HOST='master_host',
    MASTER_USER='repl_user',
    MASTER_PASSWORD='repl_password',
    MASTER_LOG_FILE='mysql-bin.000001',
    MASTER_LOG_POS=0;

-- Start replication
START SLAVE;

-- Check status
SHOW SLAVE STATUS\G
```

### 4. Environment Configuration

```env
MYSQL_HOST=localhost           # Master host
MYSQL_USER=root               # Database user
MYSQL_PASSWORD=your_password  # Database password
MYSQL_REPLICA_HOST=localhost  # Replica host
```

## 🌐 API Usage Examples

### Test Master Connection

```bash
curl http://127.0.0.1:8000/read_replicas/connect_master
```

**Response:**
```json
{
  "message": "Successfully connected to the master database!"
}
```

### Test Replica Connection

```bash
curl http://127.0.0.1:8000/read_replicas/connect_replica
```

**Response:**
```json
{
  "message": "Successfully connected to the replica database!"
}
```

### Store JSON Data (Master Write)

```bash
curl -X POST http://127.0.0.1:8000/mysql_connectors/store_json \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "age": 30,
    "email": "john@example.com",
    "job": "Software Engineer"
  }'
```

**Response:**
```json
{
  "message": "JSON data stored successfully",
  "elapsed_time": 0.0234,
  "json_data": null
}
```

### Retrieve JSON Data (Replica Read)

```bash
curl http://127.0.0.1:8000/mysql_connectors/retrieve_json
```

**Response:**
```json
{
  "message": "Data retrieved successfully",
  "elapsed_time": 0.0156,
  "json_data": [
    {
      "name": "John Doe",
      "age": 30,
      "email": "john@example.com",
      "job": "Software Engineer"
    }
  ]
}
```

## 📊 Connection Management

### Dependency Injection Pattern

The module uses FastAPI's dependency injection for clean connection management:

```python
def get_db():
    db = connect_to_database(...)
    try:
        yield db  # Provide connection
    finally:
        try:
            db.close()  # Cleanup
        except Exception:
            pass
```

**Benefits:**
- Automatic connection cleanup
- Consistent error handling
- Testable endpoints

### Connection Pooling

For production use, consider implementing connection pooling:

```python
from mysql.connector import pooling

dbconfig = {
    "host": MYSQL_HOST,
    "user": MYSQL_USER,
    "password": MYSQL_PASSWORD,
    "database": "compare_redis"
}

pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=5,
    **dbconfig
)

connection = pool.get_connection()
```

## ⏱️ Performance Monitoring

The endpoints measure and return elapsed time for operations:

```python
start_time = time.time()
# ... perform database operation ...
elapsed_time = time.time() - start_time
```

**Use this data to:**
- Compare write vs read performance
- Identify query bottlenecks
- Monitor replication lag effects

## 🔍 Monitoring Replication Health

### Check Replica Status

```sql
SHOW SLAVE STATUS\G
```

**Key Metrics:**
- `Seconds_Behind_Master`: Replication lag in seconds
- `Slave_IO_Running`: YES/NO (IO thread reading binary log)
- `Slave_SQL_Running`: YES/NO (SQL thread applying changes)
- `Last_Error`: Any replication errors

### Monitor from Python

```python
def check_replication_status(replica_db):
    cursor = replica_db.cursor(dictionary=True)
    cursor.execute("SHOW SLAVE STATUS")
    status = cursor.fetchone()
    
    lag = status['Seconds_Behind_Master']
    io_running = status['Slave_IO_Running'] == 'Yes'
    sql_running = status['Slave_SQL_Running'] == 'Yes'
    
    return {
        'lag_seconds': lag,
        'io_running': io_running,
        'sql_running': sql_running
    }
```

## 🚀 Best Practices

1. **Connection Management**
   - Always close connections after use
   - Use connection pooling for multiple operations
   - Implement exponential backoff for retries

2. **Error Handling**
   - Log all database errors
   - Implement circuit breakers for reliability
   - Handle replication lag gracefully

3. **Performance**
   - Use indexes on frequently queried columns
   - Batch insert operations when possible
   - Monitor query performance regularly

4. **Replication**
   - Monitor replication lag actively
   - Set up alerts for replication failures
   - Test failover procedures regularly
   - Keep master and replica in sync

5. **Security**
   - Use environment variables for credentials
   - Implement proper database user permissions
   - Encrypt connections (SSL/TLS for remote connections)
   - Restrict access by firewall rules

## ⚠️ Common Issues & Solutions

### "Replication Failed to Initialize"

**Cause:** Master and replica binary log positions don't match

**Solution:**
```sql
-- On master, get current position
SHOW MASTER STATUS;

-- On replica, reset and reconfigure
STOP SLAVE;
RESET SLAVE;
CHANGE MASTER TO
    MASTER_HOST='...',
    MASTER_LOG_FILE='<file_from_SHOW_MASTER_STATUS>',
    MASTER_LOG_POS=<pos_from_SHOW_MASTER_STATUS>;
START SLAVE;
```

### "Connection Refused"

**Cause:** MySQL service not running or firewall blocking

**Solution:**
- Verify MySQL is running: `mysql -h localhost -u root -p`
- Check firewall rules for port 3306/3307
- Verify credentials in `.env`

### "Seconds_Behind_Master" Increasing

**Cause:** Replica can't keep up with master writes

**Solution:**
- Analyze slow queries on replica
- Increase replica hardware resources
- Reduce write rate on master
- Check network latency

## 📚 Related Documentation

- [Parent README](../README.md) - Overall MySQL Replication & Sharding guide
- [MySQL Connectors](./mysql_connectors.py) - Data operation details
- [Master-Slave Connectors](./master_slave_connectors.py) - Connection code

## 🔗 External Resources

- [MySQL Replication Documentation](https://dev.mysql.com/doc/refman/8.0/en/replication.html)
- [MySQL Connector/Python](https://dev.mysql.com/doc/connector-python/en/)
- [FastAPI Dependency Injection](https://fastapi.tiangolo.com/tutorial/dependencies/)

## 📞 Support

For issues or questions:
1. Check this README and related documentation
2. Review MySQL error logs
3. Verify replication status with `SHOW SLAVE STATUS`
4. Consult MySQL official documentation
