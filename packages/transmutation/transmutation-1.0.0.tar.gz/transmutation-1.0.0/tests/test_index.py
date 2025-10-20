"""Tests for index operations."""

import unittest

from setup_test import sqlite_setup
from fullmetalalchemy.features import get_table

from transmutation.index import create_index, drop_index, create_unique_index

import sqlalchemy as sa


class TestCreateIndex(unittest.TestCase):
    """Tests for create_index function."""
    
    def create_index(self, setup_function, schema=None):
        engine, tbl1, tbl2 = setup_function(schema=schema)
        table = get_table('people', engine, schema=schema)
        
        # Create index on single column
        create_index('idx_name', table.name, 'name', engine, schema=schema)
        
        # Verify index was created
        inspector = sa.inspect(engine)
        indexes = inspector.get_indexes(table.name, schema=schema)
        index_names = [idx['name'] for idx in indexes]
        self.assertIn('idx_name', index_names)
    
    def test_create_index_sqlite(self):
        self.create_index(sqlite_setup)
    
    def create_composite_index(self, setup_function, schema=None):
        engine, tbl1, tbl2 = setup_function(schema=schema)
        table = get_table('people', engine, schema=schema)
        
        # Create composite index
        create_index('idx_name_age', table.name, ['name', 'age'], engine, schema=schema)
        
        # Verify index was created
        inspector = sa.inspect(engine)
        indexes = inspector.get_indexes(table.name, schema=schema)
        index_names = [idx['name'] for idx in indexes]
        self.assertIn('idx_name_age', index_names)
    
    def test_create_composite_index_sqlite(self):
        self.create_composite_index(sqlite_setup)


class TestCreateUniqueIndex(unittest.TestCase):
    """Tests for create_unique_index function."""
    
    def create_unique_index(self, setup_function, schema=None):
        engine, tbl1, tbl2 = setup_function(schema=schema)
        table = get_table('people', engine, schema=schema)
        
        # Create unique index
        create_unique_index('idx_unique_name', table.name, 'name', engine, schema=schema)
        
        # Verify unique index was created
        inspector = sa.inspect(engine)
        indexes = inspector.get_indexes(table.name, schema=schema)
        for idx in indexes:
            if idx['name'] == 'idx_unique_name':
                self.assertTrue(idx['unique'])
                break
        else:
            self.fail("Unique index not found")
    
    def test_create_unique_index_sqlite(self):
        self.create_unique_index(sqlite_setup)


class TestDropIndex(unittest.TestCase):
    """Tests for drop_index function."""
    
    def drop_index(self, setup_function, schema=None):
        engine, tbl1, tbl2 = setup_function(schema=schema)
        table = get_table('people', engine, schema=schema)
        
        # Create then drop index
        create_index('idx_to_drop', table.name, 'name', engine, schema=schema)
        drop_index('idx_to_drop', table.name, engine, schema=schema)
        
        # Verify index was dropped
        inspector = sa.inspect(engine)
        indexes = inspector.get_indexes(table.name, schema=schema)
        index_names = [idx['name'] for idx in indexes]
        self.assertNotIn('idx_to_drop', index_names)
    
    def test_drop_index_sqlite(self):
        self.drop_index(sqlite_setup)


if __name__ == '__main__':
    unittest.main()

