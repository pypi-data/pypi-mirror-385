# Transmutation

A comprehensive database migration and schema alteration tool built on SQLAlchemy and Alembic.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- **Comprehensive Operations**: Column, table, index, and constraint operations
- **Reversible Migrations**: Built-in migration system with automatic rollback
- **Type Safety**: Full type hints for Python 3.8+
- **Database Support**: SQLite, PostgreSQL, MySQL, and more via SQLAlchemy
- **Simple API**: Easy-to-use functions for common operations
- **Advanced Features**: Batch operations, transaction management, custom SQL
- **Validation**: Automatic validation of operations before execution
- **Error Handling**: Comprehensive exception hierarchy for precise error handling

## Installation

```bash
pip install transmutation
```

## Quick Start

```python
from sqlalchemy import create_engine
import transmutation as tm

# Create engine
engine = create_engine('sqlite:///mydb.db')

# Direct operations
tm.add_column('users', 'email', str, engine, nullable=False)
tm.create_index('idx_email', 'users', 'email', engine, unique=True)
tm.rename_column('users', 'name', 'full_name', engine)

# Using the migration system for rollback capability
migration = tm.Migration(engine)
migration.add_column('users', 'phone', str)
migration.create_unique_constraint('uq_email', 'users', 'email')
migration.upgrade()  # Apply changes

# If something goes wrong, rollback
migration.downgrade()
```

## Core Operations

### Column Operations

#### Add Column

```python
import transmutation as tm

# Basic column addition
tm.add_column('users', 'email', str, engine)

# With constraints
tm.add_column('users', 'age', int, engine, nullable=False, default=0)

# With server default
tm.add_column('users', 'created_at', 'datetime', engine, 
              server_default='CURRENT_TIMESTAMP')
```

#### Rename Column

```python
tm.rename_column('users', 'name', 'full_name', engine)
```

#### Drop Column

```python
tm.drop_column('users', 'middle_name', engine)
```

#### Alter Column

```python
# Change column properties
tm.alter_column('users', 'email', engine, nullable=False)

# Change type
tm.alter_column('users', 'age', engine, type_=int)

# Rename and modify
tm.alter_column('users', 'name', engine, 
                new_column_name='full_name', nullable=False)
```

### Table Operations

#### Create Table

```python
from sqlalchemy import Column, Integer, String

columns = [
    Column('id', Integer, primary_key=True),
    Column('name', String(50), nullable=False),
    Column('email', String(100), unique=True)
]

tm.create_table('users', columns, engine)
```

#### Rename Table

```python
tm.rename_table('old_users', 'users', engine)
```

#### Copy Table

```python
from fullmetalalchemy.features import get_table

source_table = get_table('users', engine)
tm.copy_table(source_table, 'users_backup', engine)

# Copy structure only (no data)
tm.copy_table(source_table, 'users_template', engine, copy_data=False)
```

#### Drop Table

```python
tm.drop_table('old_table', engine, if_exists=True)

# With cascade
tm.drop_table('parent_table', engine, cascade=True)
```

#### Truncate Table

```python
tm.truncate_table('temp_data', engine)
```

#### Create Table from SELECT

```python
from sqlalchemy import select
from fullmetalalchemy.features import get_table

users = get_table('users', engine)
query = select(users).where(users.c.active == True)

tm.create_table_as('active_users', query, engine)
```

### Index Operations

#### Create Index

```python
# Single column index
tm.create_index('idx_email', 'users', 'email', engine)

# Composite index
tm.create_index('idx_name', 'users', ['last_name', 'first_name'], engine)

# Unique index
tm.create_unique_index('idx_unique_email', 'users', 'email', engine)

# Or using create_index with unique=True
tm.create_index('idx_email', 'users', 'email', engine, unique=True)
```

#### Drop Index

```python
tm.drop_index('idx_email', 'users', engine)

# Skip if doesn't exist
tm.drop_index('idx_email', 'users', engine, if_exists=True)
```

### Constraint Operations

#### Foreign Keys

