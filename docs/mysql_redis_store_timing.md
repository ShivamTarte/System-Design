# MySQL and Redis JSON Storage Timing

This document describes the JSON storage APIs implemented in the `System-Design` repository and shows example request/response payloads with observed elapsed times.

## MySQL JSON Storage

### Endpoint
`POST /mysql_connectors/store_json`

### Request Body
```json
{
  "name": "Daniel Miller",
  "age": 27,
  "email": "daniel.miller@example.com",
  "job": "QA Engineer"
}
```

### Behavior
- The endpoint validates incoming JSON using a `JsonStructure` Pydantic model.
- Expected fields are:
  - `name` (string)
  - `age` (integer, optional)
  - `email` (string, optional)
  - `job` (string, optional)
- After validation, the payload is inserted into the MySQL table `json_data`.
- The response includes the total elapsed time for the operation.

### Example Response
```json
{
  "message": "JSON data stored successfully!",
  "elapsed_time": 0.07104730606079102,
  "json_data": null
}
```

### Notes
- `elapsed_time` is the duration measured from request start until the insert completes.
- `json_data` is `null` because this endpoint only stores data and does not return the inserted record.

## Redis JSON Storage

### Endpoint
`POST /redis/store_json`

### Request Body
```json
{
  "key": "user:7",
  "json_data": "{\"name\":\"Daniel Miller\",\"age\":27,\"email\":\"daniel.miller@example.com\",\"job\":\"QA Engineer\"}"
}
```

### Behavior
- The endpoint validates the payload using a `RedisJsonStructure` Pydantic model.
- Expected fields are:
  - `key` (string)
  - `json_data` (string containing JSON)
- The Redis connector stores the raw JSON string at the specified key.
- The response includes the elapsed time for the set operation.

### Example Response
```json
{
  "message": "JSON data stored under key: user:7",
  "elapsed_time": 0.006754398345947266,
  "json_data": null
}
```

### Notes
- `elapsed_time` represents the time taken to execute the Redis store call.
- `json_data` is `null` in the response because the endpoint only performs storage.

## Performance Summary

### Storage Operations
- The MySQL store call shows higher latency (~0.07 seconds) because it involves a relational database insert, query planning, and durability guarantees.
- The Redis store call is much faster (~0.007 seconds) because Redis is an in-memory key-value store optimized for low-latency writes.

### Retrieval Operations
- MySQL retrieval: `0.0328676700592041` seconds
- Redis retrieval: `0.020152807235717773` seconds
- Redis retrieval is approximately **40% faster** than MySQL retrieval in this benchmark.

### General Insights
- For workloads that require quick lookup and simple JSON storage, Redis is usually faster.
- MySQL is better suited for structured storage, relational queries, and persistence guarantees.
- The performance advantage of Redis grows as data retrieval complexity increases.

## Database Overview

### MySQL
- A relational database management system (RDBMS).
- Stores structured data in tables and supports SQL queries, joins, transactions, and schema enforcement.
- Best for applications that require persistent storage, strong consistency, and complex querying across related records.

### Redis
- An in-memory key-value store.
- Optimized for fast read/write operations and low latency.
- Best for caching, session storage, counters, and simple JSON or string storage when speed is critical.

## Redis Optimization Recommendations

To further improve Redis retrieval performance, consider the following optimizations:

### Avoid Key Scanning
- **Problem**: The current implementation uses `KEYS '*'` which scans the entire keyspace and is expensive for large datasets.
- **Solution**: Retrieve data by specific known keys using `GET` instead of scanning all keys.

### Reduce Round Trips
- Use Redis **pipelining** to batch multiple commands in a single network request.
- Consider `MGET` only when retrieving a small, predefined set of keys.

### Minimize Data Size
- Keep JSON payloads as compact as possible to reduce network transfer time.
- Avoid storing unnecessary fields in Redis.

### Optimize Decoding
- Minimize Python-level decoding operations in the application.
- Consider storing data in formats that require less post-processing.

### Network Latency
- Ensure the Redis server is running locally or has low network latency.
- High latency to the Redis server can dominate overall operation time.

