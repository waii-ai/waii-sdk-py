
from waii_sdk_py.my_pydantic import WaiiBaseModel
from typing import List, Optional
from waii_sdk_py.database import SearchContext, SchemaDefinition
from waii_sdk_py.query import LikedQuery
from waii_sdk_py.semantic_context import SemanticStatement
from waii_sdk_py.waii_http_client.waii_http_client import WaiiHttpClient


GET_SEMANTIC_DUMP = "get-semantic-dump"

class Metadata(WaiiBaseModel):
    exported_at: str
    source_dialect: str
    source_database: str

class DatabaseConfig(WaiiBaseModel):
    content_filters: List[SearchContext]

class SemanticLayerDump(WaiiBaseModel):
    version: str
    metadata: Optional[Metadata] = None
    database: Optional[DatabaseConfig] = None
    schemas: Optional[List[SchemaDefinition]] = None
    semantic_context: Optional[List[SemanticStatement]] = None
    liked_queries: Optional[List[LikedQuery]] = None

class GetSemanticLayerDumpRequest(WaiiBaseModel):
    db_conn_key: str
    search_context: SearchContext

class GetSemanticLayerDumpResponse(WaiiBaseModel):
    dump: SemanticLayerDump

class SemanticLayerDumpImpl:

    def __init__(self, http_client: WaiiHttpClient):
        self.http_client = http_client

    def get_dump(
            self, params: GetSemanticLayerDumpRequest
    ) -> GetSemanticLayerDumpResponse:
        return self.http_client.common_fetch(
            GET_SEMANTIC_DUMP,
            params,
            GetSemanticLayerDumpResponse
        )
    
SemanticLayerDumps = SemanticLayerDumpImpl(WaiiHttpClient.get_instance())