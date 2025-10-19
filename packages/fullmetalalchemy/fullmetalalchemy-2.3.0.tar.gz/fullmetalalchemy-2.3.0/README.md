![FullmetalAlchemy Logo](https://raw.githubusercontent.com/eddiethedean/fullmetalalchemy/main/docs/sqllogo.png)
-----------------

# FullmetalAlchemy: Easy-to-use SQL table operations with SQLAlchemy

[![PyPI Latest Release](https://img.shields.io/pypi/v/fullmetalalchemy.svg)](https://pypi.org/project/fullmetalalchemy/)
![Tests](https://github.com/eddiethedean/fullmetalalchemy/actions/workflows/tests.yml/badge.svg)
[![Python Version](https://img.shields.io/pypi/pyversions/fullmetalalchemy.svg)](https://pypi.org/project/fullmetalalchemy/)
[![Coverage](https://img.shields.io/badge/coverage-97%25-brightgreen.svg)](https://github.com/eddiethedean/fullmetalalchemy)
[![Code Quality](https://img.shields.io/badge/code%20quality-A+-success.svg)](https://github.com/eddiethedean/fullmetalalchemy)
[![Type Checked](https://img.shields.io/badge/type%20checked-mypy%20strict-blue.svg)](https://github.com/eddiethedean/fullmetalalchemy)

## What is it?

**FullmetalAlchemy** is a Python package that provides intuitive, high-level functions for common database operations using SQLAlchemy. It simplifies CRUD operations (Create, Read, Update, Delete) while maintaining the power and flexibility of SQLAlchemy under the hood.

### Key Features

- 🔄 **SQLAlchemy 1.4+ and 2.x compatible** - Works seamlessly with both versions
- ⚡ **Async/Await Support** - Full async API for high-performance applications (v2.1.0+)
- 🏗️ **Async Classes** - AsyncTable and AsyncSessionTable for Pythonic async operations (v2.2.0+)
- 📦 **Batch Processing** - Efficient bulk operations with progress tracking and parallel execution (v2.2.0+)
- 🎛️ **Session Module** - Fine-grained transaction control with manual commit/rollback (v2.3.0+)
- 🎯 **Simple API** - Intuitive functions for common database operations
- 🔒 **Transaction Management** - Built-in context managers for safe operations
- 📊 **Pythonic Interface** - Array-like access and familiar Python patterns
- 🚀 **Memory Efficient** - Chunked iteration and concurrent processing for large datasets
- 🛡️ **Type Safe** - Full type hints with MyPy strict mode compliance
- ✅ **Thoroughly Tested** - 84% test coverage with 336 passing tests (258 sync + 78 async)
- 🎨 **Code Quality** - Ruff and MyPy strict mode verified

## Installation

```sh
# Install from PyPI (sync operations only)
pip install fullmetalalchemy

# Install with async support
pip install fullmetalalchemy[async]

# Install for development
pip install fullmetalalchemy[dev]
```

The source code is hosted on GitHub at: https://github.com/eddiethedean/fullmetalalchemy

## Dependencies

**Core Dependencies:**
- **SQLAlchemy** (>=1.4, <3) - Python SQL toolkit and ORM
- **tinytim** (>=0.1.2) - Data transformation utilities
- **frozendict** (>=2.4) - Immutable dictionary support

**Optional Async Dependencies** (install with `[async]`):
- **aiosqlite** (>=0.19) - Async SQLite driver
- **greenlet** (>=3.0) - Greenlet concurrency support
- **asyncpg** (>=0.29) - Async PostgreSQL driver (optional)
- **aiomysql** (>=0.2) - Async MySQL driver (optional)

## Quick Start

### Basic CRUD Operations

```python
import fullmetalalchemy as fa

# Create a database connection
engine = fa.create_engine('sqlite:///mydata.db')

# Create a table with some initial data
table = fa.create.create_table_from_records(
    'employees',
    [
        {'id': 1, 'name': 'Alice', 'department': 'Engineering', 'salary': 95000},
        {'id': 2, 'name': 'Bob', 'department': 'Sales', 'salary': 75000}
    ],
    primary_key='id',
    engine=engine
)

# Get table for operations
table = fa.get_table('employees', engine)

# SELECT: Get all records
records = fa.select.select_records_all(table, engine)
print(records)
# Output:
# [{'id': 1, 'name': 'Alice', 'department': 'Engineering', 'salary': 95000},
#  {'id': 2, 'name': 'Bob', 'department': 'Sales', 'salary': 75000}]

# INSERT: Add new records
fa.insert.insert_records(
    table,
    [
        {'id': 3, 'name': 'Charlie', 'department': 'Engineering', 'salary': 88000},
        {'id': 4, 'name': 'Diana', 'department': 'Marketing', 'salary': 82000}
    ],
    engine
)
# Now table has 4 records

# UPDATE: Modify existing records
fa.update.update_records(
    table,
    [{'id': 2, 'name': 'Bob', 'department': 'Sales', 'salary': 80000}],
    engine
)
record = fa.select.select_record_by_primary_key(table, {'id': 2}, engine)
print(record)
# Output: {'id': 2, 'name': 'Bob', 'department': 'Sales', 'salary': 80000}

# DELETE: Remove records
fa.delete.delete_records(table, 'id', [1, 3], engine)
remaining = fa.select.select_records_all(table, engine)
print(f"Remaining records: {len(remaining)}")
# Output: Remaining records: 2
```

## Usage Examples

### 1. SessionTable - Transaction Management

Use `SessionTable` with context managers for automatic commit/rollback handling:

```python
import fullmetalalchemy as fa

engine = fa.create_engine('sqlite:///products.db')

# Create initial table
fa.create.create_table_from_records(
    'products',
    [
        {'id': 1, 'name': 'Laptop', 'price': 999, 'stock': 10},
        {'id': 2, 'name': 'Mouse', 'price': 25, 'stock': 50}
    ],
    primary_key='id',
    engine=engine
)

# Use context manager - automatically commits on success, rolls back on error
with fa.SessionTable('products', engine) as table:
    # All operations are part of a single transaction
    table.insert_records([{'id': 3, 'name': 'Keyboard', 'price': 75, 'stock': 30}])
    table.update_records([{'id': 2, 'name': 'Mouse', 'price': 29, 'stock': 45}])
    # Automatically commits here if no exceptions

# Verify changes persisted
table = fa.get_table('products', engine)
records = fa.select.select_records_all(table, engine)
print(records)
# Output:
# [{'id': 1, 'name': 'Laptop', 'price': 999, 'stock': 10},
#  {'id': 2, 'name': 'Mouse', 'price': 29, 'stock': 45},
#  {'id': 3, 'name': 'Keyboard', 'price': 75, 'stock': 30}]
```

### 2. Table Class - Pythonic Interface

The `Table` class provides an intuitive, array-like interface:

```python
import fullmetalalchemy as fa

engine = fa.create_engine('sqlite:///orders.db')

# Create initial table
fa.create.create_table_from_records(
    'orders',
    [
        {'id': 1, 'customer': 'John', 'total': 150.00},
        {'id': 2, 'customer': 'Jane', 'total': 200.00}
    ],
    primary_key='id',
    engine=engine
)

# Create Table instance
table = fa.Table('orders', engine)

# Access table properties
print(f"Columns: {table.column_names}")
# Output: Columns: ['id', 'customer', 'total']

print(f"Row count: {len(table)}")
# Output: Row count: 2

# Array-like access
print(table[0])
# Output: {'id': 1, 'customer': 'John', 'total': 150.0}

print(table['customer'])
# Output: ['John', 'Jane']

print(table[0:2])
# Output: [{'id': 1, 'customer': 'John', 'total': 150.0}, 
#          {'id': 2, 'customer': 'Jane', 'total': 200.0}]

# Direct operations (auto-commit)
table.insert_records([{'id': 3, 'customer': 'Alice', 'total': 175.00}])
table.delete_records('id', [2])

print(f"After operations: {len(table)} records")
# Output: After operations: 2 records
```

### 3. Advanced Queries

FullmetalAlchemy provides powerful querying capabilities:

```python
import fullmetalalchemy as fa

engine = fa.create_engine('sqlite:///users.db')

# Create test data
fa.create.create_table_from_records(
    'users',
    [
        {'id': i, 'name': f'User{i}', 'age': 20 + i * 5, 
         'city': ['NYC', 'LA', 'Chicago'][i % 3]}
        for i in range(1, 11)
    ],
    primary_key='id',
    engine=engine
)

table = fa.get_table('users', engine)

# Select specific columns only
records = fa.select.select_records_all(
    table, engine, 
    include_columns=['id', 'name']
)
print(records[:3])
# Output:
# [{'id': 1, 'name': 'User1'}, 
#  {'id': 2, 'name': 'User2'}, 
#  {'id': 3, 'name': 'User3'}]

# Select by slice (rows 2-5)
records = fa.select.select_records_slice(table, 2, 5, engine)
print(records)
# Output:
# [{'id': 3, 'name': 'User3', 'age': 35, 'city': 'NYC'},
#  {'id': 4, 'name': 'User4', 'age': 40, 'city': 'LA'},
#  {'id': 5, 'name': 'User5', 'age': 45, 'city': 'Chicago'}]

# Get all values from a specific column
cities = fa.select.select_column_values_all(table, 'city', engine)
print(f"Unique cities: {set(cities)}")
# Output: Unique cities: {'NYC', 'Chicago', 'LA'}

# Memory-efficient chunked iteration for large datasets
for chunk_num, chunk in enumerate(
    fa.select.select_records_chunks(table, engine, chunksize=3), 1
):
    print(f"Chunk {chunk_num}: {len(chunk)} records")
# Output:
# Chunk 1: 3 records
# Chunk 2: 3 records
# Chunk 3: 3 records
# Chunk 4: 1 records
```

## Async/Await Support (v2.1.0+)

FullmetalAlchemy provides full async/await support for high-performance applications. All CRUD operations have async equivalents in the `async_api` namespace.

### Installation for Async

```sh
# Install with async dependencies
pip install fullmetalalchemy[async]
```

### Basic Async Operations

```python
import asyncio
from fullmetalalchemy import async_api

async def main():
    # Create async engine with aiosqlite driver
    engine = async_api.create_async_engine('sqlite+aiosqlite:///employees.db')
    
    # Create table with initial data
    table = await async_api.create.create_table_from_records(
        'employees',
        [
            {'id': 1, 'name': 'Alice', 'department': 'Engineering', 'salary': 95000},
            {'id': 2, 'name': 'Bob', 'department': 'Sales', 'salary': 75000}
        ],
        primary_key='id',
        engine=engine
    )
    
    # SELECT: Get all records
    records = await async_api.select.select_records_all(table, engine)
    print(records)
    # Output:
    # [{'id': 1, 'name': 'Alice', 'department': 'Engineering', 'salary': 95000},
    #  {'id': 2, 'name': 'Bob', 'department': 'Sales', 'salary': 75000}]
    
    # INSERT: Add new records
    await async_api.insert.insert_records(
        table,
        [
            {'id': 3, 'name': 'Charlie', 'department': 'Engineering', 'salary': 88000},
            {'id': 4, 'name': 'Diana', 'department': 'Marketing', 'salary': 82000}
        ],
        engine
    )
    # Total records: 4
    
    # UPDATE: Modify existing records
    await async_api.update.update_records(
        table,
        [{'id': 2, 'name': 'Bob', 'department': 'Sales', 'salary': 80000}],
        engine
    )
    record = await async_api.select.select_record_by_primary_key(table, {'id': 2}, engine)
    print(record)
    # Output: {'id': 2, 'name': 'Bob', 'department': 'Sales', 'salary': 80000}
    
    # DELETE: Remove records
    await async_api.delete.delete_records_by_values(table, 'id', [1, 3], engine)
    remaining = await async_api.select.select_records_all(table, engine)
    print(f"Remaining records: {len(remaining)}")
    # Output: Remaining records: 2
    
    await engine.dispose()

# Run the async function
asyncio.run(main())
```

### Concurrent Operations

One of the main benefits of async is the ability to run multiple database operations concurrently:

```python
import asyncio
from fullmetalalchemy import async_api

async def main():
    engine = async_api.create_async_engine('sqlite+aiosqlite:///shop.db')
    
    # Create three tables concurrently
    tables = await asyncio.gather(
        async_api.create.create_table_from_records(
            'products',
            [{'id': 1, 'name': 'Laptop', 'price': 999}],
            primary_key='id',
            engine=engine
        ),
        async_api.create.create_table_from_records(
            'customers',
            [{'id': 1, 'name': 'Alice', 'email': 'alice@example.com'}],
            primary_key='id',
            engine=engine
        ),
        async_api.create.create_table_from_records(
            'orders',
            [{'id': 1, 'product_id': 1, 'customer_id': 1}],
            primary_key='id',
            engine=engine
        )
    )
    print(f"Created {len(tables)} tables concurrently")
    # Output: Created 3 tables concurrently
    
    # Query all tables concurrently
    results = await asyncio.gather(
        async_api.select.select_records_all(tables[0], engine),
        async_api.select.select_records_all(tables[1], engine),
        async_api.select.select_records_all(tables[2], engine)
    )
    
    print("Products:", results[0])
    # Output: Products: [{'id': 1, 'name': 'Laptop', 'price': 999}]
    print("Customers:", results[1])
    # Output: Customers: [{'id': 1, 'name': 'Alice', 'email': 'alice@example.com'}]
    print("Orders:", results[2])
    # Output: Orders: [{'id': 1, 'product_id': 1, 'customer_id': 1}]
    
    await engine.dispose()

asyncio.run(main())
```

### Advanced Async Queries

All query operations from the sync API are available in async:

```python
import asyncio
from fullmetalalchemy import async_api

async def main():
    engine = async_api.create_async_engine('sqlite+aiosqlite:///users.db')
    
    # Create test data
    table = await async_api.create.create_table_from_records(
        'users',
        [{'id': i, 'name': f'User{i}', 'age': 20 + i * 5} for i in range(1, 6)],
        primary_key='id',
        engine=engine
    )
    
    # Select with specific columns
    records = await async_api.select.select_records_all(
        table, engine, include_columns=['id', 'name']
    )
    print(records[:3])
    # Output: [{'id': 1, 'name': 'User1'}, {'id': 2, 'name': 'User2'}, {'id': 3, 'name': 'User3'}]
    
    # Select by slice
    records = await async_api.select.select_records_slice(table, 1, 4, engine)
    print(records)
    # Output: [{'id': 2, 'name': 'User2', 'age': 30},
    #          {'id': 3, 'name': 'User3', 'age': 35},
    #          {'id': 4, 'name': 'User4', 'age': 40}]
    
    # Get column values
    ages = await async_api.select.select_column_values_all(table, 'age', engine)
    print(ages)
    # Output: [25, 30, 35, 40, 45]
    
    await engine.dispose()

asyncio.run(main())
```

### Async Database Drivers

FullmetalAlchemy supports multiple async database drivers:

| Database | Driver | Connection String Example |
|----------|--------|---------------------------|
| **SQLite** | `aiosqlite` | `sqlite+aiosqlite:///path/to/db.db` |
| **PostgreSQL** | `asyncpg` | `postgresql+asyncpg://user:pass@localhost/dbname` |
| **MySQL** | `aiomysql` | `mysql+aiomysql://user:pass@localhost/dbname` |

Install the appropriate driver for your database:

```sh
pip install fullmetalalchemy[async]  # Includes aiosqlite
pip install asyncpg  # For PostgreSQL
pip install aiomysql  # For MySQL
```

## Async Classes (v2.1.0+)

### AsyncTable - Pythonic Async Interface

The `AsyncTable` class provides an intuitive, array-like interface for async operations:

```python
import asyncio
from fullmetalalchemy import async_api

async def main():
    engine = async_api.create_async_engine('sqlite+aiosqlite:///products.db')
    
    # Create table with initial data
    await async_api.create.create_table_from_records(
        'products',
        [
            {'id': 1, 'name': 'Laptop', 'price': 999, 'stock': 10},
            {'id': 2, 'name': 'Mouse', 'price': 25, 'stock': 50}
        ],
        primary_key='id',
        engine=engine
    )
    
    # Use AsyncTable class
    async with async_api.AsyncTable('products', engine) as table:
        # Array-like access
        first_product = await table[0]
        print("First product:", first_product)
        # Output: First product: {'id': 1, 'name': 'Laptop', 'price': 999, 'stock': 10}
        
        # Get column values
        names = await table['name']
        print("Product names:", names)
        # Output: Product names: ['Laptop', 'Mouse']
        
        # Insert and update
        await table.insert_records([{'id': 3, 'name': 'Keyboard', 'price': 75, 'stock': 30}])
        await table.update_records([{'id': 2, 'name': 'Mouse', 'price': 29, 'stock': 45}])
        
        # Get count
        count = await table.__len__()
        print(f"Total products: {count}")
        # Output: Total products: 3
        
        # Async iteration
        print("All products:")
        async for product in table:
            print(f"  - {product['name']}: ${product['price']}")
        # Output:
        # All products:
        #   - Laptop: $999
        #   - Mouse: $29
        #   - Keyboard: $75
    
    await engine.dispose()

asyncio.run(main())
```

### AsyncSessionTable - Transaction Management

The `AsyncSessionTable` class provides transaction-safe async operations with automatic commit/rollback:

```python
import asyncio
from fullmetalalchemy import async_api

async def main():
    engine = async_api.create_async_engine('sqlite+aiosqlite:///orders.db')
    
    # Create table
    await async_api.create.create_table_from_records(
        'orders',
        [
            {'id': 1, 'customer': 'John', 'total': 150.0},
            {'id': 2, 'customer': 'Jane', 'total': 200.0}
        ],
        primary_key='id',
        engine=engine
    )
    
    # Transaction automatically commits on success
    async with async_api.AsyncSessionTable('orders', engine) as table:
        await table.insert_records([{'id': 3, 'customer': 'Alice', 'total': 175.0}])
        await table.update_records([{'id': 1, 'customer': 'John', 'total': 160.0}])
        # Auto-commits here
    
    # Verify changes persisted
    async with async_api.AsyncSessionTable('orders', engine) as table:
        records = await table.select_all()
        print(f"Total orders after transaction: {len(records)}")
        # Output: Total orders after transaction: 3
    
    # Transaction rolls back on error
    try:
        async with async_api.AsyncSessionTable('orders', engine) as table:
            await table.insert_records([{'id': 4, 'customer': 'Bob', 'total': 225.0}])
            raise ValueError("Simulated error")
    except ValueError:
        pass
    
    # Verify rollback worked
    async with async_api.AsyncSessionTable('orders', engine) as table:
        records = await table.select_all()
        print(f"Total orders after rollback: {len(records)}")
        # Output: Total orders after rollback: 3 (Bob's order was rolled back)
    
    await engine.dispose()

asyncio.run(main())
```

## Batch Operations (v2.2.0+)

### Sync Batch Processing

Process large datasets efficiently with the `BatchProcessor`:

```python
from fullmetalalchemy import BatchProcessor
import fullmetalalchemy as fa

engine = fa.create_engine('sqlite:///data.db')
table = fa.get_table('users', engine)

# Create large dataset
large_dataset = [
    {'id': i, 'value': i * 10, 'category': f'cat_{i % 5}'}
    for i in range(1, 10001)
]

# Process in batches
processor = BatchProcessor(batch_size=1000, show_progress=False)

result = processor.process_batches(
    large_dataset,
    lambda batch: fa.insert.insert_records(table, batch, engine)
)

print(f"Processed {result.total_records} records in {result.total_batches} batches")
# Output: Processed 10000 records in 10 batches
```

### Async Batch Processing with Parallelism

The `AsyncBatchProcessor` processes multiple batches concurrently for better performance:

```python
import asyncio
from fullmetalalchemy import async_api

async def main():
    engine = async_api.create_async_engine('sqlite+aiosqlite:///data.db')
    
    # Create large dataset
    large_dataset = [{'id': i, 'value': i * 5} for i in range(1, 5001)]
    
    # Process batches concurrently (up to 5 at once)
    processor = async_api.AsyncBatchProcessor(
        batch_size=500,
        max_concurrent=5,
        show_progress=False
    )
    
    async def async_insert_batch(batch):
        # This would be your actual insert operation
        await asyncio.sleep(0.01)  # Simulate I/O
    
    result = await processor.process_batches(large_dataset, async_insert_batch)
    
    print(f"Processed {result.total_records} records in {result.total_batches} batches")
    # Output: Processed 5000 records in 10 batches
    print(f"Max concurrent: {processor.max_concurrent}")
    # Output: Max concurrent: 5
    
    await engine.dispose()

asyncio.run(main())
```

### Batch Error Handling

Handle errors gracefully with the `on_error='continue'` option:

```python
import asyncio
from fullmetalalchemy import async_api

async def main():
    records = [{'id': i, 'status': 'pending'} for i in range(10)]
    
    # Continue processing even if some batches fail
    processor = async_api.AsyncBatchProcessor(batch_size=3, on_error='continue')
    
    async def flaky_operation(batch):
        if batch[0]['id'] == 6:
            raise RuntimeError("Simulated error")
    
    result = await processor.process_batches(records, flaky_operation)
    
    print(f"Total batches: {result.total_batches}, Failed: {len(result.failed_batches)}")
    # Output: Total batches: 4, Failed: 1
    print(f"Successfully processed: {result.total_records - len(result.failed_batches) * 3} records")
    # Output: Successfully processed: 7 records

asyncio.run(main())
```

## Session Module - Fine-Grained Transaction Control (v2.3.0+)

The `session` module provides direct access to session-based operations without auto-commit, allowing for fine-grained transaction control. This is ideal for advanced users who want to manually manage transaction boundaries.

### Sync Session Operations

```python
import fullmetalalchemy as fa

# Create engine and session
engine = fa.create_engine('sqlite:///data.db')
session = fa.features.get_session(engine)
table = fa.get_table('users', engine)

# Perform multiple operations in a single transaction
fa.session.insert_records(table, [
    {'id': 1, 'name': 'Alice', 'email': 'alice@example.com'},
    {'id': 2, 'name': 'Bob', 'email': 'bob@example.com'}
], session)

fa.session.update_records(table, [
    {'id': 1, 'name': 'Alice Updated'}
], session)

fa.session.delete_records(table, 'id', [2], session)

# Commit all changes at once
session.commit()

# Verify results
records = fa.select.select_records_all(table, engine)
print(records)
# Output: [{'id': 1, 'name': 'Alice Updated', 'email': 'alice@example.com'}]

# Or rollback if needed
# session.rollback()
```

### Async Session Operations

For async operations, it's recommended to use `AsyncSessionTable` which provides transaction management with async context managers:

```python
import asyncio
from fullmetalalchemy import async_api

async def main():
    engine = async_api.create_async_engine('sqlite+aiosqlite:///data.db')
    
    # Using AsyncSessionTable for transaction control
    async with async_api.AsyncSessionTable('users', engine) as table:
        # All operations in this context are part of one transaction
        await table.insert_records([
            {'id': 1, 'name': 'Alice', 'status': 'active'},
            {'id': 2, 'name': 'Bob', 'status': 'active'}
        ])
        
        await table.update_records([
            {'id': 1, 'status': 'inactive'}
        ])
        
        await table.delete_records('id', [2])
        
        # Automatically commits on successful exit
    
    # Or use manual commit/rollback
    table = async_api.AsyncSessionTable('users', engine)
    await table.insert_records([{'id': 3, 'name': 'Charlie', 'status': 'active'}])
    await table.commit()  # Manually commit
    
    await engine.dispose()

asyncio.run(main())
```

### Available Session Functions

**Sync (`fa.session`):**
- `insert_records(table, records, session)` - Insert records
- `insert_from_table(table1, table2, session)` - Copy rows between tables
- `update_records(table, records, session, match_column_names=None)` - Update records
- `update_matching_records(table, records, match_column_names, session)` - Update with custom match columns
- `set_column_values(table, column_name, value, session)` - Set all rows in a column
- `delete_records(table, column_name, values, session)` - Delete by column values
- `delete_records_by_values(table, records, session)` - Delete matching all column values
- `delete_all_records(table, session)` - Delete all records

**Async (`async_api.session`):**
- All the same functions with `async`/`await` support

### Why Use Session Functions?

1. **Multiple operations in one transaction** - Group related changes
2. **Manual commit control** - Decide exactly when to commit
3. **Error handling** - Rollback on any error in the transaction
4. **Performance** - Reduce database round-trips
5. **Consistency** - Ensure related changes succeed or fail together

Note: The existing auto-commit functions (`fa.insert.insert_records`, etc.) internally use these session functions, so there's zero code duplication.

## API Overview

### Connection & Table Access
- `fa.create_engine(url)` - Create SQLAlchemy engine
- `fa.get_table(name, engine)` - Get table object for operations
- `fa.get_table_names(engine)` - List all table names in database

### Create Operations
- `fa.create.create_table()` - Create table from specifications
- `fa.create.create_table_from_records()` - Create table from data
- `fa.create.copy_table()` - Duplicate existing table

### Select Operations
- `fa.select.select_records_all()` - Get all records
- `fa.select.select_records_chunks()` - Iterate records in chunks
- `fa.select.select_records_slice()` - Get records by slice
- `fa.select.select_record_by_primary_key()` - Get single record
- `fa.select.select_column_values_all()` - Get all values from column

### Insert Operations
- `fa.insert.insert_records()` - Insert multiple records
- `fa.insert.insert_from_table()` - Copy records from another table

### Update Operations
- `fa.update.update_records()` - Update existing records

### Delete Operations
- `fa.delete.delete_records()` - Delete by column values
- `fa.delete.delete_records_by_values()` - Delete matching records

### Session Operations (v2.3.0+)
- `fa.session.insert_records()` - Insert without auto-commit
- `fa.session.update_records()` - Update without auto-commit
- `fa.session.delete_records()` - Delete without auto-commit
- `async_api.session.*` - Async session operations
- `fa.delete.delete_all_records()` - Clear entire table

### Drop Operations
- `fa.drop.drop_table()` - Remove table from database

## Advanced Features

### Type Safety

FullmetalAlchemy is fully typed with MyPy strict mode compliance:

```python
from typing import List, Dict, Any
import fullmetalalchemy as fa

def process_users(engine: fa.types.SqlConnection) -> List[Dict[str, Any]]:
    table = fa.get_table('users', engine)
    return fa.select.select_records_all(table, engine)
```

### Transaction Control with SessionTable

```python
with fa.SessionTable('orders', engine) as table:
    try:
        table.insert_records([...])
        table.update_records([...])
        # Commits automatically if successful
    except Exception as e:
        # Automatically rolls back on error
        print(f"Transaction failed: {e}")
```

### Bulk Operations

For better performance with large datasets:

```python
# Bulk insert
large_dataset = [{'id': i, 'value': i*2} for i in range(10000)]
fa.insert.insert_records(table, large_dataset, engine)

# Chunked processing
for chunk in fa.select.select_records_chunks(table, engine, chunksize=1000):
    process_chunk(chunk)
```

## Compatibility

- **Python**: 3.8, 3.9, 3.10, 3.11, 3.12, 3.13
- **SQLAlchemy**: 1.4+ and 2.x
- **Databases**: SQLite, PostgreSQL, MySQL, and any SQLAlchemy-supported database

## Development

### Running Tests

```sh
# Install development dependencies
pip install -e ".[dev]"

# Run tests with coverage
pytest tests/ --cov=src/fullmetalalchemy --cov-report=term-missing

# Run code quality checks
ruff check src/ tests/
mypy src/fullmetalalchemy
```

### Code Quality

This project maintains high standards:
- **84% Test Coverage** - Comprehensive test suite with 336 tests (258 sync + 78 async)
- **MyPy Strict Mode** - Full type safety enforcement
- **Ruff Verified** - Modern Python code style
- **SQLAlchemy 1.4/2.x Dual Support** - Backwards compatible
- **Async/Await Ready** - Full async API with AsyncTable/AsyncSessionTable classes
- **Batch Operations** - Efficient processing with parallel execution support

## Roadmap / Coming Soon

Features planned for future releases:

### v2.4.0 - Async Table Metadata Operations
- **Async `get_table()` function** - Currently async operations require passing table objects created with sync `get_table()`. This will add native async table metadata reflection.
- **Full string table name support in async session module** - Allow passing table names as strings to `async_api.session.*` functions without pre-fetching table objects
- **Async table creation helpers** - Improve async table creation workflow

### Future Considerations
- **Query Builder Interface** - Fluent API for complex queries
- **Migration Utilities** - Schema migration helpers
- **Connection Pooling Utilities** - Advanced connection management
- **Export/Import Tools** - CSV, JSON, Parquet data exchange
- **Table Validation** - Schema validation and data integrity checks

Have a feature request? [Open an issue](https://github.com/eddiethedean/fullmetalalchemy/issues) to discuss!

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT License](LICENSE)

## Links

- **Documentation**: https://github.com/eddiethedean/fullmetalalchemy
- **Source Code**: https://github.com/eddiethedean/fullmetalalchemy
- **Issue Tracker**: https://github.com/eddiethedean/fullmetalalchemy/issues
- **PyPI**: https://pypi.org/project/fullmetalalchemy/

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and release notes.
