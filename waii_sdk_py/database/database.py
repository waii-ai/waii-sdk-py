from waii_sdk_py.waii_http_client import WaiiHttpClient
from pydantic import BaseModel
import re
from typing import Optional, List, Dict, Any, Union
from urllib.parse import urlparse, parse_qs
from enum import Enum

MODIFY_DB_ENDPOINT = 'update-db-connect-info'
GET_CATALOG_ENDPOINT = 'get-table-definitions'
UPDATE_TABLE_DESCRIPTION_ENDPOINT = 'update-table-description'
UPDATE_SCHEMA_DESCRIPTION_ENDPOINT = 'update-schema-description'


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
    description: Optional[str]
    sample_values: Optional[ColumnSampleValues]

    def __lt__(self, other):
        return self.name < other.name


class ConstraintType(str, Enum):
    primary = "primary"


class ConstraintDetectorType(str, Enum):
    database = "database"
    inferred_llm = "inferred_llm"
    inferred_static = "inferred_static"
    inferred_query_history = "inferred_query_history"
    manual = "manual"


class TableReference(BaseModel):
    src_table: Optional[TableName]  # table name
    src_cols: Optional[List[str]]  # source table columns
    ref_table: Optional[TableName]  # ref table name
    ref_cols: Optional[List[str]]  # ref table columns
    source: Optional[ConstraintDetectorType]


class TableNameToDescription(BaseModel):
    name: str
    description: str


class SchemaDescription(BaseModel):
    summary: Optional[str]
    common_questions: Optional[List[str]]
    common_tables: Optional[List[TableNameToDescription]]


class Constraint(BaseModel):
    source: Optional[ConstraintDetectorType]
    table: Optional[TableName]
    cols: Optional[List[str]]
    constraint_type: Optional[ConstraintType]


class TableDefinition(BaseModel):
    name: TableName
    columns: Optional[List[ColumnDefinition]]
    comment: Optional[str]
    last_altered_time: Optional[int]
    refs: Optional[List[TableReference]]
    refs: Optional[List[TableReference]]
    inferred_refs: Optional[List[TableReference]]
    inferred_constraints: Optional[List[Constraint]]
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
    description: Optional[str] = None
    account_name: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    database: Optional[str] = None
    warehouse: Optional[str] = None
    role: Optional[str] = None
    path: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    parameters: Optional[Dict[str, Any]] = None
    sample_col_values: Optional[bool]


class ModifyDBConnectionRequest(BaseModel):
    updated: Optional[List[DBConnection]] = None
    removed: Optional[List[str]] = None
    validate_before_save: Optional[bool] = None
    user_id: Optional[str] = None
    default_db_connection_key: Optional[str] = None


class SchemaIndexingStatus(BaseModel):
    n_pending_indexing_tables: int
    n_total_tables: int
    status: str


class DBConnectionIndexingStatus(BaseModel):
    status: Optional[str]
    schema_status: Optional[Dict[str, SchemaIndexingStatus]]


class ModifyDBConnectionResponse(BaseModel):
    connectors: Optional[List[DBConnection]]
    diagnostics: Optional[str]
    default_db_connection_key: Optional[str]
    connector_status: Optional[Dict[str, DBConnectionIndexingStatus]]


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
    connector_status: Optional[Dict[str, DBConnectionIndexingStatus]]


class GetCatalogResponse(BaseModel):
    catalogs: Optional[List[CatalogDefinition]] = None


class UpdateTableDescriptionRequest(BaseModel):
    table_name: TableName
    description: str


class UpdateSchemaDescriptionRequest(BaseModel):
    schema_name: SchemaName
    description: str


class UpdateTableDescriptionResponse(BaseModel):
    pass


class UpdateSchemaDescriptionResponse(BaseModel):
    pass


class Database:
    @staticmethod
    def modify_connections(params: ModifyDBConnectionRequest) -> ModifyDBConnectionResponse:
        return WaiiHttpClient.get_instance().common_fetch(MODIFY_DB_ENDPOINT, params.__dict__,
                                                          ModifyDBConnectionResponse)

    @staticmethod
    def get_connections(params: GetDBConnectionRequest = GetDBConnectionRequest()) -> GetDBConnectionResponse:
        return WaiiHttpClient.get_instance().common_fetch(MODIFY_DB_ENDPOINT, params.__dict__, GetDBConnectionResponse,
                                                          need_scope=False)

    @staticmethod
    def activate_connection(key: str):
        WaiiHttpClient.get_instance().set_scope(key)

    @staticmethod
    def get_activated_connection():
        return WaiiHttpClient.get_instance().get_scope()

    @staticmethod
    def get_default_connection():
        return WaiiHttpClient.get_instance().get_scope()

    @staticmethod
    def get_catalogs(params: GetCatalogRequest = GetCatalogRequest()) -> GetCatalogResponse:
        return WaiiHttpClient.get_instance().common_fetch(GET_CATALOG_ENDPOINT, params.__dict__, GetCatalogResponse)

    @staticmethod
    def update_table_description(params: UpdateTableDescriptionRequest) -> UpdateTableDescriptionResponse:
        return WaiiHttpClient.get_instance().common_fetch(UPDATE_TABLE_DESCRIPTION_ENDPOINT, params.__dict__,
                                                          GetCatalogResponse)

    @staticmethod
    def update_schema_description(params: UpdateSchemaDescriptionRequest) -> UpdateSchemaDescriptionResponse:
        return WaiiHttpClient.get_instance().common_fetch(UPDATE_SCHEMA_DESCRIPTION_ENDPOINT, params.__dict__,
                                                          GetCatalogResponse)
