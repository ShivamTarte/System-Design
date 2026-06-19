# Redis Services

This module demonstrates **Redis** as a high-performance, in-memory data store for caching and session management. It includes asynchronous operations, connection pooling, and JSON data support.

## 📋 Overview

Redis Services provides:
- High-performance data storage and retrieval
- Asynchronous operations for non-blocking I/O
- Connection pooling for efficient resource management
- JSON data support
- Performance timing and benchmarking

## 🏗️ Architecture

```
┌─────────────────────────────────┐
│      FastAPI Application        │
└────────────┬────────────────────┘
             │
      ┌──────▼──────────┐
      │  Redis Router   │
      │  (API Endpoints)│
      └────────┬────────┘
             │
      ┌──────▼───────────────┐
      │  Redis Connector     │
      │  (Connection Mgmt)   │
      └────────┬─────────────┘
             │
    ┌────────▼────────────┐
    │  Redis Connection   │
    │  Pool (Max 5 conn)  │
    └─────────────────────┘
             │
    ┌────────▼────────────┐
    │   Redis Server      │
    │  127.0.0.1:6379     │
    │   Database: 1       │
    └─────────────────────┘
```

## 📁 Module Files

### `redis_connectors.py`

Manages Redis connections and operations:

- **Purpose**: Handle connection pooling and async data operations
- **Connection Pooling**: Max 5 concurrent connections
- **Async Support**: Uses `redis.asyncio` for non-blocking operations
- **Error Handling**: Graceful connection failure management

**Key Methods:**
- `store_json(key, json_data)`: Store data asynchronously
- `retrieve_json_all()`: Retrieve all stored data

### `redis_routes.py`

FastAPI routes for Redis operations:

- **Purpose**: Expose Redis functionality via REST API
- **Performance Tracking**: Measures operation timing
- **Error Handling**: Returns appropriate HTTP status codes
- **Response Models**: Structured Pydantic models

**Endpoints:**
- `POST /redis/store_json`: Store JSON data
- `GET /redis/retrieve_json`: Retrieve all JSON data

## 🔧 Setup & Configuration

### Prerequisites

- Redis Server 6.0+
- Python 3.10+
- Dependencies: `redis>=8.0.0`

### 1. Install Redis

**Windows (using Chocolatey):**
```bash
choco install redis-64
```

**Windows (WSL/Ubuntu):**
```bash
sudo apt-get update
sudo apt-get install redis-server
```

**macOS:**
```bash
brew install redis
```

**Docker:**
```bash
docker run -d -p 6379:6379 redis:latest
```

### 2. Start Redis Server

**Windows:**
```bash
redis-server.exe
```

**macOS/Linux:**
```bash
redis-server
```

**Verify Redis is Running:**
```bash
redis-cli ping
# Response: PONG
```

### 3. Configure Environment

Create `.env` file:
```env
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_DB=1
```

**Configuration Details:**
- `REDIS_HOST`: Redis server hostname/IP
- `REDIS_PORT`: Redis server port (default: 6379)
- `REDIS_DB`: Database number (0-15, we use 1 to avoid conflicts)

### 4. Environment Variable Defaults

If not specified in `.env`, defaults are:
```python
host = os.getenv('REDIS_HOST', '127.0.0.1')
port = int(os.getenv('REDIS_PORT', '6379'))
db = int(os.getenv('REDIS_DB', '1'))
```

## 🌐 API Endpoints

### Store JSON Data

```
POST /redis/store_json
```

**Request:**
```bash
curl -X POST http://127.0.0.1:8000/redis/store_json \
  -H "Content-Type: application/json" \
  -d '{
    "key": "user:1",
    "json_data": "{\"name\": \"John\", \"age\": 30, \"email\": \"john@example.com\"}"
  }'
```

**Request Body:**
```json
{
  "key": "user:1",
  "json_data": "{\"name\": \"John\", \"age\": 30}"
}
```

**Response (200 OK):**
```json
{
  "message": "JSON data stored under key: user:1",
  "elapsed_time": 0.00234,
  "json_data": null
}
```

