"""Table operations for database schema modifications."""

from typing import Optional, List, Any

from sqlalchemy import Table, Column, MetaData, text
from sqlalchemy.engine import Engine
from sqlalchemy.sql import Select

from fullmetalalchemy.features import get_table
from fullmetalalchemy.insert import insert_from_table
from fullmetalalchemy.drop import drop_table as fullmetalalchemy_drop_table

from transmutation.utils import (
    _get_op,
    validate_table_exists,
    table_exists
)
from transmutation.exceptions import TableError


def rename_table(
    old_table_name: str,
    new_table_name: str,
    engine: Engine,
    schema: Optional[str] = None
) -> Table:
    """
    Rename a table.
    
    Args:
        old_table_name: Current name of the table
        new_table_name: New name for the table
        engine: SQLAlchemy Engine instance
        schema: Optional schema name
        
    Returns:
        Newly reflected SQLAlchemy Table object
        
    Raises:
        TableError: If the rename operation fails
        ValidationError: If the table doesn't exist
        
    Example:
        >>> from sqlalchemy import create_engine
        >>> engine = create_engine('sqlite:///test.db')
        >>> table = rename_table('old_users', 'users', engine)
    """
    try:
        validate_table_exists(old_table_name, engine, schema)
        
        op = _get_op(engine)
        op.rename_table(old_table_name, new_table_name, schema=schema)  # type: ignore
        
        return get_table(new_table_name, engine, schema=schema)
    except Exception as e:
        if hasattr(e, '__class__') and 'ValidationError' in e.__class__.__name__:
            raise
        raise TableError(
            f"Failed to rename table '{old_table_name}': {str(e)}"
        ) from e


def create_table(
    table_name: str,
    columns: List[Column[Any]],
    engine: Engine,
    schema: Optional[str] = None,
    if_not_exists: bool = False
) -> Table:
    """
    Create a new table with the specified columns.
    
    Args:
        table_name: Name for the new table
        columns: List of SQLAlchemy Column objects
        engine: SQLAlchemy Engine instance
        schema: Optional schema name
        if_not_exists: Skip creation if table already exists (default: False)
        
    Returns:
        Newly reflected SQLAlchemy Table object
        
    Raises:
        TableError: If the create operation fails
        
    Example:
        >>> from sqlalchemy import create_engine, Column, Integer, String
        >>> engine = create_engine('sqlite:///test.db')
        >>> columns = [
        ...     Column('id', Integer, primary_key=True),
        ...     Column('name', String(50), nullable=False)
        ... ]
        >>> table = create_table('users', columns, engine)
    """
    try:
        if if_not_exists and table_exists(table_name, engine, schema):
            return get_table(table_name, engine, schema=schema)
        
        op = _get_op(engine)
        metadata = MetaData()
        
        op.create_table(table_name, *columns, metadata, schema=schema)  # type: ignore
        
        return get_table(table_name, engine, schema=schema)
    except Exception as e:
        raise TableError(
            f"Failed to create table '{table_name}': {str(e)}"
        ) from e


def drop_table(
    table_name: str,
    engine: Engine,
    schema: Optional[str] = None,
    cascade: bool = False,
    if_exists: bool = False
) -> None:
    """
    Drop a table from the database.
    
    Args:
        table_name: Name of the table to drop
        engine: SQLAlchemy Engine instance
        schema: Optional schema name
        cascade: Drop dependent objects (default: False)
        if_exists: Skip if table doesn't exist (default: False)
        
    Raises:
        TableError: If the drop operation fails
        ValidationError: If the table doesn't exist and if_exists is False
        
    Example:
        >>> from sqlalchemy import create_engine
        >>> engine = create_engine('sqlite:///test.db')
        >>> drop_table('old_table', engine, if_exists=True)
    """
    try:
        if if_exists and not table_exists(table_name, engine, schema):
            return
        
        validate_table_exists(table_name, engine, schema)
        
        op = _get_op(engine)
        op.drop_table(table_name, schema=schema)  # type: ignore
        
    except Exception as e:
        if hasattr(e, '__class__') and 'ValidationError' in e.__class__.__name__:
            raise
        raise TableError(
            f"Failed to drop table '{table_name}': {str(e)}"
        ) from e


