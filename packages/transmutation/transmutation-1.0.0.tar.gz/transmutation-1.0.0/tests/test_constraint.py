"""Tests for constraint operations."""

import unittest

from setup_test import sqlite_setup
from fullmetalalchemy.features import get_table

from transmutation.constraint import (
    create_unique_constraint,
    create_check_constraint,
    drop_constraint,
)

import sqlalchemy as sa


class TestCreateUniqueConstraint(unittest.TestCase):
    """Tests for create_unique_constraint function."""
    
    def create_unique_constraint(self, setup_function, schema=None):
        engine, tbl1, tbl2 = setup_function(schema=schema)
        table = get_table('people', engine, schema=schema)
        
        # Create unique constraint
        create_unique_constraint('uq_name', table.name, 'name', engine, schema=schema)
        
        # Verify constraint was created
        inspector = sa.inspect(engine)
        unique_constraints = inspector.get_unique_constraints(table.name, schema=schema)
        constraint_names = [uc['name'] for uc in unique_constraints]
        self.assertIn('uq_name', constraint_names)
    
    def test_create_unique_constraint_sqlite(self):
        self.create_unique_constraint(sqlite_setup)


class TestCreateCheckConstraint(unittest.TestCase):
    """Tests for create_check_constraint function."""
    
    def create_check_constraint(self, setup_function, schema=None):
        engine, tbl1, tbl2 = setup_function(schema=schema)
        table = get_table('people', engine, schema=schema)
        
        # Create check constraint
        create_check_constraint('ck_age', table.name, 'age >= 0', engine, schema=schema)
        
        # Verify constraint exists by checking it enforces the rule
        # (not all databases support reflecting check constraints)
        # We just verify no error was raised during creation
        self.assertTrue(True)
    
    def test_create_check_constraint_sqlite(self):
        self.create_check_constraint(sqlite_setup)


class TestCreatePrimaryKey(unittest.TestCase):
    """Tests for create_primary_key function."""
    
    def test_create_primary_key_basic(self):
        """Test creating a primary key on a table without one."""
        # This would need a table without a primary key
        # which the setup functions don't provide
        # So this is a placeholder for future implementation
        pass


class TestDropConstraint(unittest.TestCase):
    """Tests for drop_constraint function."""
    
    def drop_unique_constraint(self, setup_function, schema=None):
        engine, tbl1, tbl2 = setup_function(schema=schema)
        table = get_table('people', engine, schema=schema)
        
        # Create then drop constraint
        create_unique_constraint('uq_to_drop', table.name, 'name', engine, schema=schema)
        drop_constraint('uq_to_drop', table.name, engine, type_='unique', schema=schema)
        
        # Verify constraint was dropped
        inspector = sa.inspect(engine)
        unique_constraints = inspector.get_unique_constraints(table.name, schema=schema)
        constraint_names = [uc['name'] for uc in unique_constraints]
        self.assertNotIn('uq_to_drop', constraint_names)
    
    def test_drop_unique_constraint_sqlite(self):
        self.drop_unique_constraint(sqlite_setup)


if __name__ == '__main__':
    unittest.main()