**Error Response (503 Service Unavailable):**
```json
{
  "detail": "Redis service unavailable"
}
```

### Retrieve All JSON Data

```
GET /redis/retrieve_json
```

**Request:**
```bash
curl http://127.0.0.1:8000/redis/retrieve_json
```

**Response (200 OK):**
```json
{
  "message": "All JSON data retrieved",
  "elapsed_time": 0.00156,
  "json_data": [
    {
      "key": "user:1",
      "json_data": "{\"name\": \"John\", \"age\": 30}"
    },
    {
      "key": "user:2",
      "json_data": "{\"name\": \"Jane\", \"age\": 28}"
    }
  ]
}
```

**Empty Response:**
```json
{
  "message": "No data found",
  "elapsed_time": 0.00089,
  "json_data": null
}
```

## 🔌 Connection Management

### RedisConnector Class

```python
from Redis_services.redis_connectors import RedisConnector

# Initialize connector
redis_connector = RedisConnector()

# Store data
await redis_connector.store_json("user:1", '{"name": "John"}')

# Retrieve data
data = await redis_connector.retrieve_json_all()
```

### Connection Pooling

The connector automatically uses connection pooling:

```python
pool = redis.ConnectionPool(
    host=self.host,
    port=self.port,
    db=self.db,
    max_connections=5  # Maximum 5 concurrent connections
)
self.connection = redis.Redis(connection_pool=pool)
```

**Benefits:**
- Reuses connections instead of creating new ones
- Limits resource consumption
- Improves performance for multiple operations

### Error Handling

The connector handles connection errors gracefully:

```python
try:
    await self.connection.set(key, json_data)
except redis.exceptions.ConnectionError as exc:
    print(f"Redis connection failed: {exc}")
    raise
```

## 📊 Data Models

### RedisJsonStructure (Input)

```python
class RedisJsonStructure(BaseModel):
    key: str              # Redis key identifier
    json_data: str        # JSON string (not parsed as JSON)
```

### RedisResponse (Output)

```python
class RedisResponse(BaseModel):
    message: str          # Status message
    elapsed_time: float   # Operation time in seconds
    json_data: list[RedisJsonStructure] | None  # Retrieved data
```

## ⏱️ Performance Monitoring

Both endpoints measure and return operation time:

```python
start_time = time.time()
# ... perform operation ...
elapsed_time = time.time() - start_time

return RedisResponse(
    message="...",
    elapsed_time=elapsed_time
)
```

**Use this to:**
- Benchmark Redis vs MySQL performance
- Identify bottlenecks
- Monitor system health
- Track performance trends

## 🚀 Best Practices

### 1. Key Naming Conventions

Use hierarchical naming for keys:
```
user:1234                 # User object
user:1234:profile         # User profile
session:abc123def         # Session data
cache:products:123        # Product cache
```

**Benefits:**
- Easier to organize data
- Simpler pattern matching with SCAN
- Better for namespacing

### 2. JSON Storage Strategy

Store JSON as strings (not native Redis JSON):
```python
import json

# Store
json_str = json.dumps({"name": "John", "age": 30})
await redis.set("user:1", json_str)

# Retrieve and parse
data = await redis.get("user:1")
parsed = json.loads(data.decode('utf-8'))
```

### 3. Connection Management

- Reuse RedisConnector instance across requests
- Implement singleton pattern for production
- Use connection pooling (already implemented)

### 4. Error Handling

Always handle Redis failures gracefully:
```python
try:
    await redis_connector.store_json(key, data)
except RedisError as exc:
    raise HTTPException(
        status_code=503,
        detail="Redis service unavailable"
    )
```

### 5. Data Expiration

Set expiration times to prevent memory bloat:
```python
# Expire after 1 hour (3600 seconds)
await redis.setex(key, 3600, json_data)
```

### 6. Monitoring & Debugging

