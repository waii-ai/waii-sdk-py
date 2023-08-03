from waii_sdk_py.waii_http_client import WaiiHttpClient
from pydantic import BaseModel
import re
from typing import Optional, List, Dict, Any, Union
from urllib.parse import urlparse, parse_qs

MODIFY_DB_ENDPOINT = 'update-db-connect-info'
GET_CATALOG_ENDPOINT = 'get-table-definitions'

class SchemaName(BaseModel):
    schema_name: str
    database_name: Optional[str]

class TableName(BaseModel):
    table_name: str
    schema_name: Optional[str]
    database_name: Optional[str]

class ColumnSampleValues(BaseModel):
    values: Optional[Dict[str, int]]

class ColumnDefinition(BaseModel):
    name: str
    type: str
    comment: Optional[str]
    sample_values: Optional[ColumnSampleValues]

    def __lt__(self, other):
        return self.name < other.name

class TableReference(BaseModel):
    src_table: Optional[TableName]
    src_cols: Optional[List[str]]
    ref_table: Optional[TableName]
    ref_cols: Optional[List[str]]

class TableNameToDescription(BaseModel):
    name: str
    description: str

class SchemaDescription(BaseModel):
    summary: Optional[str]
    common_questions: Optional[List[str]]
    common_tables: Optional[List[TableNameToDescription]]

class TableDefinition(BaseModel):
    name: TableName
    columns: Optional[List[ColumnDefinition]]
    comment: Optional[str]
    last_altered_time: Optional[int]
    refs: Optional[List[TableReference]]
    description: Optional[str]

class SchemaDefinition(BaseModel):
    name: SchemaName
    tables: Optional[List[TableDefinition]]
    description: Optional[SchemaDescription]

class CatalogDefinition(BaseModel):
    name: str
    schemas: Optional[List[SchemaDefinition]]

class DBConnection(BaseModel):
    key: str
    db_type: str
    description: Optional[str]
    account_name: Optional[str]
    username: Optional[str]
    password: Optional[str]
    database: Optional[str]
    warehouse: Optional[str]
    role: Optional[str]
    path: Optional[str]
    parameters: Optional[Dict[str, Any]]

class ModifyDBConnectionRequest(BaseModel):
    updated: Optional[List[DBConnection]]
    removed: Optional[List[str]]
    validate_before_save: Optional[bool] = None
    user_id: Optional[str] = None
    default_db_connection_key: Optional[str] = None

class ModifyDBConnectionResponse(BaseModel):
    connectors: Optional[List[DBConnection]]
    diagnostics: Optional[str]
    default_db_connection_key: Optional[str] 

class SearchContext(BaseModel):
    db_name: Optional[str] = '*'
    schema_name: Optional[str] = '*' 
    table_name: Optional[str] = '*'

class GetCatalogRequest(BaseModel):
    pass

class GetDBConnectionRequest(BaseModel):
    pass

class GetDBConnectionResponse(BaseModel):
    connectors: Optional[List[DBConnection]]
    diagnostics: Optional[str]
    default_db_connection_key: Optional[str] 

class GetCatalogResponse(BaseModel):
    catalogs: Optional[List[CatalogDefinition]] = None

class Database:
    @staticmethod
    def modify_connections(params: ModifyDBConnectionRequest) -> ModifyDBConnectionResponse:
        return WaiiHttpClient.get_instance().common_fetch(MODIFY_DB_ENDPOINT, params.__dict__, ModifyDBConnectionResponse)

    @staticmethod
    def get_connections(params: GetDBConnectionRequest = GetDBConnectionRequest()) -> GetDBConnectionResponse:
        return WaiiHttpClient.get_instance().common_fetch(MODIFY_DB_ENDPOINT, params.__dict__, GetDBConnectionResponse)

    @staticmethod
    def activate_connection(key: str):
        WaiiHttpClient.get_instance().set_scope(key)

    @staticmethod
    def get_catalogs(params: GetCatalogRequest = GetCatalogRequest()) -> GetCatalogResponse:
        return WaiiHttpClient.get_instance().common_fetch(GET_CATALOG_ENDPOINT, params.__dict__, GetCatalogResponse)
