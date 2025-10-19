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
- 🎯 **Simple API** - Intuitive functions for common database operations
- 🔒 **Transaction Management** - Built-in context managers for safe operations
- 📦 **Pythonic Interface** - Array-like access and familiar Python patterns
- 🚀 **Memory Efficient** - Chunked iteration for large datasets
- 🛡️ **Type Safe** - Full type hints with MyPy strict mode compliance
- ✅ **Thoroughly Tested** - 97% test coverage with 258 passing tests
- 🎨 **Code Quality** - Ruff and MyPy strict mode verified

## Installation

```sh
# Install from PyPI
pip install fullmetalalchemy
```

The source code is hosted on GitHub at: https://github.com/eddiethedean/fullmetalalchemy

## Dependencies

- **SQLAlchemy** (>=1.4, <3) - Python SQL toolkit and ORM
- **tinytim** (>=0.1.2) - Data transformation utilities
- **frozendict** (>=2.4) - Immutable dictionary support

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
- **97% Test Coverage** - Comprehensive test suite with 258 tests
- **MyPy Strict Mode** - Full type safety enforcement
- **Ruff Verified** - Modern Python code style
- **SQLAlchemy 1.4/2.x Dual Support** - Backwards compatible

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
