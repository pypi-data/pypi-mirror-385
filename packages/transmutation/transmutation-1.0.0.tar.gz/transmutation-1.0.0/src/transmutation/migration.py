"""Enhanced migration system for managing reversible database operations."""

from typing import Any, Optional, Protocol, List, Union
from contextlib import contextmanager

from sqlalchemy.engine import Engine
from sqlalchemy import Column, text
import sqlalchemy as sa
from alembic.operations import Operations

from transmutation.utils import _get_op
from transmutation.alteration import (
    AddColumn,
    AlterColumn,
    CopyTable,
    CreateCheckConstraint,
    CreateForeignKey,
    CreateIndex,
    CreateTable,
    CreateUniqueConstraint,
    DropColumn,
    DropIndex,
    DropTable,
    RenameColumn,
    RenameTable,
)
from transmutation.exceptions import MigrationError, RollbackError


class Alteration(Protocol):
    """Protocol for reversible database alterations."""
    
    def upgrade(self) -> sa.Table:
        """Apply the alteration (forward migration)."""
        ...

    def downgrade(self) -> sa.Table:
        """Reverse the alteration (backward migration)."""
        ...


class Migration:
    """
    Manage database schema alterations with rollback capability.
    
    This class tracks alterations and allows rolling back changes
    if something goes wrong during migration.
    
    Example:
        >>> from sqlalchemy import create_engine
        >>> engine = create_engine('sqlite:///test.db')
        >>> migration = Migration(engine)
        >>> migration.add_column('users', 'email', str)
        >>> migration.create_index('idx_email', 'users', 'email', unique=True)
        >>> migration.upgrade()  # Apply all changes
        >>> # If something went wrong:
        >>> migration.downgrade()  # Roll back all changes
    """
    
    def __init__(self, engine: Engine, auto_transaction: bool = True) -> None:
        """
        Initialize a Migration instance.
        
        Args:
            engine: SQLAlchemy Engine instance
            auto_transaction: Enable automatic transaction management (default: True)
        """
        self._engine = engine
        self._auto_transaction = auto_transaction
        self._upgrades: List[Alteration] = []
        self._downgrades: List[Alteration] = []

    @property
    def _op(self) -> Operations:
        """Get Alembic Operations instance."""
        return _get_op(self._engine)

    def _add_upgrade(self, alteration: Alteration) -> None:
        """Add an alteration to the upgrade queue."""
        self._upgrades.append(alteration)

    def _add_downgrade(self, alteration: Alteration) -> None:
        """Add an alteration to the downgrade queue."""
        self._downgrades.append(alteration)

    @contextmanager
    def batch_operations(self):
        """
        Context manager for batch operations with automatic rollback on error.
        
        Example:
            >>> migration = Migration(engine)
            >>> with migration.batch_operations():
            ...     migration.add_column('users', 'email', str)
            ...     migration.create_index('idx_email', 'users', 'email')
            >>> # Changes are automatically applied on exit
        """
        try:
            yield self
            self.upgrade()
        except Exception as e:
            try:
                self.downgrade()
            except Exception as rollback_error:
                raise RollbackError(
                    f"Failed to rollback after error: {str(rollback_error)}"
                ) from e
            raise MigrationError(f"Migration failed: {str(e)}") from e

    def upgrade(self) -> Optional[sa.Table]:
        """
        Apply all queued alterations in order.
        
        Returns:
            The last modified table, or None if no alterations
            
        Raises:
            MigrationError: If any alteration fails
        """
        table = None
        executed = []
        
        try:
            for alteration in self._upgrades:
                table = alteration.upgrade()
                executed.append(alteration)
                self._add_downgrade(alteration)
            
            # Clear upgrades after successful execution
            self._upgrades.clear()
            return table
            
        except Exception as e:
            # Attempt automatic rollback if enabled
            if self._auto_transaction and executed:
                try:
                    for alt in reversed(executed):
                        alt.downgrade()
                except Exception as rollback_error:
                    raise RollbackError(
                        f"Migration failed and rollback failed: {str(rollback_error)}"
                    ) from e
            raise MigrationError(f"Migration upgrade failed: {str(e)}") from e

    def downgrade(self) -> Optional[sa.Table]:
        """
        Reverse all applied alterations in reverse order.
        
        Returns:
            The last modified table, or None if no alterations
            
        Raises:
            RollbackError: If any downgrade operation fails
        """
        table = None
        
        try:
            for alteration in reversed(self._downgrades):
                table = alteration.downgrade()
            
            # Clear downgrades after successful execution
            self._downgrades.clear()
            return table
            
        except Exception as e:
            raise RollbackError(f"Migration downgrade failed: {str(e)}") from e

    # Column Operations

    def rename_column(
        self,
        table_name: str,
        old_col_name: str,
        new_col_name: str,
        schema: Optional[str] = None
    ) -> None:
        """Queue a column rename operation."""
        alteration = RenameColumn(
            table_name, old_col_name, new_col_name, self._engine, schema
        )
        self._add_upgrade(alteration)

    def drop_column(
        self,
        table_name: str,
        col_name: str,
        schema: Optional[str] = None
    ) -> None:
        """Queue a column drop operation."""
        alteration = DropColumn(table_name, col_name, self._engine, schema)
        self._add_upgrade(alteration)

    def add_column(
        self,
        table_name: str,
        column_name: str,
        dtype: Any,
        schema: Optional[str] = None,
        nullable: bool = True,
        default: Optional[Any] = None,
        server_default: Optional[Any] = None
    ) -> None:
        """Queue a column add operation."""
        alteration = AddColumn(
            table_name, column_name, dtype, self._engine, 
            schema, nullable, default, server_default
        )
        self._add_upgrade(alteration)

    def alter_column(
        self,
        table_name: str,
        column_name: str,
        schema: Optional[str] = None,
        new_column_name: Optional[str] = None,
        type_: Optional[Any] = None,
        nullable: Optional[bool] = None,
        default: Optional[Any] = None,
        server_default: Optional[Any] = None
    ) -> None:
        """Queue a column alteration operation."""
        alteration = AlterColumn(
            table_name, column_name, self._engine, schema,
            new_column_name, type_, nullable, default, server_default
        )
        self._add_upgrade(alteration)

    # Table Operations

    def rename_table(
        self,
        old_table_name: str,
        new_table_name: str,
        schema: Optional[str] = None
    ) -> None:
        """Queue a table rename operation."""
        alteration = RenameTable(
            old_table_name, new_table_name, self._engine, schema
        )
        self._add_upgrade(alteration)

    def copy_table(
        self,
        table: sa.Table,
        new_table_name: str,
        if_exists: str = 'replace',
        schema: Optional[str] = None,
        copy_data: bool = True
    ) -> None:
        """Queue a table copy operation."""
        alteration = CopyTable(
            table, new_table_name, self._engine, if_exists, schema, copy_data
        )
        self._add_upgrade(alteration)

    def create_table(
        self,
        table_name: str,
        columns: List[Column[Any]],
        schema: Optional[str] = None,
        if_not_exists: bool = False
    ) -> None:
        """Queue a table creation operation."""
        alteration = CreateTable(
            table_name, columns, self._engine, schema, if_not_exists
        )
        self._add_upgrade(alteration)

    def drop_table(
        self,
        table_name: str,
        schema: Optional[str] = None,
        cascade: bool = False
    ) -> None:
        """Queue a table drop operation."""
        alteration = DropTable(table_name, self._engine, schema, cascade)
        self._add_upgrade(alteration)

    # Index Operations

    def create_index(
        self,
        index_name: str,
        table_name: str,
        columns: Union[str, List[str]],
        schema: Optional[str] = None,
        unique: bool = False,
        if_not_exists: bool = False
    ) -> None:
        """Queue an index creation operation."""
        alteration = CreateIndex(
            index_name, table_name, columns, self._engine,
            schema, unique, if_not_exists
        )
        self._add_upgrade(alteration)

    def drop_index(
        self,
        index_name: str,
        table_name: str,
        columns: Union[str, List[str]],
        schema: Optional[str] = None,
        unique: bool = False
    ) -> None:
        """Queue an index drop operation."""
        alteration = DropIndex(
            index_name, table_name, columns, self._engine, schema, unique
        )
        self._add_upgrade(alteration)

    def create_unique_index(
        self,
        index_name: str,
        table_name: str,
        columns: Union[str, List[str]],
        schema: Optional[str] = None,
        if_not_exists: bool = False
    ) -> None:
        """Queue a unique index creation operation."""
        self.create_index(
            index_name, table_name, columns, schema, 
            unique=True, if_not_exists=if_not_exists
        )

    # Constraint Operations

    def create_foreign_key(
        self,
        constraint_name: str,
        source_table: str,
        source_columns: Union[str, List[str]],
        referent_table: str,
        referent_columns: Union[str, List[str]],
        schema: Optional[str] = None,
        onupdate: Optional[str] = None,
        ondelete: Optional[str] = None
    ) -> None:
        """Queue a foreign key creation operation."""
        alteration = CreateForeignKey(
            constraint_name, source_table, source_columns,
            referent_table, referent_columns, self._engine,
            schema, onupdate, ondelete
        )
        self._add_upgrade(alteration)

    def create_unique_constraint(
        self,
        constraint_name: str,
        table_name: str,
        columns: Union[str, List[str]],
        schema: Optional[str] = None
    ) -> None:
        """Queue a unique constraint creation operation."""
        alteration = CreateUniqueConstraint(
            constraint_name, table_name, columns, self._engine, schema
        )
        self._add_upgrade(alteration)

    def create_check_constraint(
        self,
        constraint_name: str,
        table_name: str,
        condition: str,
        schema: Optional[str] = None
    ) -> None:
        """Queue a check constraint creation operation."""
        alteration = CreateCheckConstraint(
            constraint_name, table_name, condition, self._engine, schema
        )
        self._add_upgrade(alteration)

    # Utility Operations

    def execute_sql(
        self,
        sql: str,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute custom SQL directly.
        
        Note: Custom SQL is not reversible and won't be tracked for rollback.
        
        Args:
            sql: SQL statement to execute
            *args: Positional arguments for the SQL
            **kwargs: Keyword arguments for the SQL
            
        Returns:
            Result of the SQL execution
            
        Example:
            >>> migration = Migration(engine)
            >>> migration.execute_sql("UPDATE users SET active = 1 WHERE status = 'verified'")
        """
        with self._engine.begin() as conn:
            return conn.execute(text(sql), *args, **kwargs)

    def clear(self) -> None:
        """Clear all queued operations."""
        self._upgrades.clear()
        self._downgrades.clear()

    def pending_operations(self) -> int:
        """Get the number of pending upgrade operations."""
        return len(self._upgrades)

    def applied_operations(self) -> int:
        """Get the number of applied operations (available for downgrade)."""
        return len(self._downgrades)
