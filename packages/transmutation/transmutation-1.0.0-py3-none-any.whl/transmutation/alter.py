"""
Legacy module for backward compatibility.

This module re-exports functions from the new modular structure.
For new code, prefer importing from specific modules:
- transmutation.column
- transmutation.table
- transmutation.constraint
"""

from typing import Optional

from sqlalchemy import Table
from sqlalchemy.engine import Engine

# Import from new modular structure
from transmutation.column import (
    rename_column,
    drop_column,
    add_column,
    alter_column
)
from transmutation.table import (
    rename_table,
    copy_table
)
from transmutation.constraint import (
    create_primary_key,
    create_primary_keys,
    replace_primary_key,
    replace_primary_keys
)
from transmutation.utils import _get_op

# Re-export for backward compatibility
__all__ = [
    'rename_column',
    'drop_column',
    'add_column',
    'alter_column',
    'rename_table',
    'copy_table',
    'create_primary_key',
    'create_primary_keys',
    'replace_primary_key',
    'replace_primary_keys',
    '_get_op',
    'name_primary_key',
]


def name_primary_key(
    table_name: str,
    column_name: str,
    engine: Engine,
    schema: Optional[str] = None
) -> Table:
    """
    Legacy function: Names the primary key constraint for a given sql table column.
    
    This is now equivalent to create_primary_key.
    
    Args:
        table_name: Name of the table
        column_name: Name of the column
        engine: SQLAlchemy Engine instance
        schema: Optional schema name
        
    Returns:
        Newly reflected SQLAlchemy Table object
    """
    return create_primary_key(table_name, column_name, engine, schema=schema)
