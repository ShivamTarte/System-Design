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

- The MySQL store call shows higher latency (~0.07 seconds) because it involves a relational database insert, query planning, and durability guarantees.
- The Redis store call is much faster (~0.007 seconds) because Redis is an in-memory key-value store optimized for low-latency writes.
- For workloads that require quick lookup and simple JSON storage, Redis is usually faster, while MySQL is better suited for structured storage, relational queries, and persistence.

## Database Overview

### MySQL
- A relational database management system (RDBMS).
- Stores structured data in tables and supports SQL queries, joins, transactions, and schema enforcement.
- Best for applications that require persistent storage, strong consistency, and complex querying across related records.

### Redis
- An in-memory key-value store.
- Optimized for fast read/write operations and low latency.
- Best for caching, session storage, counters, and simple JSON or string storage when speed is critical.

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
