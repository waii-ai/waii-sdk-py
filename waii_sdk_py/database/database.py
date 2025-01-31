import inspect
import json
import warnings

from waii_sdk_py.waii_http_client import WaiiHttpClient
from ..common import LLMBasedRequest, CommonRequest, CheckOperationStatusResponse, CheckOperationStatusRequest
from ..my_pydantic import WaiiBaseModel, PrivateAttr
import re
from typing import Optional, List, Dict, Any, Union
from urllib.parse import urlparse, parse_qs
from enum import Enum

from ..user import CommonResponse
from ..utils.utils import to_async, wrap_methods_with_async

MODIFY_DB_ENDPOINT = "update-db-connect-info"
GET_CATALOG_ENDPOINT = "get-table-definitions"
UPDATE_TABLE_DESCRIPTION_ENDPOINT = "update-table-description"
UPDATE_SCHEMA_DESCRIPTION_ENDPOINT = "update-schema-description"
UPDATE_COLUMN_DESCRIPTION_ENDPOINT = "update-column-description"
UPDATE_CONSTRAINT_ENDPOINT = "update-constraint"
UPDATE_TABLE_DEFINITION_ENDPOINT = "update-table-definitions"
UPDATE_SIMILARITY_SEARCH_INDEX_ENDPOINT = "update-similarity-search-index"
GET_SIMILARITY_SEARCH_INDEX_ENDPOINT = "get-similarity-search-index"
DELETE_SIMILARITY_SEARCH_INDEX_ENDPOINT = "delete-similarity-search-index"
GET_SIMILARITY_SEARCH_INDEX_TABLE_ENDPOINT = "get-similarity-search-index-table"
CHECK_SIMILARITY_SEARCH_INDEX_STATUS_ENDPOINT = "check-similarity-search-index-status"


class SchemaName(WaiiBaseModel):
    schema_name: str
    database_name: Optional[str]


class TableName(WaiiBaseModel):
    table_name: str
    schema_name: Optional[str]
    database_name: Optional[str]


class ColumnName(WaiiBaseModel):
    table_name: TableName
    column_name: str


class ColumnSampleValues(WaiiBaseModel):
    values: Optional[Dict[str, int]]


class ColumnDefinition(WaiiBaseModel):
    name: str
    type: str
    comment: Optional[str]
    description: Optional[str]
    sample_values: Optional[ColumnSampleValues]

    def __lt__(self, other):
        return self.name < other.name


class ConstraintType(str, Enum):
    primary = "primary"
    foreign = "foreign"


class ConstraintDetectorType(str, Enum):
    database = "database"
    inferred_llm = "inferred_llm"
    inferred_static = "inferred_static"
    inferred_query_history = "inferred_query_history"
    manual = "manual"


class TableReference(WaiiBaseModel):
    src_table: Optional[TableName]  # table name
    src_cols: Optional[List[str]]  # source table columns
    ref_table: Optional[TableName]  # ref table name
    ref_cols: Optional[List[str]]  # ref table columns
    source: Optional[ConstraintDetectorType]


class TableNameToDescription(WaiiBaseModel):
    name: str
    description: str


class SchemaDescription(WaiiBaseModel):
    summary: Optional[str]
    common_questions: Optional[List[str]]
    common_tables: Optional[List[TableNameToDescription]]


class RelationshipType(str, Enum):
    one_to_one = "one_to_one"
    one_to_many = "one_to_many"
    many_to_many = "many_to_many"
    belongs_to = "belongs_to"
    has_one = "has_one"
    has_many = "has_many"
    many_to_one = "many_to_one"


class Constraint(WaiiBaseModel):
    source: Optional[ConstraintDetectorType]
    table: Optional[TableName]
    cols: Optional[List[str]]
    constraint_type: Optional[ConstraintType]
    relationship_type: Optional[RelationshipType]

    # for foreign key, it is the table and columns that the source table and cols
    src_table: Optional[TableName]  # table name
    src_cols: Optional[List[str]]  # source table columns

    # comment for the constraint
    comment: Optional[str]

    def __repr__(self):
        if self.constraint_type == ConstraintType.primary:
            return f"PK {self.table} ({self.cols} [{self.source.name}]"
        else:
            return f"FK {self.src_table} ({self.src_cols}) -> {self.table} ({self.cols}) [{self.source.name}]"



