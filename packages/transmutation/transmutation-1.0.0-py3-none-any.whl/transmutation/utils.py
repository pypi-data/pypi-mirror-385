"""Utility functions for transmutation operations."""

from typing import Optional, List, Dict, Any
from contextlib import contextmanager

from sqlalchemy.engine import Engine
from sqlalchemy import inspect, text as sql_text
from alembic.runtime.migration import MigrationContext
from alembic.operations import Operations

from transmutation.exceptions import ValidationError


def _get_op(engine: Engine) -> Operations:
    """
    Create an Alembic Operations object for the given engine.
    
    Args:
        engine: SQLAlchemy Engine instance
        
    Returns:
        Alembic Operations instance
    """
    conn = engine.connect()
    ctx = MigrationContext.configure(conn)
    return Operations(ctx)


def get_dialect_name(engine: Engine) -> str:
    """
    Get the database dialect name from the engine.
    
    Args:
        engine: SQLAlchemy Engine instance
        
    Returns:
        Dialect name (e.g., 'sqlite', 'postgresql', 'mysql')
    """
    return engine.dialect.name


def is_sqlite(engine: Engine) -> bool:
    """Check if the engine is for SQLite."""
    return get_dialect_name(engine) == 'sqlite'


def is_postgresql(engine: Engine) -> bool:
    """Check if the engine is for PostgreSQL."""
    return get_dialect_name(engine) == 'postgresql'


def is_mysql(engine: Engine) -> bool:
    """Check if the engine is for MySQL."""
    return get_dialect_name(engine) in ('mysql', 'mariadb')


def table_exists(table_name: str, engine: Engine, schema: Optional[str] = None) -> bool:
    """
    Check if a table exists in the database.
    
    Args:
        table_name: Name of the table
        engine: SQLAlchemy Engine instance
        schema: Optional schema name
        
    Returns:
        True if table exists, False otherwise
    """
    inspector = inspect(engine)
    return inspector.has_table(table_name, schema=schema)


def validate_table_exists(
    table_name: str, 
    engine: Engine, 
    schema: Optional[str] = None
) -> None:
    """
    Validate that a table exists, raise ValidationError if not.
    
    Args:
        table_name: Name of the table
        engine: SQLAlchemy Engine instance
        schema: Optional schema name
        
    Raises:
        ValidationError: If table does not exist
    """
    if not table_exists(table_name, engine, schema):
        schema_msg = f" in schema '{schema}'" if schema else ""
        raise ValidationError(f"Table '{table_name}' does not exist{schema_msg}")


def get_table_names(engine: Engine, schema: Optional[str] = None) -> List[str]:
    """
    Get list of all table names in the database.
    
    Args:
        engine: SQLAlchemy Engine instance
        schema: Optional schema name
        
    Returns:
        List of table names
    """
    inspector = inspect(engine)
    return inspector.get_table_names(schema=schema)


def column_exists(
    table_name: str, 
    column_name: str, 
    engine: Engine, 
    schema: Optional[str] = None
) -> bool:
    """
    Check if a column exists in a table.
    
    Args:
        table_name: Name of the table
        column_name: Name of the column
        engine: SQLAlchemy Engine instance
        schema: Optional schema name
        
    Returns:
        True if column exists, False otherwise
    """
    if not table_exists(table_name, engine, schema):
        return False
    
    inspector = inspect(engine)
    columns = inspector.get_columns(table_name, schema=schema)
    return any(col['name'] == column_name for col in columns)


def validate_column_exists(
    table_name: str, 
    column_name: str, 
    engine: Engine, 
    schema: Optional[str] = None
) -> None:
    """
    Validate that a column exists in a table.
    
    Args:
        table_name: Name of the table
        column_name: Name of the column
        engine: SQLAlchemy Engine instance
        schema: Optional schema name
        
    Raises:
        ValidationError: If column does not exist
    """
    validate_table_exists(table_name, engine, schema)
    if not column_exists(table_name, column_name, engine, schema):
        raise ValidationError(
            f"Column '{column_name}' does not exist in table '{table_name}'"
        )


def index_exists(
    index_name: str, 
    table_name: str, 
    engine: Engine, 
    schema: Optional[str] = None
) -> bool:
    """
    Check if an index exists on a table.
    
    Args:
        index_name: Name of the index
        table_name: Name of the table
        engine: SQLAlchemy Engine instance
        schema: Optional schema name
        
    Returns:
        True if index exists, False otherwise
    """
    if not table_exists(table_name, engine, schema):
        return False
    
    inspector = inspect(engine)
    indexes = inspector.get_indexes(table_name, schema=schema)
    return any(idx['name'] == index_name for idx in indexes)


def get_primary_key_columns(
    table_name: str, 
    engine: Engine, 
    schema: Optional[str] = None
) -> List[str]:
    """
    Get the primary key column names for a table.
    
    Args:
        table_name: Name of the table
        engine: SQLAlchemy Engine instance
        schema: Optional schema name
        
    Returns:
        List of primary key column names
    """
    inspector = inspect(engine)
    pk_constraint = inspector.get_pk_constraint(table_name, schema=schema)
    return pk_constraint.get('constrained_columns', [])


def get_foreign_keys(
    table_name: str, 
    engine: Engine, 
    schema: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get foreign key information for a table.
    
    Args:
        table_name: Name of the table
        engine: SQLAlchemy Engine instance
        schema: Optional schema name
        
    Returns:
        List of foreign key dictionaries
    """
    inspector = inspect(engine)
    fks = inspector.get_foreign_keys(table_name, schema=schema)
    # Cast to the expected type
    return fks  # type: ignore[return-value]


def supports_foreign_keys(engine: Engine) -> bool:
    """
    Check if the database supports foreign keys.
    
    Args:
        engine: SQLAlchemy Engine instance
        
    Returns:
        True if foreign keys are supported
    """
    # SQLite with older versions may not support foreign keys
    if is_sqlite(engine):
        # Check if foreign keys are enabled
        with engine.connect() as conn:
            result = conn.execute(sql_text("PRAGMA foreign_keys"))
            row = result.fetchone()
            return row[0] == 1 if row else False
    return True


@contextmanager
def transaction_context(engine: Engine):
    """
    Context manager for database transactions with automatic rollback on error.
    
    Args:
        engine: SQLAlchemy Engine instance
        
    Yields:
        Connection object
        
    Example:
        >>> with transaction_context(engine) as conn:
        ...     conn.execute("INSERT INTO table VALUES (1, 'value')")
    """
    conn = engine.connect()
    trans = conn.begin()
    try:
        yield conn
        trans.commit()
    except Exception:
        trans.rollback()
        raise
    finally:
        conn.close()

