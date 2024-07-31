import json
import os
import unittest
from waii_sdk_py import WAII
from waii_sdk_py.database import (
    ModifyDBConnectionRequest,
    DBConnection,
    TableDefinition,
    TableName,
    ColumnDefinition,
    TableReference,
    UpdateTableDefinitionRequest, DBContentFilter,
)


class TestDatabase(unittest.TestCase):
    def _load_db_conn(self):
        db_conn_str = os.environ.get("WAII_DB_CONN")
        if not db_conn_str:
            raise Exception(
                """You should set WAII_DB_CONN to env, format like:
        {"db_type": "snowflake", "account_name": "...", "user": "...", "pass": "...", "database": "...", "role": "...", "warehouse": "..."}
        """
            )

        db_conn_json = json.loads(db_conn_str)

        # load it from json
        self.db_conn = DBConnection(
            key="",  # will be generated by the system
            db_type=db_conn_json["db_type"],
            account_name=db_conn_json["account_name"],
            username=db_conn_json["user"],
            password=db_conn_json["pass"],
            database=db_conn_json["database"],
            warehouse=db_conn_json["warehouse"],
            role=db_conn_json["role"],
            host=db_conn_json["host"],
            port=db_conn_json["port"],
            db_content_filters = [DBContentFilter(filter_scope="column", filter_type="exclude", ignore_case=False, pattern = "ID")]
        )

    def _load_push_based_conn(self):
        self.push_db_conn = DBConnection(
            key="",  # will be generated by the system
            db_type="snowflake",
            database="push",
            host="push_sdk_test",
            push=True,
        )

    def setUp(self):
        WAII.initialize(url="http://localhost:9859/api/")

        result = WAII.Database.get_connections()
        self.result = result

        self._load_db_conn()
        self._load_push_based_conn()

        WAII.Database.activate_connection(result.connectors[0].key)

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
                    for col in table.columns:
                        assert col.name != "ID"

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
        self.assertEqual(len(result.connectors), len(self.result.connectors))

        # Define test parameters
        params = ModifyDBConnectionRequest(updated=[], removed=[])
        # Call the function
        result = WAII.Database.modify_connections(params)
        # Check the result
        # Note: The specifics of this assertion would depend on what the function should return
        self.assertEqual(len(result.connectors), len(self.result.connectors))

    def test_activate_connection(self):
        # Define test parameters
        # Call the function
        WAII.Database.activate_connection(self.result.connectors[0].key)

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


# NEED TO ADD FOR UPDATE TABLE AND UPDATE SCHEMA
if __name__ == "__main__":
    unittest.main()