```python
# Create foreign key
tm.create_foreign_key(
    'fk_user_address',
    'addresses',      # source table
    'user_id',        # source column
    'users',          # referenced table
    'id',             # referenced column
    engine,
    ondelete='CASCADE'
)

# Composite foreign key
tm.create_foreign_key(
    'fk_user_role',
    'user_roles',
    ['user_id', 'role_id'],
    'roles',
    ['user_id', 'id'],
    engine
)
```

#### Unique Constraints

```python
# Single column
tm.create_unique_constraint('uq_email', 'users', 'email', engine)

# Multiple columns
tm.create_unique_constraint('uq_user_role', 'user_roles', 
                           ['user_id', 'role_id'], engine)
```

#### Check Constraints

```python
tm.create_check_constraint('ck_age_positive', 'users', 'age > 0', engine)

tm.create_check_constraint('ck_email_format', 'users', 
                          "email LIKE '%@%'", engine)
```

#### Primary Keys

```python
# Create primary key (on table without one)
tm.create_primary_key('users', 'id', engine)

# Composite primary key
tm.create_primary_keys('user_roles', ['user_id', 'role_id'], engine)

# Replace existing primary key
from fullmetalalchemy.features import get_table
table = get_table('users', engine)
tm.replace_primary_key(table, 'uuid', engine)

# Replace with composite key
tm.replace_primary_keys(table, ['tenant_id', 'user_id'], engine)
```

#### Drop Constraints

```python
# Drop any constraint by name and type
tm.drop_constraint('fk_user_address', 'addresses', engine, 
                  type_='foreignkey')

tm.drop_constraint('uq_email', 'users', engine, type_='unique')

tm.drop_constraint('ck_age_positive', 'users', engine, type_='check')
```

## Migration System

The Migration class provides a powerful way to manage schema changes with rollback capability.

### Basic Usage

```python
from sqlalchemy import create_engine
import transmutation as tm

engine = create_engine('sqlite:///mydb.db')
migration = tm.Migration(engine)

# Queue operations
migration.add_column('users', 'email', str, nullable=False)
migration.create_index('idx_email', 'users', 'email', unique=True)
migration.add_column('users', 'phone', str)

# Apply all changes
migration.upgrade()

# If something went wrong, rollback
migration.downgrade()
```

### Batch Operations with Auto-Rollback

```python
migration = tm.Migration(engine)

try:
    with migration.batch_operations():
        migration.add_column('users', 'email', str)
        migration.create_index('idx_email', 'users', 'email')
        migration.create_foreign_key('fk_user', 'posts', 'user_id', 
                                    'users', 'id')
    # Changes are automatically applied on successful exit
except tm.MigrationError as e:
    print(f"Migration failed and was rolled back: {e}")
```

### All Migration Methods

```python
migration = tm.Migration(engine)

# Column operations
migration.add_column('table', 'col', str)
migration.drop_column('table', 'col')
migration.rename_column('table', 'old', 'new')
migration.alter_column('table', 'col', nullable=False)

# Table operations
migration.create_table('table', columns)
migration.drop_table('table')
migration.rename_table('old', 'new')
migration.copy_table(table, 'new_table')

# Index operations
migration.create_index('idx', 'table', 'col')
migration.drop_index('idx', 'table', 'col')
migration.create_unique_index('idx', 'table', 'col')

# Constraint operations
migration.create_foreign_key('fk', 'source', 'col', 'ref', 'ref_col')
migration.create_unique_constraint('uq', 'table', 'col')
migration.create_check_constraint('ck', 'table', 'condition')

# Execute custom SQL
migration.execute_sql("UPDATE users SET active = 1")

# Apply changes
migration.upgrade()

# Check status
print(f"Pending: {migration.pending_operations()}")
print(f"Applied: {migration.applied_operations()}")

# Rollback
migration.downgrade()

# Clear queue without executing
migration.clear()
```

### Transaction Management

```python
# Auto-rollback enabled by default
migration = tm.Migration(engine, auto_transaction=True)

# Disable auto-rollback for manual control
migration = tm.Migration(engine, auto_transaction=False)
```

## Advanced Usage

### Schema Support

All operations support schema specification for databases that use schemas (PostgreSQL):

