import unittest

from setup_test import sqlite_setup
from fullmetalalchemy.features import get_table, get_column

from transmutation.alter import rename_column, drop_column, add_column, rename_table
from transmutation.alter import copy_table
from transmutation.exceptions import ValidationError, ColumnError, TableError

import sqlalchemy as sa


# rename_column
class TestRenameColumn(unittest.TestCase):
    def rename_column(self, setup_function, schema=None):
        engine, tbl1, tbl2 = setup_function(schema=schema)
        table = get_table('people', engine, schema=schema)
        rename_column(table.name, 'name', 'first_name', engine, schema=schema)
        table = get_table(table.name, engine, schema=schema)
        cols = set(table.columns.keys())
        self.assertSetEqual(cols, {'id', 'age', 'first_name', 'address_id'})

    def test_rename_column_sqlite(self):
        self.rename_column(sqlite_setup)

    def raise_key_error(self, setup_function, error, schema=None):
        engine, tbl1, tbl2 = setup_function(schema=schema)
        table = get_table('people', engine, schema=schema)
        with self.assertRaises(error):
            rename_column(table.name, 'names', 'first_name', engine, schema=schema)

    def test_rename_column_key_error_sqlite(self):
        self.raise_key_error(sqlite_setup, ValidationError)

    def raise_operational_error(self, setup_function, error, schema=None):
        engine, tbl1, tbl2 = setup_function(schema=schema)
        table = get_table('people', engine, schema=schema)
        with self.assertRaises(error):
            rename_column(table.name, 'name', 'age', engine, schema=schema)

    def test_rename_column_op_error_sqlite(self):
        self.raise_operational_error(sqlite_setup, ColumnError)

# drop_column
class TestDropColumn(unittest.TestCase):
    def drop_column(self, setup_function, schema=None):
        engine, tbl1, tbl2 = setup_function(schema=schema)
        table = get_table('people', engine, schema=schema)
        drop_column(table.name, 'name', engine, schema=schema)
        table = get_table(table.name, engine, schema=schema)
        cols = set(table.columns.keys())
        self.assertSetEqual(cols, {'id', 'age', 'address_id'})

    def test_drop_column_sqlite(self):
        self.drop_column(sqlite_setup)

    def raise_key_error(self, setup_function, error, schema=None):
        engine, tbl1, tbl2 = setup_function(schema=schema)
        table = get_table('people', engine, schema=schema)
        with self.assertRaises(error):
            drop_column(table.name, 'names', engine, schema=schema)

    def test_drop_column_key_error_sqlite(self):
        self.raise_key_error(sqlite_setup, ValidationError)
    

# add_column
class TestAddColumn(unittest.TestCase):
    def add_column(self, setup_function, schema=None):
        engine, tbl1, tbl2 = setup_function(schema=schema)
        table = get_table('people', engine, schema=schema)
        table = add_column(table.name, 'last_name', str, engine, schema=schema)
        cols = set(table.columns.keys())
        self.assertSetEqual(cols, {'id', 'age', 'name', 'address_id', 'last_name'})
        self.assertIs(sa.VARCHAR, type(get_column(table, 'last_name').type))

    def test_add_column_sqlite(self):
        self.add_column(sqlite_setup)

    def raise_operational_error(self, setup_function, error, schema=None):
        engine, tbl1, tbl2 = setup_function(schema=schema)
        table = get_table('people', engine, schema=schema)
        with self.assertRaises(error):
            add_column(table.name, 'name', str, engine, schema=schema)

    def test_add_column_op_error_sqlite(self):
        self.raise_operational_error(sqlite_setup, ColumnError)


class TestRenameTable(unittest.TestCase):
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

    def raise_key_error(self, setup_function, error, schema=None):
        engine, tbl1, tbl2 = setup_function(schema=schema)
        table = get_table('people', engine, schema=schema)
        new_table_name = 'places'
        with self.assertRaises(error):
            rename_table(table.name, new_table_name, engine, schema=schema)

    def test_rename_table_fail_sqlite(self):
        self.raise_key_error(sqlite_setup, TableError)


# TODO: copy_table tests
class TestCopyTable(unittest.TestCase):
    def copy_table(self, setup_function, schema=None):
        engine, tbl1, tbl2 = setup_function(schema=schema)
        table = get_table('people', engine, schema=schema)
        new_table_name = 'employees'
        table_names = sa.inspect(engine).get_table_names(schema=schema)
        copy_table(table, new_table_name, engine, schema=schema)  # Pass table object, not table.name
        table_names.append(new_table_name)
        new_table_names = sa.inspect(engine).get_table_names(schema=schema)
        self.assertSetEqual(set(table_names), set(new_table_names))

    def test_copy_table_sqlite(self):
        self.copy_table(sqlite_setup)
 

# TODO: replace_primary_key tests
class TestReplacePrimaryKey(unittest.TestCase):
    pass

# TODO: create_primary_key tests - Only use on a table with no primary key.
class TestCreatePrimaryKey(unittest.TestCase):
    pass

# TODO: name_primary_key tests
class TestNamePrimaryKey(unittest.TestCase):
    pass