# Async MariaDB Python Connector

[![PyPI version](https://img.shields.io/pypi/v/async-mariadb-connector.svg)](https://pypi.org/project/async-mariadb-connector/)
[![Python Version](https://img.shields.io/pypi/pyversions/async-mariadb-connector.svg)](https://pypi.org/project/async-mariadb-connector/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://github.com/chanikkyasaai/async-mariadb-ml/actions/workflows/ci.yml/badge.svg)](https://github.com/chanikkyasaai/async-mariadb-ml/actions)
[![Downloads](https://img.shields.io/pypi/dm/async-mariadb-connector.svg)](https://pypi.org/project/async-mariadb-connector/)

A lightweight, production-grade, and asynchronous Python connector for MariaDB, designed for high-performance data operations in modern AI/ML and web applications.

---

## The Problem: MariaDB's Python Ecosystem Has a Performance Bottleneck

MariaDB is a powerful and reliable database, but the official Python connector (`mariadb`) operates **synchronously**. This means your application blocks and waits for every single query to finish, creating a massive performance bottleneck in modern, I/O-bound applications.

This is especially problematic for:

-   **AI/ML Pipelines:** Loading large datasets for training or performing bulk embedding inserts for RAG systems becomes slow and inefficient.
-   **Web APIs:** High-traffic web servers struggle to handle concurrent requests when each database call is a blocking operation.
-   **Data Processing:** Any workflow requiring many simultaneous database interactions is severely limited.

## The Solution: A High-Level, Production-Ready Async Connector

This project, `async-mariadb-connector`, was built to solve this exact problem. It provides a high-level, asynchronous interface to MariaDB that is not only fast but also robust and easy to use.

While low-level async drivers like `aiomysql` exist, they lack the "batteries-included" features required for production environments. This library bridges that gap.

### How Well Is It Built?

This is not just a simple wrapper. It is a complete, production-grade library with features designed for real-world use:

-   **Truly Asynchronous:** Built on `asyncio` to eliminate I/O blocking and enable massive concurrency.
-   **Automatic Connection Pooling:** Efficiently manages database connections for optimal performance, right out of the box.
-   **Resilient by Design:** Features automatic connection retries with exponential backoff, so your application can survive transient database or network issues.
-   **Seamless Pandas Integration:** Includes high-performance `bulk_insert` for DataFrames and `fetch_all_df` to move data effortlessly between your database and your data science tools.
-   **Memory-Efficient Streaming:** A `fetch_stream` method allows you to process huge datasets row-by-row, without risking memory overloads.
-   **Professionally Tested:** Comes with a comprehensive test suite (17 tests) ensuring reliability and correctness.

### See the Performance for Yourself

Don't just take our word for it. The performance gains are measurable and significant.

**Check out the detailed results in our [Benchmarks](https://github.com/chanikkyasaai/async-mariadb-ml/blob/main/docs/BENCHMARKS.md) to see how this connector is ~30% faster on concurrent read operations.**

## Strong MariaDB Integration

This library is specifically designed and tested for MariaDB:

- **Tested Against:** MariaDB 11.8.3
- **Full Type Support:** JSON, DECIMAL, utf8mb4 (emojis), TIMESTAMP, TEXT/LONGTEXT
- **Optimized For:** Connection pooling, strict SQL mode, InnoDB transactions
- **Docker Ready:** One-command setup with `docker-compose up`

For detailed MariaDB-specific features, configurations, and best practices, see [MariaDB Integration Notes](https://github.com/chanikkyasaai/async-mariadb-ml/blob/main/docs/MARIADB_NOTES.md).

## Future-Ready for AI and Modern Applications

This connector is designed for the future of data engineering and AI. The combination of non-blocking I/O, efficient bulk operations, and direct DataFrame integration makes it the ideal choice for:

-   **Building high-performance RAG pipelines** with vector embeddings stored in MariaDB.
-   **Creating fast, scalable data APIs** for web and mobile applications.
-   **Powering ETL and data processing workflows** that require high concurrency.

## Installation

```bash
pip install async-mariadb-connector
```

The package is now available on PyPI: https://pypi.org/project/async-mariadb-connector/

## Quick Start

First, spin up MariaDB with docker-compose:

```bash
docker-compose up -d
```

Then set up your `.env` file (copy from `.env.example`):

```ini
# .env
DB_HOST=127.0.0.1
DB_PORT=3307
DB_USER=root
DB_PASSWORD=root
DB_NAME=test_db
```

Now, you can connect and run queries asynchronously:

```python
import asyncio
import pandas as pd
from async_mariadb_connector import AsyncMariaDB

async def main():
    db = AsyncMariaDB()

    try:
        # Fetch all users into a DataFrame
        all_users_df = await db.fetch_all_df("SELECT * FROM users")
        print("All users:")
        print(all_users_df)

    finally:
        await db.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## Connect with the Author

This project was created by **Chanikya Nelapatla**.

-   **LinkedIn:** [https://www.linkedin.com/in/chanikkyasaai/](https://www.linkedin.com/in/chanikkyasaai/)
-   **GitHub:** [https://github.com/chanikkyasaai](https://github.com/chanikkyasaai)

## License

This project is licensed under the MIT License.