```python
# PostgreSQL schema support
tm.add_column('users', 'email', str, engine, schema='public')
tm.create_index('idx_email', 'users', 'email', engine, schema='public')
```

### Custom SQL Execution

```python
migration = tm.Migration(engine)

# Execute custom SQL
result = migration.execute_sql(
    "UPDATE users SET status = 'active' WHERE last_login > :date",
    date='2024-01-01'
)
```

### Validation

Transmutation automatically validates operations before execution:

```python
try:
    tm.add_column('nonexistent_table', 'col', str, engine)
except tm.ValidationError as e:
    print(f"Validation failed: {e}")
```

### Working with Alteration Classes

For advanced use cases, you can work directly with Alteration classes:

```python
from transmutation.alteration import AddColumn, CreateIndex

# Create alterations manually
add_col = AddColumn('users', 'email', str, engine)
create_idx = CreateIndex('idx_email', 'users', 'email', engine, unique=True)

# Apply
table = add_col.upgrade()
table = create_idx.upgrade()

# Rollback
create_idx.downgrade()
add_col.downgrade()
```

## Error Handling

Transmutation provides specific exceptions for different error types:

```python
import transmutation as tm

try:
    tm.add_column('users', 'email', str, engine)
except tm.ColumnError as e:
    print(f"Column operation failed: {e}")
except tm.ValidationError as e:
    print(f"Validation failed: {e}")
except tm.TransmutationError as e:
    print(f"General error: {e}")

# Migration-specific errors
try:
    migration.upgrade()
except tm.MigrationError as e:
    print(f"Migration failed: {e}")
except tm.RollbackError as e:
    print(f"Rollback failed: {e}")
```

### Available Exceptions

- `TransmutationError` - Base exception for all transmutation errors
- `MigrationError` - Migration operation failed
- `ColumnError` - Column operation failed
- `TableError` - Table operation failed
- `ConstraintError` - Constraint operation failed
- `IndexError` - Index operation failed
- `ValidationError` - Validation failed before operation
- `RollbackError` - Rollback operation failed

## Database Support

Transmutation works with any database supported by SQLAlchemy and Alembic:

- **SQLite**: Full support with no external dependencies
- **PostgreSQL**: Full support with schema capabilities
- **MySQL/MariaDB**: Full support
- **Oracle**: Supported via SQLAlchemy
- **Microsoft SQL Server**: Supported via SQLAlchemy

### SQLite

SQLite is the default and requires no additional setup. Foreign keys can be enabled:

```python
from sqlalchemy import create_engine, event

engine = create_engine('sqlite:///mydb.db')

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
```

### PostgreSQL

Full schema support:

```python
tm.create_table('users', columns, engine, schema='myschema')
```

## API Organization

Transmutation provides a well-organized API with operations grouped by category:

```python
import transmutation as tm

# Or import specific modules
from transmutation import column, table, index, constraint
from transmutation import Migration

# Column operations
from transmutation.column import add_column, rename_column, drop_column, alter_column

# Table operations  
from transmutation.table import create_table, drop_table, rename_table, copy_table

# Index operations
from transmutation.index import create_index, drop_index, create_unique_index

# Constraint operations
from transmutation.constraint import (
    create_foreign_key,
    create_unique_constraint,
    create_check_constraint,
    drop_constraint
)
```

## Examples

### Complete Migration Example

```python
from sqlalchemy import create_engine, Column, Integer, String
import transmutation as tm

# Setup
engine = create_engine('sqlite:///myapp.db')

# Create a new table
columns = [
    Column('id', Integer, primary_key=True),
    Column('username', String(50), nullable=False),
    Column('email', String(100))
]
tm.create_table('users', columns, engine)

# Add indexes
tm.create_unique_index('idx_username', 'users', 'username', engine)
tm.create_index('idx_email', 'users', 'email', engine)

# Add constraints
tm.create_check_constraint('ck_username_length', 'users', 
                          'LENGTH(username) >= 3', engine)

# Modify existing table
tm.add_column('users', 'created_at', 'datetime', engine,
             server_default='CURRENT_TIMESTAMP')
tm.alter_column('users', 'email', engine, nullable=False)
```

