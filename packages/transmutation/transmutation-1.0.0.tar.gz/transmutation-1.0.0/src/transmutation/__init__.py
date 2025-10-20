"""
Transmutation - Database migration and schema alteration tool.

A comprehensive library for database schema modifications using SQLAlchemy and Alembic.
Provides both direct operations and a migration system with rollback capabilities.
"""

__version__ = '1.0.0'

# Submodules
from transmutation import (
    column,
    table,
    index,
    constraint,
    exceptions,
    utils,
    migration,
    alteration,
    update,
)

# Column Operations
from transmutation.column import (
    rename_column,
    drop_column,
    add_column,
    alter_column,
)

# Table Operations
from transmutation.table import (
    rename_table,
    create_table,
    drop_table,
    copy_table,
    truncate_table,
    create_table_as,
)

# Index Operations
from transmutation.index import (
    create_index,
    drop_index,
    create_unique_index,
)

# Constraint Operations
from transmutation.constraint import (
    create_foreign_key,
    drop_constraint,
    create_unique_constraint,
    create_check_constraint,
    create_primary_key,
    create_primary_keys,
    replace_primary_key,
    replace_primary_keys,
)

# Update Operations
from transmutation.update import (
    set_column_values_session,
    set_column_values,
)

# Migration System
from transmutation.migration import Migration

# Exceptions
from transmutation.exceptions import (
    TransmutationError,
    MigrationError,
    ColumnError,
    TableError,
    ConstraintError,
    IndexError,
    ValidationError,
    RollbackError,
    ForceFail,
)

# Alteration Classes (for advanced usage)
from transmutation.alteration import (
    Alteration,
    RenameColumn as RenameColumnAlteration,
    DropColumn as DropColumnAlteration,
    AddColumn as AddColumnAlteration,
    AlterColumn as AlterColumnAlteration,
    RenameTable as RenameTableAlteration,
    CreateTable as CreateTableAlteration,
    DropTable as DropTableAlteration,
    CopyTable as CopyTableAlteration,
    CreateIndex as CreateIndexAlteration,
    DropIndex as DropIndexAlteration,
    CreateForeignKey as CreateForeignKeyAlteration,
    CreateUniqueConstraint as CreateUniqueConstraintAlteration,
    CreateCheckConstraint as CreateCheckConstraintAlteration,
    DropConstraint as DropConstraintAlteration,
)

__all__ = [
    # Version
    '__version__',
    
    # Submodules
    'column',
    'table',
    'index',
    'constraint',
    'exceptions',
    'utils',
    'migration',
    'alteration',
    'update',
    
    # Column Operations
    'rename_column',
    'drop_column',
    'add_column',
    'alter_column',
    
    # Table Operations
    'rename_table',
    'create_table',
    'drop_table',
    'copy_table',
    'truncate_table',
    'create_table_as',
    
    # Index Operations
    'create_index',
    'drop_index',
    'create_unique_index',
    
    # Constraint Operations
    'create_foreign_key',
    'drop_constraint',
    'create_unique_constraint',
    'create_check_constraint',
    'create_primary_key',
    'create_primary_keys',
    'replace_primary_key',
    'replace_primary_keys',
    
    # Update Operations
    'set_column_values_session',
    'set_column_values',
    
    # Migration System
    'Migration',
    
    # Exceptions
    'TransmutationError',
    'MigrationError',
    'ColumnError',
    'TableError',
    'ConstraintError',
    'IndexError',
    'ValidationError',
    'RollbackError',
    'ForceFail',
    
    # Alteration Classes
    'Alteration',
    'RenameColumnAlteration',
    'DropColumnAlteration',
    'AddColumnAlteration',
    'AlterColumnAlteration',
    'RenameTableAlteration',
    'CreateTableAlteration',
    'DropTableAlteration',
    'CopyTableAlteration',
    'CreateIndexAlteration',
    'DropIndexAlteration',
    'CreateForeignKeyAlteration',
    'CreateUniqueConstraintAlteration',
    'CreateCheckConstraintAlteration',
    'DropConstraintAlteration',
]
