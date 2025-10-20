"""Index operations for database schema modifications."""

from typing import List, Optional, Union

from sqlalchemy import Table
from sqlalchemy.engine import Engine

from fullmetalalchemy.features import get_table

from transmutation.utils import (
    _get_op, 
    validate_table_exists, 
    validate_column_exists,
    index_exists
)
from transmutation.exceptions import IndexError as TransmutationIndexError


def create_index(
    index_name: str,
    table_name: str,
    columns: Union[str, List[str]],
    engine: Engine,
    schema: Optional[str] = None,
    unique: bool = False,
    if_not_exists: bool = False
) -> Table:
    """
    Create an index on one or more columns.
    
    Args:
        index_name: Name of the index to create
        table_name: Name of the table
        columns: Column name or list of column names
        engine: SQLAlchemy Engine instance
        schema: Optional schema name
        unique: Whether to create a unique index (default: False)
        if_not_exists: Skip creation if index already exists (default: False)
        
    Returns:
        Newly reflected SQLAlchemy Table object
        
    Raises:
        IndexError: If the create operation fails
        ValidationError: If the table or columns don't exist
        
    Example:
        >>> from sqlalchemy import create_engine
        >>> engine = create_engine('sqlite:///test.db')
        >>> table = create_index('idx_email', 'users', 'email', engine, unique=True)
        >>> table = create_index('idx_name', 'users', ['last_name', 'first_name'], engine)
    """
    try:
        validate_table_exists(table_name, engine, schema)
        
        # Normalize columns to list
        if isinstance(columns, str):
            columns = [columns]
        
        # Validate all columns exist
        for col in columns:
            validate_column_exists(table_name, col, engine, schema)
        
        # Check if index already exists
        if if_not_exists and index_exists(index_name, table_name, engine, schema):
            return get_table(table_name, engine, schema=schema)
        
        op = _get_op(engine)
        op.create_index(
            index_name, 
            table_name, 
            columns, 
            unique=unique, 
            schema=schema
        )  # type: ignore
        
        return get_table(table_name, engine, schema=schema)
    except Exception as e:
        if hasattr(e, '__class__') and 'ValidationError' in e.__class__.__name__:
            raise
        raise TransmutationIndexError(
            f"Failed to create index '{index_name}': {str(e)}"
        ) from e


def drop_index(
    index_name: str,
    table_name: Optional[str] = None,
    engine: Optional[Engine] = None,
    schema: Optional[str] = None,
    if_exists: bool = False
) -> Optional[Table]:
    """
    Drop an index from a table.
    
    Args:
        index_name: Name of the index to drop
        table_name: Name of the table (required for some databases)
        engine: SQLAlchemy Engine instance
        schema: Optional schema name
        if_exists: Skip if index doesn't exist (default: False)
        
    Returns:
        Newly reflected SQLAlchemy Table object if table_name provided, else None
        
    Raises:
        IndexError: If the drop operation fails
        ValidationError: If the table doesn't exist
        
    Example:
        >>> from sqlalchemy import create_engine
        >>> engine = create_engine('sqlite:///test.db')
        >>> drop_index('idx_email', 'users', engine)
    """
    if engine is None:
        raise TransmutationIndexError("Engine is required for drop_index operation")
    
    try:
        if table_name:
            validate_table_exists(table_name, engine, schema)
            
            # Check if index exists
            if if_exists and not index_exists(index_name, table_name, engine, schema):
                return get_table(table_name, engine, schema=schema)
        
        op = _get_op(engine)
        op.drop_index(
            index_name, 
            table_name=table_name, 
            schema=schema
        )  # type: ignore
        
        if table_name:
            return get_table(table_name, engine, schema=schema)
        return None
    except Exception as e:
        if hasattr(e, '__class__') and 'ValidationError' in e.__class__.__name__:
            raise
        raise TransmutationIndexError(
            f"Failed to drop index '{index_name}': {str(e)}"
        ) from e


def create_unique_index(
    index_name: str,
    table_name: str,
    columns: Union[str, List[str]],
    engine: Engine,
    schema: Optional[str] = None,
    if_not_exists: bool = False
) -> Table:
    """
    Create a unique index on one or more columns.
    
    This is a convenience function that calls create_index with unique=True.
    
    Args:
        index_name: Name of the index to create
        table_name: Name of the table
        columns: Column name or list of column names
        engine: SQLAlchemy Engine instance
        schema: Optional schema name
        if_not_exists: Skip creation if index already exists (default: False)
        
    Returns:
        Newly reflected SQLAlchemy Table object
        
    Raises:
        IndexError: If the create operation fails
        ValidationError: If the table or columns don't exist
        
    Example:
        >>> from sqlalchemy import create_engine
        >>> engine = create_engine('sqlite:///test.db')
        >>> table = create_unique_index('idx_unique_email', 'users', 'email', engine)
    """
    return create_index(
        index_name=index_name,
        table_name=table_name,
        columns=columns,
        engine=engine,
        schema=schema,
        unique=True,
        if_not_exists=if_not_exists
    )