### Connection Pooling
- The current implementation already uses connection pooling (`max_connections=5`), which is good practice.
- Monitor pool saturation to ensure connections are not becoming a bottleneck.

## Storage Operation Optimization Recommendations

### MySQL Store Optimization

**Current Performance**: ~0.071 seconds per insert

#### Identified Bottlenecks
- **Network Round Trip**: Waiting for the MySQL server to acknowledge and process the INSERT.
- **Durability Overhead**: `db.commit()` ensures data is persisted to disk, adding latency.
- **Connection Overhead**: Opening and closing cursors for each request.

#### Recommendations
1. **Use Connection Pooling**
   - The current implementation uses `Depends(get_db)`, which creates a new connection per request.
   - Implement persistent connection pooling (e.g., `pymysql-pool` or `SQLAlchemy` with connection pool).
   - Reuse connections across multiple requests to eliminate connection setup time.

2. **Batch Insertions**
   - If inserting multiple records, use batch inserts: `INSERT INTO json_data VALUES (...), (...), (...)`
   - This reduces round trips and commit overhead significantly.

3. **Optimize Indexes**
   - Ensure the table has appropriate indexes on commonly queried columns.
   - Avoid overly broad indexes that slow down inserts.

4. **Consider Asynchronous Writes** (if durability can be slightly relaxed)
   - Use MySQL's `autocommit` with caution or implement write-ahead logging patterns.
   - Trade off immediate durability for higher throughput if applicable.

5. **Monitor Query Execution**
   - Use `EXPLAIN` to analyze the insert query plan.
   - Watch for slow query logs to identify bottlenecks.

### Redis Store Optimization

**Current Performance**: ~0.007 seconds per set

#### Identified Advantages
- **In-Memory Operations**: No disk I/O required.
- **Simple Protocol**: Redis uses a simple text protocol (RESP) requiring minimal parsing.

#### Recommendations for Further Improvement
1. **Avoid Extra Validation**
   - The current implementation performs full Pydantic validation before storing.
   - If the key-value pairs are pre-validated, skip redundant checks.

2. **Use Pipelining for Bulk Operations**
   - When storing multiple key-value pairs, use Redis pipelining to batch commands.
   - Example: Send multiple `SET` commands in one request instead of separate round trips.

3. **Optimize Key Naming**
   - Use shorter, meaningful key names to reduce memory usage.
   - Example: `u:7` instead of `user:7` (saves 2 bytes per key).

4. **Consider TTL (Time-To-Live)**
   - If data should expire, set a TTL to enable automatic cleanup: `SET key value EX 3600`
   - Prevents unbounded memory growth in the Redis server.

5. **Enable Redis Persistence Only When Needed**
   - If persistence is not required, disable RDB snapshots and AOF to reduce overhead.
   - If durability is needed, configure AOF with `appendfsync everysec` instead of `always`.

6. **Monitor Memory Usage**
   - Use `INFO memory` command to track Redis memory consumption.
   - Set appropriate `maxmemory` policies to handle eviction gracefully.

### Comparative Insights for Storage

| Aspect | MySQL | Redis |
|--------|-------|-------|
| **Speed** | Slower (~71ms) | Much Faster (~7ms) |
| **Durability** | Guaranteed (commit) | Optional (AOF/RDB) |
| **Scalability** | Good for complex queries | Good for simple key-value |
| **Use Case** | Persistent, relational data | Cache, session, counters |
| **Optimization Focus** | Batch operations, indexing | Pipelining, TTL |

## Validation Requirements

Ensure request payload values match the expected types:
- `name` must be a string
- `age` must be an integer if provided
- `email` must be a string if provided
- `job` must be a string if provided
- `key` must be a string
- `json_data` must be a string containing JSON data

## Usage

1. Start the FastAPI application from `main.py`.
2. Call the MySQL endpoint to persist structured JSON fields into MySQL.
3. Call the Redis endpoint to store serialized JSON under a Redis key.
4. Compare `elapsed_time` values to understand latency differences between MySQL and Redis operations.
