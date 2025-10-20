"""Alteration classes for reversible database operations."""

from dataclasses import dataclass, field
from typing import Any, Optional, Protocol, List, Union

from sqlalchemy.engine import Engine
import sqlalchemy as sa
from fullmetalalchemy.features import get_column_types, get_table
from fullmetalalchemy.type_convert import _sql_to_python
from fullmetalalchemy.drop import drop_table

import transmutation as tm


class Alteration(Protocol):
    """Protocol for reversible database alterations."""
    
    def upgrade(self) -> sa.Table:
        """Apply the alteration (forward migration)."""
        ...

    def downgrade(self) -> sa.Table:
        """Reverse the alteration (backward migration)."""
        ...


# Column Alterations

@dataclass
class RenameColumn(Alteration):
    """Alteration to rename a column."""
    
    table_name: str
    old_col_name: str
    new_col_name: str
    engine: Engine
    schema: Optional[str] = None

    def upgrade(self) -> sa.Table:
        return tm.column.rename_column(
            self.table_name,
            self.old_col_name,
            self.new_col_name,
            self.engine,
            self.schema
        )

    def downgrade(self) -> sa.Table:
        return tm.column.rename_column(
            self.table_name,
            self.new_col_name,
            self.old_col_name,
            self.engine,
            self.schema
        )


@dataclass
class DropColumn(Alteration):
    """Alteration to drop a column (with backup for rollback)."""
    
    table_name: str
    col_name: str
    engine: Engine
    schema: Optional[str] = None
    dtype: Any = field(default=None, init=False)
    table_copy: Optional[sa.Table] = field(default=None, init=False)

    def upgrade(self) -> sa.Table:
        table = get_table(self.table_name, self.engine, self.schema)
        self.dtype = _sql_to_python[type(get_column_types(table)[self.col_name])]
        self.table_copy = tm.table.copy_table(
            table, 
            f'%copy%{self.table_name}', 
            self.engine, 
            schema=self.schema
        )
        return tm.column.drop_column(
            self.table_name,
            self.col_name,
            self.engine,
            self.schema
        )

    def downgrade(self) -> sa.Table:
        return tm.column.add_column(
            self.table_name,
            self.col_name,
            self.dtype,
            self.engine,
            self.schema
        )


@dataclass
class AddColumn(Alteration):
    """Alteration to add a column."""
    
    table_name: str
    column_name: str
    dtype: Any
    engine: Engine
    schema: Optional[str] = None
    nullable: bool = True
    default: Optional[Any] = None
    server_default: Optional[Any] = None

    def upgrade(self) -> sa.Table:
        return tm.column.add_column(
            self.table_name,
            self.column_name,
            self.dtype,
            self.engine,
            self.schema,
            self.nullable,
            self.default,
            self.server_default
        )

    def downgrade(self) -> sa.Table:
        return tm.column.drop_column(
            self.table_name,
            self.column_name,
            self.engine,
            self.schema
        )


@dataclass
class AlterColumn(Alteration):
    """Alteration to modify column properties."""
    
    table_name: str
    column_name: str
    engine: Engine
    schema: Optional[str] = None
    new_column_name: Optional[str] = None
    type_: Optional[Any] = None
    nullable: Optional[bool] = None
    default: Optional[Any] = None
    server_default: Optional[Any] = None
    # Store original values for rollback
    original_name: str = field(default="", init=False)
    original_type: Optional[Any] = field(default=None, init=False)
    original_nullable: Optional[bool] = field(default=None, init=False)

    def upgrade(self) -> sa.Table:
        # Store original values before alteration
        table = get_table(self.table_name, self.engine, self.schema)
        col = table.c[self.column_name]
        self.original_name = self.column_name
        self.original_type = type(col.type)
        self.original_nullable = col.nullable
        
        return tm.column.alter_column(
            self.table_name,
            self.column_name,
            self.engine,
            self.schema,
            self.new_column_name,
            self.type_,
            self.nullable,
            self.default,
            self.server_default
        )

    def downgrade(self) -> sa.Table:
        # Use the new name if column was renamed
        current_name = self.new_column_name if self.new_column_name else self.column_name
        
        return tm.column.alter_column(
            self.table_name,
            current_name,
            self.engine,
            self.schema,
            self.original_name if self.new_column_name else None,
            self.original_type,
            self.original_nullable
        )


