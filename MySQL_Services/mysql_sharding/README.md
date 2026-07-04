# MySQL Database Sharding

This module demonstrates **Database Sharding**, a horizontal partitioning technique that distributes data across multiple databases to achieve scalability for very large datasets and high write throughput.

## 📋 Overview

Database Sharding allows you to:
- Scale beyond single database capacity limits
- Distribute write load across multiple servers
- Partition data logically based on shard keys
- Maintain independent shard availability
- Enable unlimited horizontal growth

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│     Application Layer               │
│  (Shard Key: First Letter of Name)  │
└────────┬────────────────────────────┘
         │
    ┌────┴─────────┐
    │ Shard Routing│
    │ Logic (A-M)  │
    │ Logic (N-Z)  │
    └────┬─────────┘
    ┌────▼──────────┐      ┌──────────────┐
    │   Shard 1     │      │   Shard 2    │
    │  (Database 1) │      │ (Database 2) │
    │   Names A-M   │      │   Names N-Z  │
    └───────────────┘      └──────────────┘
```

## 📁 Module Files

### `mysql_shard.py`

Implements sharding logic with shard routing:

- **Purpose**: Distribute data across shards based on shard key
- **Shard Key**: First letter of the name field
- **Routing Strategy**: Range-based
  - Names A-M → Shard 1
  - Names N-Z → Shard 2
- **Endpoint**: `POST /sharding/add_shard`

**Data Model:**
```python
class Shard(BaseModel):
    name: str
    nickname: str = None
```

## 🔧 Sharding Strategy

### Shard Key Selection

The current implementation uses **range-based sharding** on the first letter of names:

```
Shard 1 (3306): A, B, C, D, E, F, G, H, I, J, K, L, M
Shard 2 (3307): N, O, P, Q, R, S, T, U, V, W, X, Y, Z
```

### How It Works

```python
# Extract first letter and map to shard
first = shard.name.strip()[0].lower()

if "a" <= first <= "m":
    # Insert into Shard 1
    cursor = shard_db1.cursor()
    cursor.execute(
        "INSERT INTO sharded_names (name, nickname) VALUES (%s, %s)",
        (shard.name, shard.nickname)
    )
else:  # "n" <= first <= "z"
    # Insert into Shard 2
    cursor = shard_db2.cursor()
    cursor.execute(
        "INSERT INTO sharded_names (name, nickname) VALUES (%s, %s)",
        (shard.name, shard.nickname)
    )
```

## 📊 Setup & Configuration

### 1. Create Shard Databases

**On Shard 1 (Port 3306):**
```sql
CREATE DATABASE shard1;
USE shard1;

CREATE TABLE sharded_names (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    nickname VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_name (name)
);
```

**On Shard 2 (Port 3307):**
```sql
CREATE DATABASE shard2;
USE shard2;

CREATE TABLE sharded_names (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    nickname VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_name (name)
);
```

### 2. Environment Configuration

```env
MYSQL_HOST=localhost              # Shard 1 host
MYSQL_USER=root                  # Database user
MYSQL_PASSWORD=your_password     # Database password
MYSQL_REPLICA_HOST=localhost     # Shard 2 host
```

### 3. Connection Initialization

The module automatically establishes connections to both shards:

```python
shard_db1 = connect_to_database(
    os.environ["MYSQL_HOST"],
    os.environ["MYSQL_USER"],
    os.environ["MYSQL_PASSWORD"],
    3306,
    database="shard1"
)

shard_db2 = connect_to_database(
    os.environ["MYSQL_REPLICA_HOST"],
    os.environ["MYSQL_USER"],
    os.environ["MYSQL_PASSWORD"],
    3307,
    database="shard2"
)
```

## 🌐 API Endpoints

### Add Data to Shard

```
POST /sharding/add_shard
```

**Request:**
```bash
curl -X POST http://127.0.0.1:8000/sharding/add_shard \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alice",
    "nickname": "Ali"
  }'
```

**Response:**
```json
{
  "message": "Data added to shard 1"
}
```

**Examples:**

Names starting with A-M go to Shard 1:
- Alice → Shard 1
- Bob → Shard 1
- Charlie → Shard 1

Names starting with N-Z go to Shard 2:
- Nancy → Shard 2
- Zoe → Shard 2
- Tom → Shard 2

## 📈 Sharding Benefits

### Scalability
- **Horizontal Growth**: Add more shards to increase capacity
- **Write Throughput**: Distribute writes across shards
- **Storage**: Each shard holds a subset of data

### Performance
- **Query Performance**: Smaller datasets per shard = faster queries
- **Index Efficiency**: More efficient B-tree indexes
- **Parallel Processing**: Process multiple shards concurrently

### Cost
- **Commodity Hardware**: Use smaller database servers
- **Efficient Utilization**: Balance load across shards

## ⚠️ Sharding Challenges

### Increased Complexity
- Application must be shard-aware
- Debugging distributed queries is harder
- Testing across multiple shards required

### Cross-Shard Operations
- Joining data from multiple shards is expensive
- Aggregations across shards require application logic
- Transactions spanning shards are difficult

### Shard Rebalancing
- Adding new shards requires data migration
- Consistent hashing can minimize redistribution
- Downtime may be required during rebalancing

### Hotspots
- Uneven data distribution (some names more common)
- Load imbalance between shards
- May require dynamic rebalancing

## 🚀 Best Practices

### 1. Shard Key Selection

**Good Shard Keys:**
- Relatively uniform distribution
- Rarely changed (immutable preferred)
- Small and numeric (faster routing)
- Used in most queries

**Poor Shard Keys:**
- User ID if distribution is skewed
- Timestamp (causes hotspots)
- Frequently changing values

### 2. Shard Sizing

```python
# Monitor shard sizes
def check_shard_balance(shard_db1, shard_db2):
    cursor1 = shard_db1.cursor()
    cursor1.execute("SELECT COUNT(*) as count FROM sharded_names")
    count1 = cursor1.fetchone()[0]
    
    cursor2 = shard_db2.cursor()
    cursor2.execute("SELECT COUNT(*) as count FROM sharded_names")
    count2 = cursor2.fetchone()[0]
    
    return {
        'shard1_count': count1,
        'shard2_count': count2,
        'balance_ratio': max(count1, count2) / min(count1, count2)
    }