### Using Migration for Complex Changes

```python
from sqlalchemy import create_engine
import transmutation as tm

engine = create_engine('sqlite:///myapp.db')
migration = tm.Migration(engine)

# Queue multiple related changes
migration.add_column('users', 'status', str, default='active')
migration.create_index('idx_status', 'users', 'status')
migration.add_column('users', 'last_login', 'datetime')

# Create posts table with foreign key to users
from sqlalchemy import Column, Integer, String, Text
posts_columns = [
    Column('id', Integer, primary_key=True),
    Column('user_id', Integer, nullable=False),
    Column('title', String(200), nullable=False),
    Column('content', Text)
]
migration.create_table('posts', posts_columns)
migration.create_foreign_key('fk_post_user', 'posts', 'user_id', 
                            'users', 'id', ondelete='CASCADE')
migration.create_index('idx_user_posts', 'posts', 'user_id')

# Apply all changes atomically
migration.upgrade()

# If anything goes wrong:
# migration.downgrade()
```

### Data Migration with Custom SQL

```python
migration = tm.Migration(engine)

# Add new column
migration.add_column('users', 'full_name', str)

# Populate it with data using custom SQL
migration.execute_sql(
    "UPDATE users SET full_name = name || ' ' || surname WHERE surname IS NOT NULL"
)
migration.execute_sql(
    "UPDATE users SET full_name = name WHERE surname IS NULL"
)

# Drop old columns
migration.drop_column('users', 'name')
migration.drop_column('users', 'surname')

# Apply all changes
migration.upgrade()
```

## Development

### Setup

```bash
# Clone repository
git clone https://github.com/odosmatthews/transmutation.git
cd transmutation

# Install development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_alter.py

# With coverage report
pytest --cov=transmutation --cov-report=html

# Open coverage report
open htmlcov/index.html
```

### Code Quality

```bash
# Run type checking
mypy src

# Run linter
ruff check src tests

# Auto-fix linting issues
ruff check --fix src tests

# Format code
black src tests

# Sort imports
isort src tests
```

## Best Practices

### 1. Use Migration for Complex Changes

For multiple related changes, use the Migration system:

```python
# Good - atomic, reversible
migration = tm.Migration(engine)
migration.add_column('users', 'email', str)
migration.create_index('idx_email', 'users', 'email')
migration.upgrade()

# Less ideal - individual operations
tm.add_column('users', 'email', str, engine)
tm.create_index('idx_email', 'users', 'email', engine)
```

### 2. Always Handle Errors

```python
try:
    migration.upgrade()
except tm.MigrationError as e:
    logger.error(f"Migration failed: {e}")
    migration.downgrade()
    raise
```

### 3. Use Validation

Transmutation validates operations automatically, but you can also validate manually:

```python
from transmutation.utils import validate_table_exists, validate_column_exists

validate_table_exists('users', engine)
validate_column_exists('users', 'email', engine)
```

### 4. Test Your Migrations

Always test migrations in a development environment first:

```python
def test_migration():
    # Setup test database
    engine = create_engine('sqlite:///:memory:')
    
    # Run migration
    migration = tm.Migration(engine)
    migration.add_column('users', 'new_col', str)
    migration.upgrade()
    
    # Verify
    from fullmetalalchemy.features import get_table
    table = get_table('users', engine)
    assert 'new_col' in table.columns
    
    # Test rollback
    migration.downgrade()
    table = get_table('users', engine)
    assert 'new_col' not in table.columns
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Add tests for new features
- Maintain test coverage above 65%
- Follow type hints for all functions
- Add comprehensive docstrings
- Run linters before committing

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

Built on top of:
- [SQLAlchemy](https://www.sqlalchemy.org/) - The Python SQL toolkit
- [Alembic](https://alembic.sqlalchemy.org/) - Database migration tool
- [fullmetalalchemy](https://github.com/kajuberdut/fullmetalalchemy) - SQLAlchemy utilities

## Support

For issues, questions, or contributions, please visit the GitHub repository.
