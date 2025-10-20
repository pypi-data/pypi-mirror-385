"""Custom exceptions for transmutation operations."""


class TransmutationError(Exception):
    """Base exception for all transmutation errors."""
    
    pass


class MigrationError(TransmutationError):
    """Raised when a migration operation fails."""
    
    pass


class ColumnError(TransmutationError):
    """Raised when a column operation fails."""
    
    pass


class TableError(TransmutationError):
    """Raised when a table operation fails."""
    
    pass


class ConstraintError(TransmutationError):
    """Raised when a constraint operation fails."""
    
    pass


class IndexError(TransmutationError):
    """Raised when an index operation fails."""
    
    pass


class ValidationError(TransmutationError):
    """Raised when validation of parameters fails."""
    
    pass


class RollbackError(TransmutationError):
    """Raised when a rollback operation fails."""
    
    pass


class ForceFail(TransmutationError):
    """Legacy exception for forced failures."""
    
    pass