# Table Alterations

@dataclass
class RenameTable(Alteration):
    """Alteration to rename a table."""
    
    old_table_name: str
    new_table_name: str
    engine: Engine
    schema: Optional[str] = None

    def upgrade(self) -> sa.Table:
        return tm.table.rename_table(
            self.old_table_name,
            self.new_table_name,
            self.engine,
            self.schema
        )

    def downgrade(self) -> sa.Table:
        return tm.table.rename_table(
            self.new_table_name,
            self.old_table_name,
            self.engine,
            self.schema
        )


@dataclass
class CopyTable(Alteration):
    """Alteration to copy a table."""
    
    table: sa.Table
    new_table_name: str
    engine: Engine
    if_exists: str = 'replace'
    schema: Optional[str] = None
    copy_data: bool = True

    def upgrade(self) -> sa.Table:
        table_copy = tm.table.copy_table(
            self.table,
            self.new_table_name,
            self.engine,
            self.if_exists,
            self.schema,
            self.copy_data
        )
        return table_copy

    def downgrade(self) -> sa.Table:
        drop_table(
            self.new_table_name,
            self.engine,
            schema=self.schema
        )
        return self.table


@dataclass
class CreateTable(Alteration):
    """Alteration to create a table."""
    
    table_name: str
    columns: List[sa.Column[Any]]
    engine: Engine
    schema: Optional[str] = None
    if_not_exists: bool = False

    def upgrade(self) -> sa.Table:
        return tm.table.create_table(
            self.table_name,
            self.columns,
            self.engine,
            self.schema,
            self.if_not_exists
        )

    def downgrade(self) -> sa.Table:
        tm.table.drop_table(
            self.table_name,
            self.engine,
            self.schema,
            if_exists=True
        )
        # Return a dummy table since it's been dropped
        return sa.Table(self.table_name, sa.MetaData())


@dataclass
class DropTable(Alteration):
    """Alteration to drop a table (with backup for rollback)."""
    
    table_name: str
    engine: Engine
    schema: Optional[str] = None
    cascade: bool = False
    backup_table: Optional[sa.Table] = field(default=None, init=False)
    backup_name: str = field(default="", init=False)

    def upgrade(self) -> sa.Table:
        # Create backup for potential rollback
        table = get_table(self.table_name, self.engine, self.schema)
        self.backup_name = f'%backup%{self.table_name}'
        self.backup_table = tm.table.copy_table(
            table,
            self.backup_name,
            self.engine,
            schema=self.schema
        )
        
        tm.table.drop_table(
            self.table_name,
            self.engine,
            self.schema,
            self.cascade
        )
        return sa.Table(self.table_name, sa.MetaData())

    def downgrade(self) -> sa.Table:
        if self.backup_table:
            # Restore from backup
            restored = tm.table.copy_table(
                self.backup_table,
                self.table_name,
                self.engine,
                schema=self.schema
            )
            # Clean up backup
            drop_table(self.backup_name, self.engine, schema=self.schema)
            return restored
        raise tm.exceptions.RollbackError("No backup available for table restoration")


# Index Alterations

@dataclass
class CreateIndex(Alteration):
    """Alteration to create an index."""
    
    index_name: str
    table_name: str
    columns: Union[str, List[str]]
    engine: Engine
    schema: Optional[str] = None
    unique: bool = False
    if_not_exists: bool = False

    def upgrade(self) -> sa.Table:
        return tm.index.create_index(
            self.index_name,
            self.table_name,
            self.columns,
            self.engine,
            self.schema,
            self.unique,
            self.if_not_exists
        )

    def downgrade(self) -> sa.Table:
        result = tm.index.drop_index(
            self.index_name,
            self.table_name,
            self.engine,
            self.schema,
            if_exists=True
        )
        # drop_index returns Optional[Table], ensure we return a Table
        if result is None:
            from fullmetalalchemy.features import get_table
            return get_table(self.table_name, self.engine, self.schema)
        return result


