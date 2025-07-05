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

from enum import Enum
from typing import Optional, List, Union
from pydantic import Field

from ..my_pydantic import WaiiBaseModel
from ..common import LLMBasedRequest
from ..database import TableDefinition, ColumnDefinition, SchemaDefinition, Constraint
from ..semantic_context import SemanticStatement
from waii_sdk_py.utils import wrap_methods_with_async
from ..waii_http_client import WaiiHttpClient

GET_KNOWLEDGE_GRAPH_ENDPOINT = "get-knowledge-graph"


class GetKnowledgeGraphRequest(LLMBasedRequest):
    ask: str

    def trim(self):
        self.ask = self.ask.strip()


class KnowlegeGraphNodeType(str, Enum):
    table = "table"
    column = "column"
    schema = "schema"
    semantic_statement = "semantic_statement"


class KnowledgeGraphEdgeType(str, Enum):
    # join between two tables
    constraint = "constraint"
    # reference to a semantic context
    semantic_statement_reference = "semantic_statement_reference"
    table_to_column = "table_to_column"
    schema_to_table = "schema_to_table"


class KnowledgeGraphNode(WaiiBaseModel):
    id: str
    display_name: str
    entity_type: str  # Use str instead of enum, but can compare with KnowlegeGraphNodeType values
    entity: Union[TableDefinition, ColumnDefinition, SchemaDefinition, SemanticStatement] = Field(..., discriminator='entity_type')
    parent_entity: Optional[Union[TableDefinition, SchemaDefinition]] = Field(None, discriminator='entity_type')
    

class KnowledgeGraphEdge(WaiiBaseModel):
    edge_type: str  # Use str instead of enum, but can compare with KnowledgeGraphEdgeType values
    source_id: str
    target_id: str
    # when it is directed, it's from source to target
    # when it is undirected, it's just link between two nodes (source and target are interchangeable)
    directed: bool
    description: Optional[str] = None
    # when it is table to column or schema to table, we will keep the edge_entity to None
    edge_entity: Optional[Union[SemanticStatement, Constraint]] = Field(None, discriminator='entity_type')


class KnowledgeGraph(WaiiBaseModel):
    nodes: List[KnowledgeGraphNode]
    edges: List[KnowledgeGraphEdge]


class GetKnowledgeGraphResponse(WaiiBaseModel):
    graph: Optional[KnowledgeGraph] = None


class KnowledgeGraphImpl:
    
    def __init__(self, http_client: WaiiHttpClient):
        self.http_client = http_client
    
    def get_knowledge_graph(self, params: GetKnowledgeGraphRequest) -> GetKnowledgeGraphResponse:
        """
        Get a knowledge graph based on the provided parameters.
        
        Args:
            params: GetKnowledgeGraphRequest containing the query parameters
            
        Returns:
            GetKnowledgeGraphResponse containing the generated knowledge graph
        """
        return self.http_client.common_fetch(
            GET_KNOWLEDGE_GRAPH_ENDPOINT, params, GetKnowledgeGraphResponse
        )


class AsyncKnowledgeGraphImpl:
    def __init__(self, http_client: WaiiHttpClient):
        self._kg_impl = KnowledgeGraphImpl(http_client)
        wrap_methods_with_async(self._kg_impl, self)


# Use KnowledgeGraphClient to avoid conflict with KnowledgeGraph model class
KnowledgeGraphClient = KnowledgeGraphImpl(WaiiHttpClient.get_instance()) 