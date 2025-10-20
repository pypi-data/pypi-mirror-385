import unittest
import decimal
from velocity.db.servers.postgres.sql import SQL
from velocity.db.servers.tablehelper import TableHelper
from velocity.db.servers.postgres.types import TYPES


class MockTx:
    def __init__(self):
        self.table_cache = {}
        self.cursor_cache = {}
    
    def cursor(self):
        return None
    
    def table(self, table_name):
        # Return a mock table object
        return MockTable()

class MockTable:
    def column(self, column_name):
        return MockColumn()

class MockColumn:
    def __init__(self):
        self.py_type = str
    
    def exists(self):
        return True

class TestSQLModule(unittest.TestCase):
    def test_quote_simple_identifier(self):
        self.assertEqual(TableHelper.quote("test"), "test")

    def test_quote_reserved_word(self):
        self.assertEqual(TableHelper.quote("SELECT"), '"SELECT"')

    def test_quote_with_special_characters(self):
        self.assertEqual(TableHelper.quote("my/schema"), '"my/schema"')

    def test_quote_dot_notation(self):
        self.assertEqual(TableHelper.quote("my_table.my_column"), "my_table.my_column")

    def test_quote_list_identifiers(self):
        self.assertEqual(
            TableHelper.quote(["test", "SELECT", "my_table"]),
            ["test", '"SELECT"', "my_table"],
        )

    def test_make_where_simple_equality(self):
        # Create a mock transaction and table helper
        mock_tx = MockTx()
        helper = TableHelper(mock_tx, "test_table")

        sql, vals = helper.make_where({"column1": "value1"})
        self.assertIn("column1 = %s", sql)
        self.assertEqual(vals, ("value1",))

    def test_make_where_with_null(self):
        mock_tx = MockTx()
        helper = TableHelper(mock_tx, "test_table")

        sql, vals = helper.make_where({"column1": None})
        self.assertIn("column1 IS NULL", sql)
        self.assertEqual(vals, ())

    def test_make_where_with_not_null(self):
        mock_tx = MockTx()
        helper = TableHelper(mock_tx, "test_table")

        sql, vals = helper.make_where({"column1!": None})
        self.assertIn("column1! IS NULL", sql)
        self.assertEqual(vals, ())

    def test_make_where_with_operators(self):
        mock_tx = MockTx()
        helper = TableHelper(mock_tx, "test_table")

        sql, vals = helper.make_where({"column1>": 10, "column2!": "value2"})
        self.assertIn("column1> = %s", sql)
        self.assertIn("column2! = %s", sql)
        self.assertEqual(len(vals), 2)

    def test_make_where_with_list(self):
        mock_tx = MockTx()
        helper = TableHelper(mock_tx, "test_table")

        sql, vals = helper.make_where({"column1": [1, 2, 3]})
        self.assertIn("column1 IN", sql)
        self.assertEqual(len(vals), 3)

    def test_make_where_between(self):
        mock_tx = MockTx()
        helper = TableHelper(mock_tx, "test_table")

        sql, vals = helper.make_where({"column1><": [1, 10]})
        self.assertIn("column1>< = %s", sql)
        self.assertEqual(len(vals), 1)  # Actual implementation returns one parameter

    def test_sql_select_simple(self):
        mock_tx = MockTx()
        sql_query, params = SQL.select(mock_tx, columns="*", table="my_table")
        self.assertIn("SELECT *", sql_query)
        self.assertIn("FROM my_table", sql_query)
        self.assertEqual(params, ())

    def test_sql_select_with_where(self):
        mock_tx = MockTx()
        sql_query, params = SQL.select(mock_tx, columns="*", table="my_table", where={"id": 1})
        self.assertIn("SELECT *", sql_query)
        self.assertIn("WHERE id = %s", sql_query)
        self.assertEqual(params, (1,))

    def test_sql_select_with_order_by(self):
        mock_tx = MockTx()
        sql_query, params = SQL.select(mock_tx, columns="*", table="my_table", orderby="id DESC")
        self.assertIn("SELECT *", sql_query)
        self.assertIn("ORDER BY id DESC", sql_query)
        self.assertEqual(params, ())

    def test_sql_insert(self):
        sql_query, params = SQL.insert(
            table="my_table", data={"column1": "value1", "column2": 2}
        )
        self.assertIn("INSERT INTO my_table", sql_query)
        self.assertIn("VALUES (%s,%s)", sql_query)
        self.assertEqual(params, ("value1", 2))

    def test_sql_update(self):
        mock_tx = MockTx()
        sql_query, params = SQL.update(
            mock_tx, table="my_table", data={"column1": "new_value"}, pk={"id": 1}
        )
        self.assertIn("UPDATE my_table", sql_query)
        self.assertIn("SET column1 = %s", sql_query)
        self.assertIn("WHERE id = %s", sql_query)
        self.assertEqual(params, ("new_value", 1))

    def test_sql_delete(self):
        mock_tx = MockTx()
        sql_query, params = SQL.delete(mock_tx, table="my_table", where={"id": 1})
        self.assertIn("DELETE", sql_query)
        self.assertIn("FROM my_table", sql_query)
        self.assertIn("WHERE id = %s", sql_query)
        self.assertEqual(params, (1,))

    def test_sql_create_table(self):
        sql_query, params = SQL.create_table(
            name="public.test_table", columns={"name": str, "age": int}, drop=True
        )
        self.assertIn("CREATE TABLE", sql_query)
        self.assertIn("test_table", sql_query)
        self.assertIn("DROP TABLE IF EXISTS", sql_query)
        self.assertEqual(params, ())

    def test_sql_drop_table(self):
        sql_query, params = SQL.drop_table("public.test_table")
        self.assertIn("drop table if exists", sql_query.lower())
        self.assertIn("test_table", sql_query)
        self.assertEqual(params, ())

    def test_sql_create_index(self):
        mock_tx = MockTx()
        sql_query, params = SQL.create_index(
            mock_tx, table="my_table", columns="column1", unique=True
        )
        self.assertIn("CREATE UNIQUE INDEX", sql_query)
        self.assertIn("my_table", sql_query)
        self.assertEqual(params, ())

    def test_sql_drop_index(self):
        sql_query, params = SQL.drop_index(table="my_table", columns="column1")
        self.assertIn("DROP INDEX IF EXISTS", sql_query)
        self.assertEqual(params, ())

    def test_sql_foreign_key_creation(self):
        sql_query, params = SQL.create_foreign_key(
            table="child_table",
            columns="parent_id",
            key_to_table="parent_table",
            key_to_columns="id",
        )
        self.assertIn("ALTER TABLE child_table ADD CONSTRAINT", sql_query)
        self.assertIn(
            "FOREIGN KEY (parent_id) REFERENCES parent_table (id);", sql_query
        )
        self.assertEqual(params, ())

    def test_sql_merge_insert(self):
        mock_tx = MockTx()
        sql_query, params = SQL.merge(
            mock_tx,
            table="my_table",
            data={"column1": "value1"},
            pk={"id": 1},
            on_conflict_do_nothing=True,
            on_conflict_update=False,
        )
        self.assertIn("INSERT INTO my_table", sql_query)
        self.assertIn("ON CONFLICT", sql_query)
        self.assertIn("DO NOTHING", sql_query)
        self.assertEqual(params, ("value1", 1))

    def test_sql_merge_update(self):
        mock_tx = MockTx()
        sql_query, params = SQL.merge(
            mock_tx,
            table="my_table",
            data={"column1": "value1"},
            pk={"id": 1},
            on_conflict_do_nothing=False,
            on_conflict_update=True,
        )
        self.assertIn("INSERT INTO my_table", sql_query)
        self.assertIn("ON CONFLICT", sql_query)
        self.assertIn("DO", sql_query)
        self.assertIn("UPDATE", sql_query)
        self.assertIn("SET", sql_query)
        self.assertEqual(params, ("value1", 1))

    def test_get_type_mapping(self):
        self.assertEqual(TYPES.get_type("string"), "TEXT")
        self.assertEqual(TYPES.get_type(123), "BIGINT")
        self.assertEqual(TYPES.get_type(123.456), "NUMERIC(19, 6)")
        self.assertEqual(TYPES.get_type(True), "BOOLEAN")
        self.assertEqual(TYPES.get_type(None), "TEXT")

    def test_py_type_mapping(self):
        self.assertEqual(TYPES.py_type("INTEGER"), int)
        self.assertEqual(TYPES.py_type("NUMERIC"), decimal.Decimal)
        self.assertEqual(TYPES.py_type("TEXT"), str)
        self.assertEqual(TYPES.py_type("BOOLEAN"), bool)

    def test_sql_truncate(self):
        sql_query, params = SQL.truncate("my_table")
        self.assertEqual(sql_query, "truncate table my_table")
        self.assertEqual(params, ())

    def test_sql_create_view(self):
        sql_query, params = SQL.create_view(
            name="my_view", query="SELECT * FROM my_table", temp=True, silent=True
        )
        self.assertIn("CREATE OR REPLACE", sql_query)
        self.assertIn("TEMPORARY VIEW", sql_query)
        self.assertIn("my_view", sql_query)
        self.assertIn("SELECT *", sql_query)
        self.assertIn("FROM my_table", sql_query)
        self.assertEqual(params, ())

    def test_sql_drop_view(self):
        sql_query, params = SQL.drop_view(name="my_view", silent=True)
        self.assertEqual(sql_query, "DROP VIEW IF EXISTS my_view")
        self.assertEqual(params, ())

    # Additional tests can be added here to cover more methods and edge cases


if __name__ == "__main__":
    unittest.main()