```

### 3. Connection Management

- Use connection pooling for each shard
- Maintain separate connection pools per shard
- Implement exponential backoff for failures

### 4. Query Patterns

**Single Shard Queries (Fast):**
```python
# Extract shard from data
first = name[0].lower()
if "a" <= first <= "m":
    result = query_shard1(name)
else:
    result = query_shard2(name)
```

**Multi-Shard Queries (Slow):**
```python
# Query all shards and merge results
results = []
results.extend(query_shard1(criteria))
results.extend(query_shard2(criteria))
return aggregate(results)
```

### 5. Monitoring & Alerts

```python
# Monitor shard imbalance
balance = check_shard_balance(shard_db1, shard_db2)
if balance['balance_ratio'] > 2.0:
    # Alert: shards are unbalanced
    trigger_alert("Shard imbalance detected")
```

## 🔍 Common Sharding Strategies

### 1. Range-Based (Current Implementation)
```
A-M → Shard 1
N-Z → Shard 2
```
**Pros:** Simple to implement
**Cons:** Can cause hotspots

### 2. Hash-Based
```
hash(name) % num_shards → Shard number
```
**Pros:** Better distribution
**Cons:** Rebalancing is harder

### 3. Directory-Based
```
Lookup table: name_prefix → shard_id
```
**Pros:** Flexible, supports rebalancing
**Cons:** Extra lookup overhead

### 4. Geographic-Based
```
US → Shard 1
Europe → Shard 2
Asia → Shard 3
```
**Pros:** Reduces latency
**Cons:** Can be unbalanced

## 📊 Example Operations

### Add Multiple Records

```bash
# Shard 1 candidates
curl -X POST http://127.0.0.1:8000/sharding/add_shard \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "nickname": "Ali"}'

curl -X POST http://127.0.0.1:8000/sharding/add_shard \
  -H "Content-Type: application/json" \
  -d '{"name": "Bob", "nickname": "Bobby"}'

curl -X POST http://127.0.0.1:8000/sharding/add_shard \
  -H "Content-Type: application/json" \
  -d '{"name": "Charlie", "nickname": "Chuck"}'

# Shard 2 candidates
curl -X POST http://127.0.0.1:8000/sharding/add_shard \
  -H "Content-Type: application/json" \
  -d '{"name": "Nancy", "nickname": "Nan"}'

curl -X POST http://127.0.0.1:8000/sharding/add_shard \
  -H "Content-Type: application/json" \
  -d '{"name": "Zoe", "nickname": "Z"}'
```

### Verify Distribution

```sql
-- Check Shard 1
USE shard1;
SELECT name, nickname FROM sharded_names;
-- Results: Alice, Bob, Charlie, ...

-- Check Shard 2
USE shard2;
SELECT name, nickname FROM sharded_names;
-- Results: Nancy, Zoe, Tom, ...
```

## 🔄 Handling Shard Growth

### Adding a New Shard

**Scenario:** Current 2-shard setup is overloaded

**Steps:**
1. Create Shard 3 database
2. Plan data redistribution
3. Migrate appropriate data
4. Update routing logic
5. Update application configuration
6. Verify all shards are balanced

**New Distribution Example:**
```
A-I   → Shard 1
J-R   → Shard 2
S-Z   → Shard 3
```

## ⚠️ Error Handling

The module includes validation for shard keys:

```python
if not shard.name or not shard.name.strip():
    return {"message": "Invalid shard name. Must be a non-empty string."}

first = shard.name.strip()[0].lower()
if not ("a" <= first <= "z"):
    return {"message": "Invalid name. Must start with a letter."}
```

## 📚 Related Documentation

- [Parent README](../README.md) - Overall MySQL Replication & Sharding guide
- [MySQL Replica Guide](../mysql_replica/README.md) - Replication details
- [Utils](../utils.py) - Connection utilities

## 🔗 External Resources

- [MySQL Sharding Patterns](https://dev.mysql.com/doc/mysql-shell/8.0/en/mysql-innodb-cluster.html)
- [Consistent Hashing](https://en.wikipedia.org/wiki/Consistent_hashing)
- [Vitess (MySQL Sharding Platform)](https://vitess.io/)
- [Citus (PostgreSQL Extension)](https://www.citusdata.com/)

## 📞 Support

For issues or questions:
1. Verify shard key distribution
2. Check connection strings to both shards
3. Monitor shard imbalance metrics
4. Review MySQL error logs on each shard
5. Consult MySQL documentation
