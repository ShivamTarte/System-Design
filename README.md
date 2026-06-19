# System Design Project

A comprehensive system design implementation demonstrating key concepts and patterns for building scalable, distributed systems. This project implements MySQL Master-Slave Replication, MySQL Sharding, and Redis caching patterns with FastAPI.

## 📋 Overview

This project serves as a practical demonstration of critical system design patterns used in production environments:

- **MySQL Master-Slave Replication**: Read replicas for distributing read queries
- **MySQL Sharding**: Horizontal data partitioning for scalability
- **Redis Caching**: High-performance in-memory data storage and retrieval
- **FastAPI Integration**: RESTful API endpoints for all services

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- MySQL Server (Master and Replica instances)
- Redis Server
- pip or uv package manager

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd System-Design
```

2. Install dependencies:
```bash
pip install -r requirements.txt
# OR
uv sync
```

3. Configure environment variables:

Create a `.env` file in the root directory:
```
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_REPLICA_HOST=localhost
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_DB=1
```

4. Run the application:
```bash
python main.py
# OR
uv run main.py
```

The FastAPI server will start at `http://127.0.0.1:8000`

## 📁 Project Structure

```
System-Design/
├── main.py                          # FastAPI application entry point
├── pyproject.toml                   # Project dependencies and metadata
├── README.md                        # This file
├── MySQL_Replica/                  # MySQL replication and sharding
│   ├── README.md                   # MySQL setup and configuration guide
│   ├── utils.py                    # Database connection utilities
│   ├── mysql_replica/              # Master-slave replication module
│   │   ├── __init__.py
│   │   ├── README.md               # Replication documentation
│   │   ├── master_slave_connectors.py
│   │   └── mysql_connectors.py
│   └── mysql_sharding/             # Sharding module
│       ├── __init__.py
│       ├── README.md               # Sharding documentation
│       └── mysql_shard.py
├── Redis_services/                 # Redis caching and storage
│   ├── README.md                   # Redis setup and usage
│   ├── redis_connectors.py         # Redis connection management
│   └── redis_routes.py             # Redis API endpoints
└── docs/                           # Documentation
    └── mysql_redis_store_timing.md # Performance timing documentation
```

## 🔧 Core Components

### MySQL Replication
Demonstrates master-slave replication for read scaling:
- Writes go to the master database
- Reads are distributed across replicas
- Automatic synchronization of data

[Learn more](./MySQL_Replica/README.md)

### MySQL Sharding
Implements horizontal partitioning of data:
- Data distribution based on shard keys
- Parallel query processing across shards
- Improved throughput and latency

[Learn more](./MySQL_Replica/mysql_sharding/README.md)

### Redis Services
Provides high-performance caching:
- Async data storage and retrieval
- JSON data support
- Connection pooling for efficiency

[Learn more](./Redis_services/README.md)

## 🌐 API Endpoints

### MySQL Replication
- `GET /read_replicas/connect_master` - Test master connection
- `GET /read_replicas/connect_replica` - Test replica connection

### MySQL Operations
- `POST /mysql_connectors/store_json` - Store JSON data with timing
- `GET /mysql_connectors/retrieve_json` - Retrieve JSON data

### MySQL Sharding
- `POST /sharding/add_shard` - Add data to appropriate shard

### Redis Operations
- `POST /redis/store_json` - Store JSON in Redis with timing
- `GET /redis/retrieve_json` - Retrieve all JSON data from Redis

## 📊 Performance Comparison

The project includes timing measurements comparing:
- MySQL storage and retrieval performance
- Redis storage and retrieval performance
- Master vs Replica latency characteristics

See [Performance Documentation](./docs/mysql_redis_store_timing.md) for detailed analysis.

## 🔐 Configuration

All sensitive configuration (database credentials, hosts, ports) is managed through environment variables in the `.env` file. Never commit credentials to version control.

### Key Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MYSQL_HOST` | Master database host | localhost |
| `MYSQL_USER` | Database user | root |
| `MYSQL_PASSWORD` | Database password | - |
| `MYSQL_REPLICA_HOST` | Replica database host | localhost |
| `REDIS_HOST` | Redis server host | 127.0.0.1 |
| `REDIS_PORT` | Redis server port | 6379 |
| `REDIS_DB` | Redis database number | 1 |

## 📚 Learning Resources

- [MySQL Replication Documentation](./MySQL_Replica/README.md)
- [MySQL Sharding Guide](./MySQL_Replica/mysql_sharding/README.md)
- [Redis Services Guide](./Redis_services/README.md)
- [Master-Slave Connectors](./MySQL_Replica/mysql_replica/README.md)

## 🧪 Testing

To test the endpoints using curl:

```bash
# Test Master Connection
curl http://127.0.0.1:8000/read_replicas/connect_master

# Store JSON in MySQL
curl -X POST http://127.0.0.1:8000/mysql_connectors/store_json \
  -H "Content-Type: application/json" \
  -d '{"name": "John", "age": 30, "email": "john@example.com"}'

# Store JSON in Redis
curl -X POST http://127.0.0.1:8000/redis/store_json \
  -H "Content-Type: application/json" \
  -d '{"key": "user:1", "json_data": "{\"name\": \"John\", \"age\": 30}"}'

# Retrieve from Redis
curl http://127.0.0.1:8000/redis/retrieve_json
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📄 License

This project is open source and available under the MIT License.

## ⚙️ System Requirements

- **MySQL Server**: 5.7+ or 8.0+
- **Redis Server**: 6.0+
- **Python**: 3.10+
- **RAM**: Minimum 2GB (4GB+ recommended)
- **Disk Space**: At least 5GB for database files

## 🐛 Troubleshooting

### MySQL Connection Issues
- Ensure MySQL servers are running on specified hosts and ports
- Verify credentials in `.env` file
- Check firewall rules

### Redis Connection Issues
- Verify Redis server is running
- Check Redis host and port configuration
- Ensure Redis is accessible from the application

### Import Errors
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Ensure the project root is in PYTHONPATH
- Check that all package `__init__.py` files exist

## 📞 Support

For issues, questions, or suggestions, please open an issue on the project repository.