```bash
# Connect to Redis CLI
redis-cli

# Check server info
INFO

# View keys
KEYS *

# Check memory usage
INFO memory

# Monitor commands
MONITOR
```

## 📈 Redis Data Types

While this module uses strings, Redis supports:

- **Strings**: Text and binary data
- **Lists**: Ordered collections
- **Sets**: Unordered unique collections
- **Hashes**: Key-value pairs
- **Sorted Sets**: Scored ordered collections
- **Streams**: Time-series data
- **Geospatial**: Geographic data
- **Bitmaps**: Bit operations
- **HyperLogLog**: Cardinality estimation

**For this project:**
- We use **Strings** for JSON data storage
- Simple key-value retrieval pattern

## 🔍 Debugging & Troubleshooting

### Redis Connection Issues

**Problem:** `ConnectionError: Error 111 connecting to 127.0.0.1:6379`

**Solutions:**
1. Verify Redis is running: `redis-cli ping`
2. Check host/port in `.env`
3. Check firewall rules
4. Verify Redis listens on the configured port:
   ```bash
   netstat -an | grep 6379  # Windows: netstat -ano
   ```

### Out of Memory

**Problem:** Redis eviction or memory full errors

**Solutions:**
1. Set max memory limit in redis.conf:
   ```
   maxmemory 256mb
   maxmemory-policy allkeys-lru
   ```
2. Implement TTL (expiration) on keys
3. Monitor memory usage:
   ```bash
   redis-cli INFO memory
   ```

### Slow Operations

**Problem:** Slow store/retrieve operations

**Solutions:**
1. Check network latency
2. Increase connection pool size:
   ```python
   max_connections = 10  # Increase from 5
   ```
3. Monitor with `MONITOR` command
4. Profile with `redis-benchmark`

### Connection Pool Exhaustion

**Problem:** Too many connections, new requests fail

**Solutions:**
1. Increase pool size cautiously
2. Reduce number of concurrent requests
3. Implement request queuing
4. Monitor pool utilization

## 🎯 Comparison: Redis vs MySQL

### Redis Advantages
- ✅ Extremely fast (sub-millisecond)
- ✅ Simple key-value model
- ✅ Atomic operations
- ✅ Perfect for caching

### Redis Disadvantages
- ❌ In-memory (data loss on crash)
- ❌ Limited query flexibility
- ❌ No complex transactions
- ❌ Requires monitoring

### MySQL Advantages
- ✅ Persistent storage
- ✅ Complex queries (SQL)
- ✅ ACID transactions
- ✅ Mature and stable

### MySQL Disadvantages
- ❌ Slower than Redis
- ❌ More overhead
- ❌ Complex for simple lookups
- ❌ Scaling is harder

## 📚 Example Workflow

```bash
# 1. Start Redis
redis-server

# 2. Start FastAPI application
python main.py

# 3. Store some data
curl -X POST http://127.0.0.1:8000/redis/store_json \
  -H "Content-Type: application/json" \
  -d '{"key": "user:1", "json_data": "{\"name\": \"Alice\"}"}'

curl -X POST http://127.0.0.1:8000/redis/store_json \
  -H "Content-Type: application/json" \
  -d '{"key": "user:2", "json_data": "{\"name\": \"Bob\"}"}'

# 4. Retrieve all data
curl http://127.0.0.1:8000/redis/retrieve_json

# 5. Check in Redis CLI
redis-cli
> SELECT 1
> KEYS *
> GET user:1
> FLUSHDB  # Clear database if needed
```

## 🔗 External Resources

- [Redis Documentation](https://redis.io/documentation)
- [Redis Commands](https://redis.io/commands/)
- [redis-py Client](https://redis-py.readthedocs.io/)
- [Redis CLI](https://redis.io/docs/manual/cli/)
- [Redis Best Practices](https://redis.io/docs/management/optimization/)

## 📞 Support

For issues:
1. Verify Redis is running: `redis-cli ping`
2. Check `.env` configuration
3. Review connection pool settings
4. Check Redis logs
5. Consult Redis documentation
