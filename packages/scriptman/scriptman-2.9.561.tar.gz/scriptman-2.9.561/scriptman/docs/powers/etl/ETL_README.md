# ETL Module Documentation

## Overview

The **ETL (Extract, Transform, Load)** module provides a powerful, thread-safe, and easy-to-use interface for database operations with built-in deadlock prevention, automatic retry logic, and data transformation capabilities.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Core Features](#core-features)
3. [Architecture](#architecture)
4. [API Reference](#api-reference)
5. [Advanced Usage](#advanced-usage)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Basic Example

```python
from scriptman.powers.etl import ETL
from scriptman.powers.database import DatabaseHandler

# Initialize database connection
db = DatabaseHandler(
    server="your_server",
    database="your_database",
    driver="ODBC Driver 17 for SQL Server"
)

# Extract data from database
etl = ETL.from_db(
    db=db,
    query="SELECT * FROM customers WHERE region = :region",
    params={"region": "North"}
)

# Transform data
etl = (
    etl.to_snake_case()              # Convert column names to snake_case
       .filter(etl['status'] == 'active')  # Filter active customers
       .set_index('customer_id', inplace=True)  # Set index
)

# Load data to another table
etl.to_db(
    db_handler=db,
    table_name="active_customers_north",
    method="upsert"
)
```

---

## Core Features

### 🔒 **Deadlock Prevention**
- Automatic table-level queueing prevents concurrent writes to the same table
- Operations on different tables run in parallel
- One operation per table at a time (hard-coded for safety)

### 🔄 **Automatic Retry Logic**
- Retries database operations on transient failures
- Exponential backoff (10s → 60s max delay)
- Up to 5 retry attempts
- Handles connection timeouts and pool exhaustion

### 🎯 **Smart Table Detection**
- Automatically extracts table names from SQL queries
- Supports INSERT, UPDATE, DELETE, MERGE, TRUNCATE, CREATE, ALTER
- No manual table name specification needed

### 📊 **Data Transformation**
- Built-in pandas DataFrame operations
- Column name sanitization (SQL-safe)
- Case conversion (snake_case, camelCase)
- Nested data flattening
- Merge, filter, concat operations

### 🚀 **Performance Optimized**
- Batch operations support
- Connection pool auto-upgrade for ETL workloads
- Parallel execution across different tables
- Efficient memory usage

---

## Architecture

### Component Overview

```
┌─────────────────────────────────────────────────┐
│ ETL (High-Level API)                            │
│ - from_db(), to_db()                            │
│ - Data transformations                          │
│ - File operations (CSV, JSON)                   │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│ ETLDatabase (Composition Wrapper)               │
│ - Automatic table name extraction               │
│ - Queue management coordination                 │
│ - Retry logic decorator                         │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│ _TableQueueManager (Singleton)                  │
│ - Per-table semaphores (max_concurrent=1)       │
│ - Active operation tracking                     │
│ - Automatic cleanup every 5 minutes             │
└─────────────────────────────────────────────────┘
```

### Key Design Decisions

1. **Table-Level Locking**: Prevents deadlocks by serializing operations on the same table
2. **No Caching**: Removed to reduce complexity; users can implement custom caching if needed
3. **Automatic Everything**: Table detection, retry, queue management - all automatic
4. **Composition over Inheritance**: ETLDatabase wraps DatabaseHandler without modifying it

---

## API Reference

See [ETL_API_Reference.md](./ETL_API_Reference.md) for complete API documentation.

### Quick Reference

#### Extraction Methods
```python
ETL.from_db(db, query, params={})           # Extract from database
ETL.from_csv(file_path)                     # Extract from CSV
ETL.from_json(file_path)                    # Extract from JSON
ETL.from_dataframe(df)                      # Extract from pandas DataFrame
ETL.from_list(data)                         # Extract from list of dicts
```

#### Transformation Methods
```python
etl.transform(function)                     # Apply custom transformation
etl.merge(right, how="inner", on=None)      # Merge with another dataset
etl.filter(condition)                       # Filter rows
etl.to_snake_case()                         # Convert columns to snake_case
etl.to_camel_case()                         # Convert columns to camelCase
etl.sanitize_names()                        # Make names SQL-safe
etl.flatten(column)                         # Flatten nested dictionaries
```

#### Loading Methods
```python
etl.to_db(db, table_name, method="upsert")  # Load to database
etl.to_csv(file_path)                       # Save to CSV
etl.to_json(file_path)                      # Save to JSON
etl.to_list()                               # Convert to list of dicts
etl.to_dataframe()                          # Get underlying DataFrame
```

---

## Advanced Usage

### 1. Complex Transformations

```python
from scriptman.powers.etl import ETL

# Extract
orders = ETL.from_db(db, "SELECT * FROM orders WHERE date >= :start_date",
                     params={"start_date": "2024-01-01"})

# Transform with chaining
processed = (
    orders
    .to_snake_case()
    .set_index('order_id', inplace=True)
    .transform(lambda df: df[df['total'] > 100])  # Custom filter
    .flatten('metadata')  # Flatten nested JSON column
)

# Load
processed.to_db(db, "processed_orders", method="replace")
```

### 2. Upsert with Logical Keys

```python
# Create table with logical keys (no database constraints)
etl = ETL(data).set_index(['customer_id', 'order_date'], inplace=True)

etl.to_db(
    db_handler=db,
    table_name="customer_orders",
    method="upsert",
    use_logical_keys=True,  # No PRIMARY KEY constraint in database
    synchronize_schema=True  # Auto-add missing columns
)
```

### 3. Batch Processing

```python
# Process large datasets in batches
large_etl = ETL.from_csv("large_file.csv")

large_etl.to_db(
    db_handler=db,
    table_name="large_table",
    batch_size=5000,        # Insert 5000 rows at a time
    batch_execute=True,      # Use batch operations
    method="insert"
)
```

### 4. Schema Synchronization

```python
# Automatically add missing columns to existing table
etl = ETL(new_data_with_extra_columns)

etl.to_db(
    db_handler=db,
    table_name="existing_table",
    synchronize_schema=True,  # Auto-add missing columns
    force_nvarchar=False      # Use proper data types
)
```

### 5. Parallel Processing Different Tables

```python
from scriptman.powers.tasks import TaskExecutor

executor = TaskExecutor()

# These run in parallel (different tables)
tasks = executor.multithread([
    (ETL(customers).to_db, (db, "customers"), {}),
    (ETL(orders).to_db, (db, "orders"), {}),
    (ETL(products).to_db, (db, "products"), {})
])

results = tasks.await_results()
```

---

## Best Practices

### ✅ DO

1. **Set Index for Upsert/Update Operations**
   ```python
   etl = ETL(data).set_index(['id'], inplace=True)
   etl.to_db(db, "table", method="upsert")
   ```

2. **Use Batch Operations for Large Datasets**
   ```python
   etl.to_db(db, "table", batch_size=1000, batch_execute=True)
   ```

3. **Sanitize Column Names**
   ```python
   etl.to_db(db, "table", sanitize_column_names=True)  # Default
   ```

4. **Use Proper Methods**
   - `truncate`: Clear existing data, then insert
   - `replace`: Drop and recreate table
   - `insert`: Insert new rows only
   - `update`: Update existing rows (requires index)
   - `upsert`: Insert new or update existing (recommended)

5. **Handle Exceptions**
   ```python
   try:
       etl.to_db(db, "table", method="upsert")
   except DatabaseError as e:
       logger.error(f"Database operation failed: {e}")
   ```

### ❌ DON'T

1. **Don't Insert Without Index for Upsert**
   ```python
   # ❌ BAD - will raise error
   ETL(data).to_db(db, "table", method="upsert")

   # ✅ GOOD
   ETL(data).set_index('id', inplace=True).to_db(db, "table", method="upsert")
   ```

2. **Don't Use Multiple Small Writes to Same Table**
   ```python
   # ❌ SLOW - 3 queue acquisitions
   for batch in batches:
       ETL(batch).to_db(db, "customers")

   # ✅ FAST - 1 queue acquisition
   ETL(pd.concat(batches)).to_db(db, "customers")
   ```

3. **Don't Ignore Schema Synchronization Issues**
   ```python
   # ✅ Let it auto-sync
   etl.to_db(db, "table", synchronize_schema=True)
   ```

4. **Don't Use force_nvarchar Unless Necessary**
   ```python
   # ❌ BAD - all columns become NVARCHAR(MAX)
   etl.to_db(db, "table", force_nvarchar=True)

   # ✅ GOOD - proper data types
   etl.to_db(db, "table", force_nvarchar=False)
   ```

---

## Troubleshooting

### Issue: "Dataset has no index!"

**Problem:** Trying to use `method="upsert"` or `method="update"` without setting an index.

**Solution:**
```python
etl = ETL(data).set_index(['primary_key_column'], inplace=True)
etl.to_db(db, "table", method="upsert")
```

---

### Issue: Operations on Same Table Are Slow

**Problem:** Multiple operations on the same table are serializing.

**Why:** This is by design to prevent deadlocks. Only one operation per table at a time.

**Solution:** Batch your operations:
```python
# Instead of multiple small writes:
all_data = pd.concat([batch1, batch2, batch3])
ETL(all_data).to_db(db, "table")
```

---

### Issue: Table Name Not Detected

**Problem:** Complex query doesn't have table name extracted.

**Symptoms:** Log shows `"🔍 No table name available - executing without queue"`

**Impact:** Operation executes without queue lock (potential deadlock risk).

**Queries that work:**
- `INSERT INTO table_name ...`
- `UPDATE table_name SET ...`
- `DELETE FROM table_name ...`
- `MERGE table_name AS target ...`

**Queries that don't work:**
- `WITH cte AS (...) INSERT INTO ...`
- `EXEC stored_procedure ...`
- Complex subqueries

**Solution:** For these cases, the operation still executes, but without queue protection. Ensure your queries don't conflict.

---

### Issue: Deadlock Despite Queue

**Problem:** Still getting deadlocks.

**Possible Causes:**
1. Using stored procedures (table name not detected)
2. Complex CTEs or subqueries
3. Cross-database operations

**Solution:** Verify table name extraction in logs. Look for successful extraction messages.

---

### Issue: Memory Growing Over Time

**Problem:** `_TableQueueManager` accumulating semaphores.

**Why:** Many different tables being accessed.

**Solution:** The queue manager auto-cleans every 5 minutes. If memory is still an issue, restart your application periodically or use fewer unique table names.

---

## Performance Tips

### 1. Batch Size Optimization

```python
# Test different batch sizes to find optimal
for batch_size in [500, 1000, 5000, 10000]:
    start = time()
    etl.to_db(db, "table", batch_size=batch_size)
    print(f"Batch size {batch_size}: {time() - start}s")
```

### 2. Connection Pool Tuning

```python
# ETL automatically upgrades pool for heavy operations
db = DatabaseHandler(...)
# Pool is auto-upgraded when ETLDatabase is initialized
```

### 3. Parallel Table Operations

```python
# Operations on different tables run in parallel
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [
        executor.submit(ETL(data1).to_db, db, "table1"),
        executor.submit(ETL(data2).to_db, db, "table2"),
        executor.submit(ETL(data3).to_db, db, "table3"),
    ]
    results = [f.result() for f in futures]
```

---

## See Also

- [ETL API Reference](./ETL_API_Reference.md) - Complete API documentation
- [ETL Examples](./ETL_Examples.md) - More usage examples
- [Main Documentation](../../README.md) - Back to documentation index

---

## Version History

### v2.0.0 (Current)
- ✅ Removed caching functionality (breaking change)
- ✅ Removed `table_name` parameter from all methods (breaking change)
- ✅ Removed `max_concurrent_per_table` parameter (breaking change)
- ✅ Removed `from_db_cached()` and `from_db_fresh()` methods (breaking change)
- ✅ Hard-coded `max_concurrent_per_table=1` for safety
- ✅ Simplified API and improved documentation

### Migration from v1.x

**Old Code:**
```python
etl = ETL.from_db_cached(db, query, cache_ttl=1800)
etl = ETL.from_db(db, query, use_cache=True, table_name="customers")
etl.to_db(db, "table", max_concurrent_per_table=2)
```

**New Code:**
```python
etl = ETL.from_db(db, query)  # Simpler, no caching
etl.to_db(db, "table")  # No max_concurrent parameter
```

---

**Questions or Issues?** Please refer to the troubleshooting section or check the examples documentation.