class TableDefinition(WaiiBaseModel):
    name: TableName
    columns: Optional[List[ColumnDefinition]]
    comment: Optional[str]
    last_altered_time: Optional[int]
    _refs: Optional[List[TableReference]] = PrivateAttr(default=[])
    constraints: Optional[List[Constraint]]
    inferred_refs: Optional[List[TableReference]]
    inferred_constraints: Optional[List[Constraint]]
    description: Optional[str]

    def __init__(self, **data):
        super().__init__(**data)
        refs_data = data.get("refs",None)
        refs = []
        if refs_data:
            for ref in refs_data:
                if type(ref) == TableReference:
                    refs.append(ref)
                else:
                    refs.append(TableReference(**ref))

        self._refs = refs

    @property
    def refs(self):
        warnings.warn(
            "The 'refs' attribute is deprecated and will be removed in a future release. Use 'constraints' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._refs

    @refs.setter
    def refs(self, value):
        warnings.warn(
            "The 'refs' attribute is deprecated and will be removed in a future release. Use 'constraints' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self._refs = value

class SchemaDefinition(WaiiBaseModel):
    name: SchemaName
    tables: Optional[List[TableDefinition]]
    description: Optional[SchemaDescription]


class CatalogDefinition(WaiiBaseModel):
    name: str
    schemas: Optional[List[SchemaDefinition]]

class DBContentFilterScope(str, Enum):
    schema = "schema"
    table = "table"
    column = "column"

class DBContentFilterType(str, Enum):
    include = "include"
    exclude = "exclude"

class DBContentFilterActionType(str, Enum):
    # this means we will include/exclude the content
    visibility = "visibility"

    # this means we will do sample value or not
    sample_values = "sample_values"


class FilterType(str, Enum):
    INCLUSION = "inclusion"
    EXCLUSION = "exclusion"


class SearchContext(WaiiBaseModel):
    type: Optional[FilterType] = FilterType.INCLUSION
    db_name: Optional[str] = '*'
    schema_name: Optional[str] = '*'
    table_name: Optional[str] = '*'
    column_name: Optional[str] = '*'
    ignore_case: Optional[bool] = True

class DBContentFilter(WaiiBaseModel):
    filter_scope: DBContentFilterScope
    filter_type: DBContentFilterType = DBContentFilterType.include
    filter_action_type: DBContentFilterActionType = DBContentFilterActionType.visibility
    ignore_case: Optional[bool] = True
    pattern: str  # regex pattern
    search_context: Optional[List[SearchContext]]


class DBAccessPolicy(WaiiBaseModel):
    read_only: Optional[bool] = False
    allow_access_beyond_db_content_filter: Optional[bool] = True
    allow_access_beyond_search_context: Optional[bool] = True

class DBConnection(WaiiBaseModel):
    key: Optional[str] = None
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
    sample_col_values: Optional[bool] = None
    push:Optional[bool] = False
    db_content_filters: Optional[List[DBContentFilter]] = None
    embedding_model: Optional[str] = None
    always_include_tables: Optional[List[TableName]] = None
    alias: Optional[str] = None
    db_access_policy: Optional[DBAccessPolicy] = DBAccessPolicy()
    host_alias : Optional[str] = None
    user_alias: Optional[str] = None
    db_alias: Optional[str] = None
    client_email: Optional[str] = None
    content_filters: Optional[List[SearchContext]] = None
    sample_filters: Optional[List[SearchContext]] = None

class ModifyDBConnectionRequest(WaiiBaseModel):
    updated: Optional[List[DBConnection]] = None
    removed: Optional[List[str]] = None
    validate_before_save: Optional[bool] = None
    user_id: Optional[str] = None
    default_db_connection_key: Optional[str] = None
    owner_user_id: Optional[str] = None


class SchemaIndexingStatus(WaiiBaseModel):
    n_pending_indexing_tables: int
    n_total_tables: int
    status: str


class DBConnectionIndexingStatus(WaiiBaseModel):
    status: Optional[str]
    schema_status: Optional[Dict[str, SchemaIndexingStatus]]


class ModifyDBConnectionResponse(CommonResponse):
    connectors: Optional[List[DBConnection]]
    diagnostics: Optional[str]
    default_db_connection_key: Optional[str]
    connector_status: Optional[Dict[str, DBConnectionIndexingStatus]]


class GetCatalogRequest(LLMBasedRequest):
    search_context: Optional[List[SearchContext]] = None

    # ask is to perform semantic search, if it is provided, then we will use it to search the table definition
    # we will try to find the same tables which can answer the ask
    ask: Optional[str] = None

    internal: bool = False


class GetDBConnectionRequest(CommonRequest):
    pass


class GetDBConnectionResponse(CommonResponse):
    connectors: Optional[List[DBConnection]]
    diagnostics: Optional[str] = None
    default_db_connection_key: Optional[str] = None
    connector_status: Optional[Dict[str, DBConnectionIndexingStatus]] = None


class GetCatalogResponse(CommonResponse):
    catalogs: Optional[List[CatalogDefinition]] = None
    debug_info: Optional[Dict[str, Any]]


class UpdateTableDescriptionRequest(WaiiBaseModel):
    table_name: TableName
    description: str


class UpdateTableDefinitionRequest(WaiiBaseModel):
    updated_tables: Optional[List[TableDefinition]]
    removed_tables: Optional[List[TableName]]


class ColumnDescription(WaiiBaseModel):
    column_name: str
    description: Optional[str]


class TableToColumnDescription(WaiiBaseModel):
    table_name: TableName
    column_descriptions: Optional[List[ColumnDescription]]


class UpdateColumnDescriptionRequest(WaiiBaseModel):
    col_descriptions: Optional[List[TableToColumnDescription]]


class UpdatedTableToCol(WaiiBaseModel):
    table_name: TableName
    column_names: Optional[List[str]]


class UpdateColumnDescriptionResponse(CommonResponse):
    updated_table_to_cols: Optional[List[UpdatedTableToCol]]

class UpdateTableDefinitionResponse(CommonResponse):
    updated_tables: Optional[List[TableName]]


class UpdateSchemaDescriptionRequest(WaiiBaseModel):
    schema_name: SchemaName
    description: str


class UpdateTableDescriptionResponse(CommonResponse):
    pass


class UpdateSchemaDescriptionResponse(CommonResponse):
    pass


class TableConstraints(WaiiBaseModel):
    table_name: TableName
    constraints: Optional[List[Constraint]]
    constraint_type: ConstraintType


class UpdateConstraintRequest(WaiiBaseModel):
    # updated constraints, it will replace the existing constraints
    updated_constraints: Optional[List[TableConstraints]]


class UpdateConstraintResponse(CommonResponse):
    updated_tables: Optional[List[TableName]]


class RefreshDBConnectionRequest(WaiiBaseModel):
    db_conn_key: str


class ColumnValue(WaiiBaseModel):
    value: str
    additional_info: Optional[List[str]]


class UpdateSimilaritySearchIndexRequest(CommonRequest):
    values: Optional[List[ColumnValue]]
    column: ColumnName
    enable_llm_rerank: Optional[bool] = True
    similarity_score_threshold: Optional[float] = None
    max_matched_values: Optional[int] = None
    min_matched_values: Optional[int] = None


class UpdateSimilaritySearchIndexResponse(CommonResponse):
    op_id: str


class GetSimilaritySearchIndexOnTableRequest(CommonRequest):
    table: TableName


class GetSimilaritySearchIndexOnTableResponse(CommonResponse):
    table: TableName
    columns: List[ColumnName]


class DeleteSimilaritySearchIndexRequest(CommonRequest):
    column: ColumnName

class DeleteSimilaritySearchIndexResponse(CommonResponse):
    op_id: Optional[str]


class GetSimilaritySearchIndexRequest(CommonRequest):
    column: ColumnName


class GetSimilaritySearchIndexResponse(CommonRequest):
    column: ColumnName
    values: Optional[List[ColumnValue]]


class DatabaseImpl:

    def __init__(self, http_client: WaiiHttpClient):
        self.http_client = http_client

    def modify_connections(
        self, params: ModifyDBConnectionRequest
    ) -> ModifyDBConnectionResponse:
        if params.updated is not None:
            self._modify_connection_request(params.updated)
        return self.http_client.common_fetch(
            MODIFY_DB_ENDPOINT, params, ModifyDBConnectionResponse
        )


    def _modify_connection_request(self, conns:List[DBConnection]):
        for conn in conns:
            if conn.db_type == "bigquery" and conn.password:
                password_dict = json.loads(conn.password)
                conn.database = password_dict['project_id']
                conn.client_email = password_dict['client_email']




    def get_connections(
        self, params: Optional[GetDBConnectionRequest] = None
    ) -> GetDBConnectionResponse:
        if params == None:
            params = GetDBConnectionRequest()
        return self.http_client.common_fetch(
            MODIFY_DB_ENDPOINT,
            params,
            GetDBConnectionResponse,
            need_scope=False,
        )

    def activate_connection(self, key: str):
        self.http_client.set_scope(key)

    def get_activated_connection(self):
        return self.http_client.get_scope()

    def get_default_connection(self):
        return self.http_client.get_scope()

    def get_catalogs(
        self, params: Optional[GetCatalogRequest] = None
    ) -> GetCatalogResponse:
        if params == None:
            params = GetCatalogRequest()
        return self.http_client.common_fetch(
            GET_CATALOG_ENDPOINT, params, GetCatalogResponse
        )

    def update_table_description(
        self, params: UpdateTableDescriptionRequest
    ) -> UpdateTableDescriptionResponse:
        return self.http_client.common_fetch(
            UPDATE_TABLE_DESCRIPTION_ENDPOINT, params, GetCatalogResponse
        )

    def update_table_definition(
        self, params:UpdateTableDefinitionRequest
    ) -> UpdateTableDefinitionResponse:
        return self.http_client.common_fetch(
            UPDATE_TABLE_DEFINITION_ENDPOINT, params,UpdateTableDefinitionResponse
        )

    def update_schema_description(
        self, params: UpdateSchemaDescriptionRequest
    ) -> UpdateSchemaDescriptionResponse:
        return self.http_client.common_fetch(
            UPDATE_SCHEMA_DESCRIPTION_ENDPOINT, params, GetCatalogResponse
        )

    def update_column_description(
        self, params: UpdateColumnDescriptionRequest
    ) -> UpdateColumnDescriptionResponse:
        return self.http_client.common_fetch(
            UPDATE_COLUMN_DESCRIPTION_ENDPOINT,
            params,
            UpdateColumnDescriptionResponse,
        )

    def update_constraint(
        self, params: UpdateConstraintRequest
    ) -> UpdateConstraintResponse:
        return self.http_client.common_fetch(
            UPDATE_CONSTRAINT_ENDPOINT, params, UpdateConstraintResponse
        )

    def refresh_db_connection(self):
        return self.http_client.common_fetch(
            "refresh-db-connection",
            {
                "db_conn_key": self.get_activated_connection(),
            },
            CommonResponse,
        )

    def update_similarity_search_index(
            self, params: UpdateSimilaritySearchIndexRequest
    ) -> CommonResponse:
        return self.http_client.common_fetch(
            UPDATE_SIMILARITY_SEARCH_INDEX_ENDPOINT, params, UpdateSimilaritySearchIndexResponse
        )

    def get_similarity_search_index(
            self, params: GetSimilaritySearchIndexRequest
    ) -> GetSimilaritySearchIndexResponse:
        return self.http_client.common_fetch(
            GET_SIMILARITY_SEARCH_INDEX_ENDPOINT, params, GetSimilaritySearchIndexResponse
        )

    def delete_similarity_search_index(
            self, params: DeleteSimilaritySearchIndexRequest
    ) -> CommonResponse:
        return self.http_client.common_fetch(
            DELETE_SIMILARITY_SEARCH_INDEX_ENDPOINT, params, DeleteSimilaritySearchIndexResponse
        )

    def get_similarity_search_index_on_table(
            self, params: GetSimilaritySearchIndexOnTableRequest
    ) -> GetSimilaritySearchIndexOnTableResponse:
        return self.http_client.common_fetch(
            GET_SIMILARITY_SEARCH_INDEX_TABLE_ENDPOINT, params, GetSimilaritySearchIndexOnTableResponse
        )

    def get_similarity_search_index_status(
            self, params: CheckOperationStatusRequest
    ) -> CheckOperationStatusResponse:
        return self.http_client.common_fetch(
            CHECK_SIMILARITY_SEARCH_INDEX_STATUS_ENDPOINT, params, CheckOperationStatusResponse
        )


class AsyncDatabaseImpl:
    def __init__(self, http_client: WaiiHttpClient):
        self._database_impl = DatabaseImpl(http_client)
        wrap_methods_with_async(self._database_impl, self)



Database = DatabaseImpl(WaiiHttpClient.get_instance())
