import unittest
import pytest
from waii_sdk_py import WAII
from waii_sdk_py.common import OperationStatus
from waii_sdk_py.database import *
from waii_sdk_py.query import *
from waii_sdk_py.semantic_layer_dump import *

class TestSemanticLayerDump(unittest.TestCase):
    def connect_db1(self):
        result = WAII.Database.get_connections()
        for connector in result.connectors:
            if connector.db_type == "postgresql" and connector.database == 'waii_sdk_test':
                db_conn1 = connector
                break

        WAII.Database.activate_connection(db_conn1.key)
        self.db_conn1 = db_conn1
    
    def connect_db2(self):
        result = WAII.Database.get_connections()
        for connector in result.connectors:
            if connector.db_type == "postgresql" and connector.database == 'waii_sdk_test_copy':
                db_conn2 = connector
                break

        WAII.Database.activate_connection(db_conn2.key)
        self.db_conn2 = db_conn2

    def setUp(self):
        WAII.initialize(url="http://localhost:9859/api/")
        self.connect_db2()
        self.connect_db1()

    def test_export_import_semantic_layer_dump(self):
        self.connect_db1()

        catalogs: Optional[List[CatalogDefinition]] = WAII.Database.get_catalogs(GetCatalogRequest()).catalogs
        source_table = catalogs[0].schemas[1].tables[0].name
        source_table_name = source_table.table_name
        source_old_description = catalogs[0].schemas[1].tables[0].description
        source_new_description = "test description"

        self.connect_db2()
        catalogs: Optional[List[CatalogDefinition]] = WAII.Database.get_catalogs(GetCatalogRequest()).catalogs
        for catalog in catalogs:
            for schema in catalog.schemas:
                for table in schema.tables:
                    if table.name.table_name == source_table_name:
                        target_table = table.name
                        target_table_name = target_table.table_name
                        target_old_description = table.description
                        target_new_description = "test description 2"

        # add custom table description
        self.connect_db1()
        WAII.Database.update_table_description(UpdateTableDescriptionRequest(
            table_name=source_table,
            description=source_new_description
        ))

        # change the description of the target table
        self.connect_db2()
        WAII.Database.update_table_description(UpdateTableDescriptionRequest(
            table_name=target_table,
            description=target_new_description
        ))

        # export semantic layer dump
        self.connect_db1()
        resp = WAII.SemanticLayerDump.export_dump(ExportSemanticLayerDumpRequest(
            db_conn_key=self.db_conn1.key
        ))
        export_op_id = resp.op_id

        # wait for the export to complete
        while True:
            resp = WAII.SemanticLayerDump.export_dump_status(CheckOperationStatusRequest(
                op_id=export_op_id
            ))
            if resp.status == OperationStatus.SUCCEEDED:
                break
            elif resp.status == OperationStatus.FAILED: 
                raise Exception(f"Export failed: {resp.info}")
            time.sleep(1)
        
        # check the description of the source table from the export
        configuration = resp.info
        for table in configuration['tables']:
            if table['name'] == source_table_name:
                self.assertEqual(table['description'], source_new_description)

        # import the semantic layer dump
        self.connect_db2()
        resp = WAII.SemanticLayerDump.import_dump(ImportSemanticLayerDumpRequest(
            db_conn_key=self.db_conn2.key,
            configuration=resp.info
        ))
        import_op_id = resp.op_id

        # wait for the import to complete
        while True:
            resp = WAII.SemanticLayerDump.import_dump_status(CheckOperationStatusRequest(
                op_id=import_op_id
            ))
            if resp.status == OperationStatus.SUCCEEDED:
                break
            elif resp.status == OperationStatus.FAILED:
                raise Exception(f"Import failed: {resp.info}")
            time.sleep(1)

        # check the table description
        self.connect_db2()
        catalogs: Optional[List[CatalogDefinition]] = WAII.Database.get_catalogs(GetCatalogRequest()).catalogs
        for catalog in catalogs:
            for schema in catalog.schemas:
                for table in schema.tables:
                    if table.name.table_name == target_table_name:
                        self.assertEqual(table.description, source_new_description)

        # restore the table descriptions
        self.connect_db1()
        WAII.Database.update_table_description(UpdateTableDescriptionRequest(
            table_name=source_table,
            description=source_old_description
        ))
        self.connect_db2()
        WAII.Database.update_table_description(UpdateTableDescriptionRequest(
            table_name=target_table,
            description=target_old_description
        ))
