# MySQL Replication and Sharding

This directory contains implementations of two key MySQL scaling patterns: **Master-Slave Replication** and **Sharding**.

## 📋 Overview

MySQL replication and sharding are complementary techniques for scaling databases:

- **Master-Slave Replication**: Creates read replicas to distribute read queries
- **Sharding**: Partitions data horizontally across multiple databases to scale writes and total data capacity

## 📁 Directory Structure

```
MySQL_Replica/
├── utils.py                    # Common database connection utilities
├── mysql_replica/              # Master-slave replication module
│   ├── __init__.py
│   ├── README.md              # Detailed replication documentation
│   ├── master_slave_connectors.py  # Connections to master and replica
│   └── mysql_connectors.py         # Data operations on master/replica
└── mysql_sharding/            # Database sharding module
    ├── __init__.py
    ├── README.md              # Detailed sharding documentation
    └── mysql_shard.py         # Shard routing and data distribution
```

## 🔧 Setup Instructions

### Prerequisites

- MySQL Server 5.7+ or 8.0+
- MySQL Command Line Client or MySQL Workbench
- Python 3.10+

### 1. Create Master Database

```sql
-- Create the main database
CREATE DATABASE compare_redis;
USE compare_redis;

-- Create the json_data table
CREATE TABLE json_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    age INT,
    email VARCHAR(255),
    job VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for better query performance
CREATE INDEX idx_name ON json_data(name);
```

### 2. Configure Master-Slave Replication

#### Enable Binary Logging (Master)

Edit `my.cnf` or `my.ini`:
```ini
[mysqld]
server-id=1
log_bin=mysql-bin
binlog_format=ROW
```

Restart MySQL and verify:
```sql
SHOW MASTER STATUS;
```

#### Configure Replica

Edit replica's `my.cnf`:
```ini
[mysqld]
server-id=2
relay-log=mysql-relay-bin
relay-log-index=mysql-relay-bin.index
```

Create replication user on master:
```sql
CREATE USER 'repl_user'@'replica_host' IDENTIFIED BY 'repl_password';
GRANT REPLICATION SLAVE ON *.* TO 'repl_user'@'replica_host';
FLUSH PRIVILEGES;
```

On replica:
```sql
CHANGE MASTER TO
    MASTER_HOST='master_host',
    MASTER_USER='repl_user',
    MASTER_PASSWORD='repl_password',
    MASTER_LOG_FILE='mysql-bin.000001',
    MASTER_LOG_POS=0;

START SLAVE;
SHOW SLAVE STATUS;
```

### 3. Configure Sharding

Create shard databases:

```sql
-- On Shard 1
CREATE DATABASE shard1;
USE shard1;
CREATE TABLE sharded_names (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    nickname VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- On Shard 2
CREATE DATABASE shard2;
USE shard2;
CREATE TABLE sharded_names (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    nickname VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## ⚙️ Configuration

### Environment Variables (.env)

```env
# Master Database
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_PORT=3306

# Replica Database
MYSQL_REPLICA_HOST=localhost
MYSQL_REPLICA_PORT=3307

# Database Names
MASTER_DB=compare_redis
SHARD1_DB=shard1
SHARD2_DB=shard2
```

## 📊 Key Features

### Master-Slave Replication

- **Write Operations**: Directed to master
- **Read Operations**: Can be directed to replicas
- **Automatic Synchronization**: Changes replicate automatically
- **Read Scaling**: Distribute read load across multiple replicas
- **High Availability**: Replica can be promoted to master if needed

**Use Cases:**
- Read-heavy applications
- Reporting and analytics (read replica)
- Backup and disaster recovery

### Sharding

- **Data Partitioning**: Data split across multiple databases
- **Horizontal Scaling**: Add more shards to increase capacity
- **Shard Key**: Determines which shard stores data
- **Range-based Sharding**: Names A-M → Shard 1, N-Z → Shard 2
- **Load Distribution**: Even distribution of data and queries

**Use Cases:**
- Very large datasets (multi-terabyte)
- High write throughput requirements
- Geographic distribution

## 🔌 Connection Management

### Using `utils.py`

```python
from MySQL_Replica.utils import connect_to_database
import os

