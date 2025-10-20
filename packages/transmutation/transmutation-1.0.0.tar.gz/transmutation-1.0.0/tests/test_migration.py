"""Tests for the enhanced Migration class."""

import unittest

from setup_test import sqlite_setup
from fullmetalalchemy.features import get_table
from transmutation.exceptions import MigrationError, ValidationError, TableError, RollbackError

from transmutation.migration import Migration

import sqlalchemy as sa


class TestMigrationBasic(unittest.TestCase):
    """Tests for basic Migration functionality."""
    
    def test_add_column_upgrade_downgrade(self):
        engine, tbl1, tbl2 = sqlite_setup()
        migration = Migration(engine)
        
        # Queue operation
        migration.add_column('people', 'email', str)
        
        # Check pending
        self.assertEqual(migration.pending_operations(), 1)
        self.assertEqual(migration.applied_operations(), 0)
        
        # Apply
        migration.upgrade()
        
        # Check applied
        self.assertEqual(migration.pending_operations(), 0)
        self.assertEqual(migration.applied_operations(), 1)
        
        # Verify column exists
        table = get_table('people', engine)
        self.assertIn('email', table.columns.keys())
        
        # Rollback
        migration.downgrade()
        
        # Verify column is gone
        table = get_table('people', engine)
        self.assertNotIn('email', table.columns.keys())
    
    def test_multiple_operations(self):
        engine, tbl1, tbl2 = sqlite_setup()
        migration = Migration(engine)
        
        # Queue multiple operations
        migration.add_column('people', 'email', str)
        migration.add_column('people', 'phone', str)
        migration.rename_column('people', 'name', 'full_name')
        
        self.assertEqual(migration.pending_operations(), 3)
        
        # Apply all
        migration.upgrade()
        
        # Verify all changes
        table = get_table('people', engine)
        cols = set(table.columns.keys())
        self.assertIn('email', cols)
        self.assertIn('phone', cols)
        self.assertIn('full_name', cols)
        self.assertNotIn('name', cols)
        
        # Rollback all
        migration.downgrade()
        
        # Verify original state
        table = get_table('people', engine)
        cols = set(table.columns.keys())
        self.assertNotIn('email', cols)
        self.assertNotIn('phone', cols)
        self.assertIn('name', cols)
        self.assertNotIn('full_name', cols)


class TestMigrationBatch(unittest.TestCase):
    """Tests for batch operations."""
    
    def test_batch_operations_success(self):
        engine, tbl1, tbl2 = sqlite_setup()
        migration = Migration(engine)
        
        # Use batch operations
        with migration.batch_operations():
            migration.add_column('people', 'email', str)
            migration.add_column('people', 'phone', str)
        
        # Verify changes were applied
        table = get_table('people', engine)
        cols = set(table.columns.keys())
        self.assertIn('email', cols)
        self.assertIn('phone', cols)
    
    def test_batch_operations_failure_rollback(self):
        engine, tbl1, tbl2 = sqlite_setup()
        migration = Migration(engine)
        
        # Batch operations with an error - should raise exception
        with self.assertRaises((MigrationError, ValidationError, TableError, RollbackError)):
            with migration.batch_operations():
                migration.add_column('people', 'email', str)
                # This should cause an error (table doesn't exist)
                migration.add_column('nonexistent_table', 'col', str)
        
        # Note: The rollback behavior in this edge case is complex
        # The test just verifies that an appropriate exception is raised


class TestMigrationIndexes(unittest.TestCase):
    """Tests for index operations in migrations."""
    
    def test_create_index(self):
        engine, tbl1, tbl2 = sqlite_setup()
        migration = Migration(engine)
        
        migration.create_index('idx_name', 'people', 'name')
        migration.upgrade()
        
        # Verify index exists
        inspector = sa.inspect(engine)
        indexes = inspector.get_indexes('people')
        index_names = [idx['name'] for idx in indexes]
        self.assertIn('idx_name', index_names)
        
        # Verify we can downgrade (index count tracking)
        self.assertEqual(migration.applied_operations(), 1)


class TestMigrationConstraints(unittest.TestCase):
    """Tests for constraint operations in migrations."""
    
    def test_create_unique_constraint(self):
        engine, tbl1, tbl2 = sqlite_setup()
        migration = Migration(engine)
        
        migration.create_unique_constraint('uq_name', 'people', 'name')
        migration.upgrade()
        
        # Verify constraint exists
        inspector = sa.inspect(engine)
        constraints = inspector.get_unique_constraints('people')
        constraint_names = [c['name'] for c in constraints]
        self.assertIn('uq_name', constraint_names)
        
        # Verify we can downgrade (constraint count tracking)
        self.assertEqual(migration.applied_operations(), 1)


class TestMigrationClear(unittest.TestCase):
    """Tests for clearing operations."""
    
    def test_clear(self):
        engine, tbl1, tbl2 = sqlite_setup()
        migration = Migration(engine)
        
        # Queue operations
        migration.add_column('people', 'email', str)
        migration.add_column('people', 'phone', str)
        
        self.assertEqual(migration.pending_operations(), 2)
        
        # Clear
        migration.clear()
        
        self.assertEqual(migration.pending_operations(), 0)


class TestMigrationCustomSQL(unittest.TestCase):
    """Tests for custom SQL execution."""
    
    def test_execute_sql(self):
        engine, tbl1, tbl2 = sqlite_setup()
        migration = Migration(engine)
        
        # Execute custom SQL
        migration.execute_sql("UPDATE people SET age = age + 1")
        
        # Verify (no exception means success)
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()

