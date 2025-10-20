"""Tests for table operations."""

import unittest

from setup_test import sqlite_setup
from fullmetalalchemy.features import get_table

from transmutation.table import (
    rename_table,
    create_table,
    drop_table,
    copy_table,
    truncate_table,
)

import sqlalchemy as sa
from sqlalchemy import Column, Integer, String


class TestRenameTable(unittest.TestCase):
    """Tests for rename_table function."""
    
    def rename_table(self, setup_function, schema=None):
        engine, tbl1, tbl2 = setup_function(schema=schema)
        table = get_table('people', engine, schema=schema)
        new_table_name = 'employees'
        
        table_names = sa.inspect(engine).get_table_names(schema=schema)
        table_names.remove(table.name)
        
        table = rename_table(table.name, new_table_name, engine, schema=schema)
        table_names.append(new_table_name)
        
        new_table_names = sa.inspect(engine).get_table_names(schema=schema)
        self.assertSetEqual(set(table_names), set(new_table_names))

    def test_rename_table_sqlite(self):
        self.rename_table(sqlite_setup)


class TestCreateTable(unittest.TestCase):
    """Tests for create_table function."""
    
    def create_table_basic(self, setup_function, schema=None):
        engine, _, _ = setup_function(schema=schema)
        
        columns = [
            Column('id', Integer, primary_key=True),
            Column('name', String(50), nullable=False),
            Column('email', String(100))
        ]
        
        create_table('new_users', columns, engine, schema=schema)
        
        # Verify table was created
        inspector = sa.inspect(engine)
        table_names = inspector.get_table_names(schema=schema)
        self.assertIn('new_users', table_names)
        
        # Verify columns
        cols = inspector.get_columns('new_users', schema=schema)
        col_names = [c['name'] for c in cols]
        self.assertIn('id', col_names)
        self.assertIn('name', col_names)
        self.assertIn('email', col_names)
    
    def test_create_table_sqlite(self):
        self.create_table_basic(sqlite_setup)


class TestDropTable(unittest.TestCase):
    """Tests for drop_table function."""
    
    def drop_table_basic(self, setup_function, schema=None):
        engine, tbl1, tbl2 = setup_function(schema=schema)
        
        # Drop an existing table (places is created by setup)
        drop_table('places', engine, schema=schema)
        
        # Verify table was dropped
        inspector = sa.inspect(engine)
        table_names = inspector.get_table_names(schema=schema)
        self.assertNotIn('places', table_names)
    
    def test_drop_table_sqlite(self):
        self.drop_table_basic(sqlite_setup)
    
    def test_drop_table_if_exists(self, setup_function=sqlite_setup, schema=None):
        engine, _, _ = setup_function(schema=schema)
        
        # Should not raise error for non-existent table
        drop_table('nonexistent_table', engine, schema=schema, if_exists=True)
        
        self.assertTrue(True)  # If we get here, no exception was raised
    
    def test_drop_table_if_exists_sqlite(self):
        self.test_drop_table_if_exists(sqlite_setup)


class TestCopyTable(unittest.TestCase):
    """Tests for copy_table function."""
    
    def copy_table_basic(self, setup_function, schema=None):
        engine, tbl1, tbl2 = setup_function(schema=schema)
        table = get_table('people', engine, schema=schema)
        new_table_name = 'people_backup'
        
        table_names = sa.inspect(engine).get_table_names(schema=schema)
        copy_table(table, new_table_name, engine, schema=schema)
        table_names.append(new_table_name)
        
        new_table_names = sa.inspect(engine).get_table_names(schema=schema)
        self.assertSetEqual(set(table_names), set(new_table_names))
    
    def test_copy_table_sqlite(self):
        self.copy_table_basic(sqlite_setup)


class TestTruncateTable(unittest.TestCase):
    """Tests for truncate_table function."""
    
    def truncate_table_basic(self, setup_function, schema=None):
        engine, tbl1, tbl2 = setup_function(schema=schema)
        table = get_table('people', engine, schema=schema)
        
        # Insert some data first
        with engine.begin() as conn:
            conn.execute(
                sa.insert(table).values(name='Test', age=30, address_id=1)
            )
        
        # Truncate the table
        truncate_table(table.name, engine, schema=schema)
        
        # Verify table is empty
        with engine.connect() as conn:
            result = conn.execute(sa.select(sa.func.count()).select_from(table))
            count = result.scalar()
            self.assertEqual(count, 0)
    
    def test_truncate_table_sqlite(self):
        self.truncate_table_basic(sqlite_setup)


if __name__ == '__main__':
    unittest.main()

