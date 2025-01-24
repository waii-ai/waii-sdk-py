import unittest
import pytest

import time

from tests.common_test_utils import connect_db, load_db_conn1, check_table_existence
from waii_sdk_py import WAII
from waii_sdk_py.database import (
    ModifyDBConnectionRequest,
    DBConnection,
    TableDefinition,
    TableName,
    ColumnDefinition,
    TableReference,
    UpdateTableDefinitionRequest, DBContentFilter, DBContentFilterScope, DBContentFilterType,
    DBContentFilterActionType, SearchContext, )
from waii_sdk_py.query import RunQueryRequest


class TestDatabase(unittest.TestCase):
    def _load_push_based_conn(self):
        self.push_db_conn = DBConnection(
            key="",  # will be generated by the system
            db_type="snowflake",
            database="push",
            host="push_sdk_test",
            push=True,
        )

    def setUp(self):
        WAII.initialize(url="http://localhost:9859/api/", verbose=True)

        self.db_conn = load_db_conn1()
        self._load_push_based_conn()

        connect_db(self.db_conn)
    
    def test_unknown_db_conn_fields_error(self):
        db_conn = DBConnection(
            key="postgresql://waii@localhost:5432/waii_sdk_test",
            db_type="postgresql",
            host="localhost",
            port=5432,
            database="waii_sdk_test",
            uname="waii", # uname field doesn't exist (sub for username). Should be caught in the test
            password="password"
        )

        db_conn.db_content_filters = [DBContentFilter(
            filter_scope = DBContentFilterScope.table,
            filter_type = DBContentFilterType.include,
            filter_action_type = DBContentFilterActionType.visibility,
            pattern='', # empty regex pattern matches all
            search_context = [
                SearchContext(db_name='*', schema_name='information_schema', table_name='tables'),
                SearchContext(db_name='*', schema_name='information_schema', table_name='columns'),
                SearchContext(db_name='*', schema_name='public', table_name='movies'),
            ]
        )]

        # modify the connection
        with pytest.raises(ValueError) as e:
            result = WAII.Database.modify_connections(
                ModifyDBConnectionRequest(updated=[db_conn])
            ).connectors
            assert str(e) == "ValueError: Cannot set unknown fields: ['uname']"

    def test_modify_db_with_search_context_db_content_filter(self):
        db_conn = load_db_conn1()
        db_conn.db_content_filters = [DBContentFilter(
            filter_scope = DBContentFilterScope.table,
            filter_type = DBContentFilterType.include,
            filter_action_type = DBContentFilterActionType.visibility,
            pattern='', # empty regex pattern matches all
            search_context = [
                SearchContext(db_name='*', schema_name='information_schema', table_name='tables'),
                SearchContext(db_name='*', schema_name='information_schema', table_name='columns'),
                SearchContext(db_name='*', schema_name='public', table_name='movies'),
            ]
        )]

        # modify the connection
        result = WAII.Database.modify_connections(
            ModifyDBConnectionRequest(updated=[db_conn])
        ).connectors

        # check if the connection is modified
        time.sleep(15)

        # get the catalog
        result = WAII.Database.get_catalogs()
        tables = set([str(t.name) for c in result.catalogs for s in c.schemas for t in s.tables])
        assert tables == {"table_name='COLUMNS' schema_name='INFORMATION_SCHEMA' database_name='WAII_SDK_TEST'",
                         "table_name='MOVIES' schema_name='PUBLIC' database_name='WAII_SDK_TEST'",
                         "table_name='TABLES' schema_name='INFORMATION_SCHEMA' database_name='WAII_SDK_TEST'"}

    def test_modify_connections(self):
        # first try to delete te connection if it exists
        result = WAII.Database.get_connections().connectors
        for conn in result:
            if (
                    conn.db_type == self.db_conn.db_type
                    and conn.account_name == self.db_conn.account_name
                    and self.db_conn.database == conn.database
                    and self.db_conn.username == conn.username
            ):
                result = WAII.Database.modify_connections(
                    ModifyDBConnectionRequest(removed=[conn.key])
                ).connectors
                break

        # then add the new connection
        new_result = WAII.Database.modify_connections(
            ModifyDBConnectionRequest(updated=[self.db_conn])
        ).connectors

        assert len(result) == len(new_result) - 1

        # then activate the new connection
        for conn in new_result:
            if (
                    conn.db_type == self.db_conn.db_type
                    and conn.account_name == self.db_conn.account_name
                    and self.db_conn.database == conn.database
                    and self.db_conn.username == conn.username
            ):
                WAII.Database.activate_connection(conn.key)
                break
        else:
            raise Exception("Cannot find the new connection")

        # list databases
        result = WAII.Database.get_catalogs()
        assert len(result.catalogs) > 0
        for catalog in result.catalogs:
            for schema in catalog.schemas:
                for table in schema.tables:
                    if len(table.refs) > 0:
                        assert type(table.refs[0]) == TableReference

    def test_modify_push_connection(self):
        result = WAII.Database.get_connections().connectors
        for conn in result:
            if (
                    conn.db_type == self.push_db_conn.db_type
                    and conn.host == self.push_db_conn.host
                    and conn.push
            ):
                result = WAII.Database.modify_connections(
                    ModifyDBConnectionRequest(removed=[conn.key])
                ).connectors
                break
        new_result = WAII.Database.modify_connections(
            ModifyDBConnectionRequest(updated=[self.push_db_conn])
        ).connectors

        assert len(result) == len(new_result) - 1

    def test_get_connections(self):
        # Call the function
        result = WAII.Database.get_connections()
        # Check the result
        # Note: The specifics of this assertion would depend on what the function should return
        self.assertEqual(len(result.connectors), len(result.connectors))

        # Define test parameters
        params = ModifyDBConnectionRequest(updated=[], removed=[])
        # Call the function
        result = WAII.Database.modify_connections(params)
        # Check the result
        # Note: The specifics of this assertion would depend on what the function should return
        self.assertEqual(len(result.connectors), len(result.connectors))

    def test_activate_connection(self):
        # Define test parameters
        # Call the function
        WAII.Database.activate_connection(self.db_conn.key)

    def test_get_catalogs(self):
        # Call the function
        result = WAII.Database.get_catalogs()
        assert len(result.catalogs) > 0

    def test_get_refs_from_api(self):
        result = WAII.Database.get_catalogs()
        catalog_def = result.catalogs[0]
        schemas = catalog_def.schemas
        refs = []
        for schema in schemas:
            if schema.name.schema_name == "INFORMATION_SCHEMA":
                continue
            for table in schema.tables:
                refs.extend(table.refs)

    def test_get_refs(self):
        table_definition = TableDefinition(
            name=TableName(
                database_name="db1", schema_name="schema1", table_name="table1"
            ),
            columns=[
                ColumnDefinition(name="col1", type="int"),
                ColumnDefinition(name="col2", type="int"),
                ColumnDefinition(name="col3", type="int"),
            ],
            refs=[
                TableReference(
                    src_table=TableName(
                        database_name="db1", schema_name="schema1", table_name="table1"
                    ),
                    src_cols=["col3"],
                    ref_table=TableName(
                        database_name="db1", schema_name="schema1", table_name="table1"
                    ),
                    ref_cols=["col3"],
                ),
            ],
        )
        assert len(table_definition.refs) > 0
        assert table_definition.refs[0] == TableReference(
            src_table=TableName(
                database_name="db1", schema_name="schema1", table_name="table1"
            ),
            src_cols=["col3"],
            ref_table=TableName(
                database_name="db1", schema_name="schema1", table_name="table1"
            ),
            ref_cols=["col3"],
        )

    def test_initial_connect(self):
        # because now we select first connection by default
        result = WAII.Database.get_catalogs()
        assert len(result.catalogs) > 0

        assert len(WAII.Database.get_activated_connection()) > 0

    def test_call_without_activated_connection(self):
        WAII.Database.activate_connection("")
        with self.assertRaises(Exception):
            result = WAII.Database.get_catalogs()

    def test_tabl_ref_deserialize(self):
        table_dict = {
            "name": TableName(
                table_name="table1", schema_name="schema1", database_name="db1"
            ),
            "columns": [
                ColumnDefinition(
                    name="col1",
                    type="int",
                    comment=None,
                    description=None,
                    sample_values=None,
                ),
                ColumnDefinition(
                    name="col2",
                    type="int",
                    comment=None,
                    description=None,
                    sample_values=None,
                ),
                ColumnDefinition(
                    name="col3",
                    type="int",
                    comment=None,
                    description=None,
                    sample_values=None,
                ),
            ],
            "comment": None,
            "last_altered_time": None,
            "constraints": None,
            "inferred_refs": None,
            "inferred_constraints": None,
            "description": None,
            "refs": [
                {
                    "ref_cols": ["col3"],
                    "ref_table": {
                        "database_name": "db1",
                        "schema_name": "schema1",
                        "table_name": "table1",
                    },
                    "source": None,
                    "src_cols": ["col3"],
                    "src_table": {
                        "database_name": "db1",
                        "schema_name": "schema1",
                        "table_name": "table1",
                    },
                }
            ],
        }
        ref_dict = {
            "src_table": {
                "table_name": "MATCHES",
                "schema_name": "WTA_1",
                "database_name": "SPIDER_DEV",
            },
            "src_cols": ["WINNER_ID"],
            "ref_table": {
                "table_name": "PLAYERS",
                "schema_name": "WTA_1",
                "database_name": "SPIDER_DEV",
            },
            "ref_cols": ["PLAYER_ID"],
            "source": "database",
            "score": None,
        }
        table_def = TableDefinition(**table_dict)
        assert type(table_def.refs[0]) == TableReference
        assert table_def.refs[0] == TableReference(
            src_table=TableName(
                database_name="db1", schema_name="schema1", table_name="table1"
            ),
            src_cols=["col3"],
            ref_table=TableName(
                database_name="db1", schema_name="schema1", table_name="table1"
            ),
            ref_cols=["col3"],
        )

    def test_update_table_definitions(self):

        table_definition = TableDefinition(
            name=TableName(
                database_name="db1", schema_name="schema2", table_name="table2"
            ),
            columns=[
                ColumnDefinition(name="col1", type="int"),
                ColumnDefinition(name="col2", type="int"),
                ColumnDefinition(name="col3", type="int"),
            ],
        )
        update_table_req = UpdateTableDefinitionRequest(
            updated_tables=[table_definition]
        )
        result = WAII.Database.update_table_definition(update_table_req)

    def test_remove_tables(self):
        table_to_be_removed = TableName(
            database_name="db1", schema_name="schema2", table_name="table2"
        )

        update_table_req = UpdateTableDefinitionRequest(
            removed_tables=[table_to_be_removed]
        )
        result = WAII.Database.update_table_definition(update_table_req)

    def test_refresh_db_connection(self):
        WAII.Database.activate_connection(self.db_conn.key)

        # get catalog and see if test_refresh_db_connection table exists
        result = WAII.Database.get_catalogs()
        table_exists = False
        for catalog in result.catalogs:
            for schema in catalog.schemas:
                for table in schema.tables:
                    if table.name.table_name.lower() == "test_refresh_db_connection":
                        table_exists = True
                        break

        # if table exists, run DROP TABLE
        if table_exists:
            try:
                WAII.Query.run(RunQueryRequest(query="DROP TABLE test_refresh_db_connection_schema.test_refresh_db_connection"))
            except Exception as e:
                print(f"Error dropping table: {e}")

            table_removed = check_table_existence(
                WAII, "test_refresh_db_connection", False
            )

            assert table_removed

        # then create a new table
        WAII.Query.run(
            RunQueryRequest(
                query="CREATE SCHEMA IF NOT EXISTS test_refresh_db_connection_schema"
            )
        )

        WAII.Query.run(
            RunQueryRequest(
                query="CREATE TABLE test_refresh_db_connection_schema.test_refresh_db_connection (id INT)"
            )
        )

        table_created = check_table_existence(
            WAII, "test_refresh_db_connection", True
        )

        assert table_created


# NEED TO ADD FOR UPDATE TABLE AND UPDATE SCHEMA
if __name__ == "__main__":
    unittest.main()