def copy_table(
    table: Table,
    new_table_name: str,
    engine: Engine,
    if_exists: str = 'replace',
    schema: Optional[str] = None,
    copy_data: bool = True
) -> Table:
    """
    Create a copy of a table with a new name.
    
    Args:
        table: SQLAlchemy Table object to copy
        new_table_name: Name for the new table
        engine: SQLAlchemy Engine instance
        if_exists: Action if table exists ('replace', 'fail', 'skip')
        schema: Optional schema name
        copy_data: Whether to copy data from source table (default: True)
        
    Returns:
        The new SQLAlchemy Table object
        
    Raises:
        TableError: If the copy operation fails
        
    Example:
        >>> from sqlalchemy import create_engine
        >>> from sqlalchemize.features import get_table
        >>> engine = create_engine('sqlite:///test.db')
        >>> source_table = get_table('users', engine)
        >>> new_table = copy_table(source_table, 'users_backup', engine)
    """
    try:
        # Handle if_exists logic
        if table_exists(new_table_name, engine, schema):
            if if_exists == 'fail':
                raise TableError(f"Table '{new_table_name}' already exists")
            elif if_exists == 'skip':
                return get_table(new_table_name, engine, schema=schema)
            elif if_exists == 'replace':
                fullmetalalchemy_drop_table(new_table_name, engine, schema=schema)
        
        op = _get_op(engine)
        op.create_table(
            new_table_name, 
            *table.c, 
            table.metadata, 
            schema=schema
        )  # type: ignore
        
        new_table = get_table(new_table_name, engine, schema=schema)
        
        # Copy data if requested
        if copy_data:
            insert_from_table(table, new_table, engine)
        
        return new_table
    except Exception as e:
        if hasattr(e, '__class__') and 'TableError' in e.__class__.__name__:
            raise
        raise TableError(
            f"Failed to copy table '{table.name}' to '{new_table_name}': {str(e)}"
        ) from e


def truncate_table(
    table_name: str,
    engine: Engine,
    schema: Optional[str] = None,
    cascade: bool = False
) -> None:
    """
    Truncate all data from a table.
    
    Note: TRUNCATE is not supported on all databases. Falls back to DELETE if needed.
    
    Args:
        table_name: Name of the table to truncate
        engine: SQLAlchemy Engine instance
        schema: Optional schema name
        cascade: Cascade truncation to dependent tables (default: False)
        
    Raises:
        TableError: If the truncate operation fails
        ValidationError: If the table doesn't exist
        
    Example:
        >>> from sqlalchemy import create_engine
        >>> engine = create_engine('sqlite:///test.db')
        >>> truncate_table('temp_data', engine)
    """
    try:
        validate_table_exists(table_name, engine, schema)
        
        # Build fully qualified table name
        full_table_name = f"{schema}.{table_name}" if schema else table_name
        
        # Try TRUNCATE first, fall back to DELETE if not supported
        with engine.begin() as conn:
            try:
                cascade_clause = " CASCADE" if cascade else ""
                conn.execute(text(f"TRUNCATE TABLE {full_table_name}{cascade_clause}"))
            except Exception:
                # Fall back to DELETE for databases that don't support TRUNCATE
                conn.execute(text(f"DELETE FROM {full_table_name}"))
                
    except Exception as e:
        if hasattr(e, '__class__') and 'ValidationError' in e.__class__.__name__:
            raise
        raise TableError(
            f"Failed to truncate table '{table_name}': {str(e)}"
        ) from e


def create_table_as(
    table_name: str,
    select_query: Select[Any],
    engine: Engine,
    schema: Optional[str] = None,
    if_not_exists: bool = False
) -> Table:
    """
    Create a table from a SELECT query (CREATE TABLE AS SELECT).
    
    Note: This uses database-specific SQL and may have limitations.
    
    Args:
        table_name: Name for the new table
        select_query: SQLAlchemy Select object
        engine: SQLAlchemy Engine instance
        schema: Optional schema name
        if_not_exists: Skip creation if table already exists (default: False)
        
    Returns:
        Newly reflected SQLAlchemy Table object
        
    Raises:
        TableError: If the create operation fails
        
    Example:
        >>> from sqlalchemy import create_engine, select
        >>> from sqlalchemize.features import get_table
        >>> engine = create_engine('sqlite:///test.db')
        >>> users = get_table('users', engine)
        >>> query = select(users).where(users.c.active == True)
        >>> new_table = create_table_as('active_users', query, engine)
    """
    try:
        if if_not_exists and table_exists(table_name, engine, schema):
            return get_table(table_name, engine, schema=schema)
        
        # Build fully qualified table name
        full_table_name = f"{schema}.{table_name}" if schema else table_name
        
        # Compile the select query
        compiled = select_query.compile(engine, compile_kwargs={"literal_binds": True})
        
        # Execute CREATE TABLE AS SELECT
        with engine.begin() as conn:
            create_sql = f"CREATE TABLE {full_table_name} AS {compiled}"
            conn.execute(text(create_sql))
        
        return get_table(table_name, engine, schema=schema)
    except Exception as e:
        raise TableError(
            f"Failed to create table '{table_name}' from SELECT: {str(e)}"
        ) from e

