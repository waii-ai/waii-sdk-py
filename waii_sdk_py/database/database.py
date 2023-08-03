from typing import List, Optional
from dataclasses import dataclass
from waii_sdk_py.waii_http_client import WaiiHttpClient

MODIFY_DB_ENDPOINT = 'update-db-connect-info'
GET_CATALOG_ENDPOINT = 'get-table-definitions'


@dataclass
class DBConnection:
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
    parameters: Optional[dict] = None


@dataclass
class ModifyDBConnectionRequest:
    updated: Optional[List[DBConnection]] = None
    removed: Optional[List[str]] = None
    validate_before_save: Optional[bool] = None
    user_id: Optional[str] = None


@dataclass
class ModifyDBConnectionResponse:
    connectors: Optional[List[DBConnection]] = None
    diagnostics: Optional[List[str]] = None


@dataclass
class GetDBConnectionRequest:
    pass


@dataclass
class GetDBConnectionResponse:
    connectors: Optional[List[DBConnection]] = None
    diagnostics: Optional[List[str]] = None


@dataclass
class SearchContext:
    db_name: Optional[str] = None
    schema_name: Optional[str] = None
    table_name: Optional[str] = None


@dataclass
class TableDescriptionPair:
    name: str
    description: str


@dataclass
class SchemaDescription:
    summary: Optional[str] = None
    common_questions: Optional[List[str]] = None
    common_tables: Optional[List[TableDescriptionPair]] = None


@dataclass
class SchemaName:
    schema_name: str
    database_name: Optional[str] = None


@dataclass
class TableName:
    table_name: str
    schema_name: Optional[str] = None
    database_name: Optional[str] = None


@dataclass
class TableReference:
    src_table: Optional[List[TableName]] = None
    src_cols: Optional[List[str]] = None
    ref_table: Optional[List[TableName]] = None
    ref_cols: Optional[List[str]] = None


@dataclass
class ColumnSampleValues:
    values: Optional[List[dict]] = None


@dataclass
class Column:
    name: str
    type: str
    comment: Optional[str] = None
    sample_values: Optional[List[ColumnSampleValues]] = None


@dataclass
class Table:
    name: TableName
    columns: Optional[List[Column]] = None
    comment: Optional[str] = None
    last_altered_time: Optional[int] = None
    refs: Optional[List[TableReference]] = None
    description: Optional[str] = None


@dataclass
class Schema:
    name: SchemaName
    tables: Optional[List[Table]] = None
    description: Optional[List[SchemaDescription]] = None


@dataclass
class Catalog:
    name: str
    schemas: Optional[List[Schema]] = None


@dataclass
class GetCatalogRequest:
    pass


@dataclass
class GetCatalogResponse:
    catalogs: Optional[List[Catalog]] = None


class Database:
    @staticmethod
    def modify_connections(params: ModifyDBConnectionRequest) -> ModifyDBConnectionResponse:
        return WaiiHttpClient.get_instance().common_fetch(MODIFY_DB_ENDPOINT, params.__dict__)

    @staticmethod
    def get_connections(params: GetDBConnectionRequest = GetDBConnectionRequest()) -> GetDBConnectionResponse:
        return WaiiHttpClient.get_instance().common_fetch(MODIFY_DB_ENDPOINT, params.__dict__)

    @staticmethod
    def activate_connection(key: str):
        WaiiHttpClient.get_instance().set_scope(key)

    @staticmethod
    def get_catalogs(params: GetCatalogRequest = GetCatalogRequest()) -> GetCatalogResponse:
        return WaiiHttpClient.get_instance().common_fetch(GET_CATALOG_ENDPOINT, params.__dict__)