@dataclass
class DropIndex(Alteration):
    """Alteration to drop an index."""
    
    index_name: str
    table_name: str
    columns: Union[str, List[str]]
    engine: Engine
    schema: Optional[str] = None
    unique: bool = False

    def upgrade(self) -> sa.Table:
        result = tm.index.drop_index(
            self.index_name,
            self.table_name,
            self.engine,
            self.schema
        )
        # drop_index returns Optional[Table], ensure we return a Table
        if result is None:
            from fullmetalalchemy.features import get_table
            return get_table(self.table_name, self.engine, self.schema)
        return result

    def downgrade(self) -> sa.Table:
        return tm.index.create_index(
            self.index_name,
            self.table_name,
            self.columns,
            self.engine,
            self.schema,
            self.unique
        )


# Constraint Alterations

@dataclass
class CreateForeignKey(Alteration):
    """Alteration to create a foreign key constraint."""
    
    constraint_name: str
    source_table: str
    source_columns: Union[str, List[str]]
    referent_table: str
    referent_columns: Union[str, List[str]]
    engine: Engine
    schema: Optional[str] = None
    onupdate: Optional[str] = None
    ondelete: Optional[str] = None

    def upgrade(self) -> sa.Table:
        return tm.constraint.create_foreign_key(
            self.constraint_name,
            self.source_table,
            self.source_columns,
            self.referent_table,
            self.referent_columns,
            self.engine,
            self.schema,
            self.onupdate,
            self.ondelete
        )

    def downgrade(self) -> sa.Table:
        return tm.constraint.drop_constraint(
            self.constraint_name,
            self.source_table,
            self.engine,
            type_='foreignkey',
            schema=self.schema
        )


@dataclass
class DropConstraint(Alteration):
    """Alteration to drop a constraint."""
    
    constraint_name: str
    table_name: str
    engine: Engine
    type_: str = 'foreignkey'
    schema: Optional[str] = None
    # Note: Downgrade would require storing constraint details, which is complex
    # Users should use specific constraint alterations for reversible operations

    def upgrade(self) -> sa.Table:
        return tm.constraint.drop_constraint(
            self.constraint_name,
            self.table_name,
            self.engine,
            self.type_,
            self.schema
        )

    def downgrade(self) -> sa.Table:
        raise NotImplementedError(
            "Cannot automatically reverse DropConstraint. "
            "Use specific constraint creation alterations for reversible operations."
        )


@dataclass
class CreateUniqueConstraint(Alteration):
    """Alteration to create a unique constraint."""
    
    constraint_name: str
    table_name: str
    columns: Union[str, List[str]]
    engine: Engine
    schema: Optional[str] = None

    def upgrade(self) -> sa.Table:
        return tm.constraint.create_unique_constraint(
            self.constraint_name,
            self.table_name,
            self.columns,
            self.engine,
            self.schema
        )

    def downgrade(self) -> sa.Table:
        return tm.constraint.drop_constraint(
            self.constraint_name,
            self.table_name,
            self.engine,
            type_='unique',
            schema=self.schema
        )


@dataclass
class CreateCheckConstraint(Alteration):
    """Alteration to create a check constraint."""
    
    constraint_name: str
    table_name: str
    condition: str
    engine: Engine
    schema: Optional[str] = None

    def upgrade(self) -> sa.Table:
        return tm.constraint.create_check_constraint(
            self.constraint_name,
            self.table_name,
            self.condition,
            self.engine,
            self.schema
        )

    def downgrade(self) -> sa.Table:
        return tm.constraint.drop_constraint(
            self.constraint_name,
            self.table_name,
            self.engine,
            type_='check',
            schema=self.schema
        )