# Create a connection
db = connect_to_database(
    host=os.environ["MYSQL_HOST"],
    user=os.environ["MYSQL_USER"],
    passwd=os.environ["MYSQL_PASSWORD"],
    port=3306,
    database="compare_redis"
)

# Use the connection
cursor = db.cursor()
cursor.execute("SELECT * FROM json_data")
results = cursor.fetchall()

# Close connection
db.close()
```

## 🌐 API Endpoints

### Replication Endpoints

```
GET /read_replicas/connect_master
- Test connectivity to master database
- Response: {"message": "Successfully connected to the master database!"}

GET /read_replicas/connect_replica
- Test connectivity to replica database
- Response: {"message": "Successfully connected to the replica database!"}
```

### MySQL Connector Endpoints

```
POST /mysql_connectors/store_json
- Store JSON data in master database
- Request: {"name": "John", "age": 30, "email": "john@example.com", "job": "Engineer"}
- Response: {"message": "...", "elapsed_time": 0.001234, "json_data": [...]}

GET /mysql_connectors/retrieve_json
- Retrieve JSON data from master database
- Response: {"message": "...", "elapsed_time": 0.001234, "json_data": [...]}
```

### Sharding Endpoints

```
POST /sharding/add_shard
- Add data to appropriate shard based on shard key
- Request: {"name": "Alice", "nickname": "Ali"}
- Response: {"message": "Data added to shard"}
```

## 📈 Performance Considerations

### Master-Slave Replication

**Advantages:**
- Read scalability
- Minimal latency for reads
- Simple to set up

**Disadvantages:**
- Eventual consistency (replication lag)
- Increased storage (data duplicated)
- Master becomes write bottleneck

**Metrics to Monitor:**
- Replication lag
- Master QPS
- Network bandwidth between master/replica

### Sharding

**Advantages:**
- Horizontal write scalability
- Distributed query load
- Unlimited data capacity

**Disadvantages:**
- Increased application complexity
- Cross-shard queries are expensive
- Data redistribution is complex

**Metrics to Monitor:**
- Shard balancing (data distribution)
- Cross-shard query frequency
- Individual shard load

## 🔍 Monitoring

### Check Replication Status

```sql
-- On Master
SHOW MASTER STATUS;

-- On Replica
SHOW SLAVE STATUS\G
```

Key fields:
- `Seconds_Behind_Master`: Replication lag
- `Slave_IO_Running`: IO thread status
- `Slave_SQL_Running`: SQL thread status

## 🚀 Best Practices

1. **Always test replication setup** before production
2. **Monitor replication lag** actively
3. **Use connection pooling** for efficient resource usage
4. **Implement proper error handling** for database operations
5. **Back up regularly** before and after schema changes
6. **Document your sharding strategy** for team reference
7. **Use consistent shard keys** across operations
8. **Plan capacity** for shard growth

## 📚 Further Reading

- [MySQL Replication Documentation](https://dev.mysql.com/doc/refman/8.0/en/replication.html)
- [MySQL Sharding Strategies](https://dev.mysql.com/doc/mysql-shell/8.0/en/mysql-innodb-cluster.html)
- [Master-Slave Connectors](./mysql_replica/README.md)
- [Sharding Details](./mysql_sharding/README.md)

## 🐛 Troubleshooting

### Replication Not Syncing

```sql
-- Check replica status
SHOW SLAVE STATUS\G

-- If stuck, reset and reconfigure
STOP SLAVE;
RESET SLAVE;
-- Reconfigure using CHANGE MASTER TO
```

### Connection Refused

- Verify MySQL is running: `mysql -h localhost -u root -p`
- Check firewall rules
- Verify credentials in `.env` file

### Shard Imbalance

- Monitor shard sizes regularly
- Implement rebalancing if needed
- Document your shard key strategy

## 📞 Support

For issues with MySQL replication and sharding setup, refer to:
- [MySQL Official Documentation](https://dev.mysql.com/doc/)
- Project README
- Individual module READMEs
