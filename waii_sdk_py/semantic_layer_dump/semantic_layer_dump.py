"""
Copyright 2023–2025 Waii, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""


from waii_sdk_py.common import CheckOperationStatusRequest, CheckOperationStatusResponse
from waii_sdk_py.my_pydantic import WaiiBaseModel
from typing import List, Optional
from waii_sdk_py.database import SearchContext, SchemaDefinition
from waii_sdk_py.query import LikedQuery
from waii_sdk_py.semantic_context import SemanticStatement
from waii_sdk_py.waii_http_client.waii_http_client import WaiiHttpClient

from typing import Dict, Any, Union
from enum import Enum


IMPORT_SEMANTIC_DUMP = "semantic-layer/import"
EXPORT_SEMANTIC_DUMP = "semantic-layer/export"
IMPORT_SEMANTIC_DUMP_STATUS = "semantic-layer/import/status"
EXPORT_SEMANTIC_DUMP_STATUS = "semantic-layer/export/status"

class ExportSemanticLayerDumpRequest(WaiiBaseModel):
    db_conn_key: str
    search_context: List[SearchContext] = [SearchContext()]

class ExportSemanticLayerDumpResponse(WaiiBaseModel):
    op_id: str

class ImportSemanticLayerDumpRequest(WaiiBaseModel):
    db_conn_key: str
    configuration: Dict[str, Any]
    schema_mapping: Dict[str, str] = {}
    database_mapping: Dict[str, str] = {}
    search_context: List[SearchContext] = [SearchContext()]

class ImportSemanticLayerDumpResponse(WaiiBaseModel):
    op_id: str



class SemanticLayerDumpImpl:

    def __init__(self, http_client: WaiiHttpClient):
        self.http_client = http_client

    def export_dump(
            self, params: ExportSemanticLayerDumpRequest
    ) -> ExportSemanticLayerDumpResponse:
        return self.http_client.common_fetch(
            EXPORT_SEMANTIC_DUMP,
            params,
            ExportSemanticLayerDumpResponse
        )
    
    def import_dump(
            self, params: ImportSemanticLayerDumpRequest
    ) -> ImportSemanticLayerDumpResponse:
        return self.http_client.common_fetch(
            IMPORT_SEMANTIC_DUMP,
            params,
            ImportSemanticLayerDumpResponse
        )
    
    def import_dump_status(
            self, params: CheckOperationStatusRequest
    ) -> CheckOperationStatusResponse:
        return self.http_client.common_fetch(
            IMPORT_SEMANTIC_DUMP_STATUS,
            params,
            CheckOperationStatusResponse
        )
    
    def export_dump_status(
            self, params: CheckOperationStatusRequest
    ) -> CheckOperationStatusResponse:
        return self.http_client.common_fetch(
            EXPORT_SEMANTIC_DUMP_STATUS,
            params,
            CheckOperationStatusResponse
        )
    
SemanticLayerDump = SemanticLayerDumpImpl(WaiiHttpClient.get_instance())