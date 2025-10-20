"""Column operations for database schema modifications."""

from typing import Any, Optional, Union

from sqlalchemy import Table, Column
from sqlalchemy.engine import Engine
from sqlalchemy.types import TypeEngine

from fullmetalalchemy.features import get_table
from fullmetalalchemy.type_convert import sql_type

from transmutation.utils import _get_op, validate_table_exists, validate_column_exists
from transmutation.exceptions import ColumnError


def rename_column(
    table_name: str,
    old_col_name: str,
    new_col_name: str,
    engine: Engine,
    schema: Optional[str] = None
) -> Table:
    """
    Rename a table column.
    
    Args:
        table_name: Name of the table containing the column
        old_col_name: Current name of the column
        new_col_name: New name for the column
        engine: SQLAlchemy Engine instance
        schema: Optional schema name
        
    Returns:
        Newly reflected SQLAlchemy Table object
        
    Raises:
        ColumnError: If the rename operation fails
        ValidationError: If the table or column doesn't exist
        
    Example:
        >>> from sqlalchemy import create_engine
        >>> engine = create_engine('sqlite:///test.db')
        >>> table = rename_column('users', 'name', 'full_name', engine)
    """
    try:
        validate_table_exists(table_name, engine, schema)
        validate_column_exists(table_name, old_col_name, engine, schema)
        
        op = _get_op(engine)
        
        with op.batch_alter_table(table_name, schema=schema) as batch_op:
            batch_op.alter_column(
                old_col_name, 
                nullable=True, 
                new_column_name=new_col_name
            )  # type: ignore
            
        return get_table(table_name, engine, schema=schema)
    except Exception as e:
        if hasattr(e, '__class__') and 'ValidationError' in e.__class__.__name__:
            raise
        raise ColumnError(f"Failed to rename column '{old_col_name}': {str(e)}") from e


def drop_column(
    table_name: str,
    col_name: str,
    engine: Engine,
    schema: Optional[str] = None
) -> Table:
    """
    Drop a column from a table.
    
    Args:
        table_name: Name of the table
        col_name: Name of the column to drop
        engine: SQLAlchemy Engine instance
        schema: Optional schema name
        
    Returns:
        Newly reflected SQLAlchemy Table object
        
    Raises:
        ColumnError: If the drop operation fails
        ValidationError: If the table or column doesn't exist
        
    Example:
        >>> from sqlalchemy import create_engine
        >>> engine = create_engine('sqlite:///test.db')
        >>> table = drop_column('users', 'middle_name', engine)
    """
    try:
        validate_table_exists(table_name, engine, schema)
        validate_column_exists(table_name, col_name, engine, schema)
        
        op = _get_op(engine)
        
        with op.batch_alter_table(table_name, schema=schema) as batch_op:
            batch_op.drop_column(col_name)  # type: ignore
            
        return get_table(table_name, engine, schema=schema)
    except Exception as e:
        if hasattr(e, '__class__') and 'ValidationError' in e.__class__.__name__:
            raise
        raise ColumnError(f"Failed to drop column '{col_name}': {str(e)}") from e


def add_column(
    table_name: str,
    column_name: str,
    dtype: Any,
    engine: Engine,
    schema: Optional[str] = None,
    nullable: bool = True,
    default: Optional[Any] = None,
    server_default: Optional[Any] = None
) -> Table:
    """
    Add a column to a table.
    
    Args:
        table_name: Name of the table
        column_name: Name of the new column
        dtype: Data type for the column (Python type or SQLAlchemy type)
        engine: SQLAlchemy Engine instance
        schema: Optional schema name
        nullable: Whether the column allows NULL values (default: True)
        default: Python-side default value
        server_default: Server-side default value
        
    Returns:
        Newly reflected SQLAlchemy Table object
        
    Raises:
        ColumnError: If the add operation fails
        ValidationError: If the table doesn't exist
        
    Example:
        >>> from sqlalchemy import create_engine
        >>> engine = create_engine('sqlite:///test.db')
        >>> table = add_column('users', 'email', str, engine, nullable=False)
    """
    try:
        validate_table_exists(table_name, engine, schema)
        
        sa_type = sql_type(dtype)
        op = _get_op(engine)
        
        col: Column[Any] = Column(
            column_name, 
            sa_type,
            nullable=nullable,
            default=default,
            server_default=server_default
        )
        
        op.add_column(table_name, col, schema=schema)  # type: ignore
        
        return get_table(table_name, engine, schema=schema)
    except Exception as e:
        if hasattr(e, '__class__') and 'ValidationError' in e.__class__.__name__:
            raise
        raise ColumnError(f"Failed to add column '{column_name}': {str(e)}") from e


def alter_column(
    table_name: str,
    column_name: str,
    engine: Engine,
    schema: Optional[str] = None,
    new_column_name: Optional[str] = None,
    type_: Optional[Union[type, TypeEngine[Any]]] = None,
    nullable: Optional[bool] = None,
    default: Optional[Any] = None,
    server_default: Optional[Any] = None,
    comment: Optional[str] = None
) -> Table:
    """
    Alter various properties of a column.
    
    Args:
        table_name: Name of the table
        column_name: Name of the column to alter
        engine: SQLAlchemy Engine instance
        schema: Optional schema name
        new_column_name: New name for the column (if renaming)
        type_: New data type for the column
        nullable: New nullable setting
        default: New Python-side default value
        server_default: New server-side default value
        comment: New column comment
        
    Returns:
        Newly reflected SQLAlchemy Table object
        
    Raises:
        ColumnError: If the alter operation fails
        ValidationError: If the table or column doesn't exist
        
    Example:
        >>> from sqlalchemy import create_engine
        >>> engine = create_engine('sqlite:///test.db')
        >>> table = alter_column('users', 'age', engine, nullable=False, default=0)
    """
    try:
        validate_table_exists(table_name, engine, schema)
        validate_column_exists(table_name, column_name, engine, schema)
        
        op = _get_op(engine)
        
        # Convert Python type to SQLAlchemy type if needed
        converted_type: Optional[TypeEngine[Any]] = None
        if type_ is not None and not isinstance(type_, TypeEngine):
            converted_type = sql_type(type_)
        elif type_ is not None:
            converted_type = type_  # type: ignore
        
        with op.batch_alter_table(table_name, schema=schema) as batch_op:
            batch_op.alter_column(
                column_name,
                new_column_name=new_column_name,
                type_=converted_type,
                nullable=nullable,
                server_default=server_default,
                comment=comment
            )  # type: ignore
            
        return get_table(table_name, engine, schema=schema)
    except Exception as e:
        if hasattr(e, '__class__') and 'ValidationError' in e.__class__.__name__:
            raise
        raise ColumnError(f"Failed to alter column '{column_name}': {str(e)}") from e

