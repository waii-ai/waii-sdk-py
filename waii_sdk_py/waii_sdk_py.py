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

from contextlib import contextmanager
from typing import Optional, List

from .access_rules import AccessRuleImpl, AsyncAccessRuleImpl
from .chart import ChartImpl, Chart, AsyncChartImpl
from .chat import ChatImpl, Chat, AsyncChatImpl
from .history import HistoryImpl, History, AsyncHistoryImpl
from .query import QueryImpl, Query, AsyncQueryImpl
from .database import DatabaseImpl, Database, AsyncDatabaseImpl
from .semantic_context import SemanticContextImpl, SemanticContext, AsyncSemanticContextImpl
from .settings import SettingsImpl, AsyncSettingsImpl
from .user import UserImpl, AsyncUserImpl
from .user.user_static import User
from .waii_http_client import WaiiHttpClient
import importlib.metadata
from .my_pydantic import WaiiBaseModel
from .semantic_layer_dump import SemanticLayerDumpImpl, SemanticLayerDump
from .kg import KnowledgeGraphImpl, AsyncKnowledgeGraphImpl

GET_MODELS_ENDPOINT = "get-models"


class GetModelsRequest(WaiiBaseModel):
    pass


class ModelType(WaiiBaseModel):
    name: str
    description: Optional[str]
    vendor: Optional[str]


class GetModelsResponse(WaiiBaseModel):
    models: Optional[List[ModelType]]


class Waii:

    def __init__(self, initialize_legacy_fields: bool = False):
        self.history = None
        self.query = None
        self.database = None
        self.semantic_context = None
        self.chat = None
        self.chart = None
        self.user = None
        self.access_rules = None
        self.settings = None
        self.knowledge_graph = None
        self.initialize_legacy_fields = initialize_legacy_fields
        self.http_client = None


    def initialize(self, url: str = "https://tweakit.waii.ai/api/", api_key: str = "", verbose=False):
        http_client = WaiiHttpClient(url, api_key, verbose=verbose)
        self.http_client = http_client
        self.history = HistoryImpl(http_client)
        self.query = QueryImpl(http_client)
        self.database = DatabaseImpl(http_client)
        self.semantic_context = SemanticContextImpl(http_client)
        self.chat = ChatImpl(http_client)
        self.chart = ChartImpl(http_client)
        self.user = UserImpl(http_client)
        self.access_rules = AccessRuleImpl(http_client)
        self.settings = SettingsImpl(http_client)
        self.semantic_layer_dump = SemanticLayerDumpImpl(http_client)
        self.knowledge_graph = KnowledgeGraphImpl(http_client)

        if self.initialize_legacy_fields:
            self.History = self.history
            self.Query = self.query
            self.Database = self.database
            self.SemanticContext = self.semantic_context
            self.Chart = self.chart
            self.Chat = self.chat
            self.User = self.user
            self.SemanticLayerDump = self.semantic_layer_dump
            self.KnowledgeGraph = self.knowledge_graph
            Query.http_client = http_client
            History.http_client = http_client
            Database.http_client = http_client
            SemanticContext.http_client = http_client
            User.http_client = http_client
            Chat.http_client = http_client
            Chart.http_client = http_client
            SemanticLayerDump.http_client = http_client

        conns = self.database.get_connections().connectors
        if len(conns) > 0:
            self.database.activate_connection(conns[0].key)

    @staticmethod
    def version():
        return importlib.metadata.version('waii-sdk-py')

    def get_models(self, params: GetModelsRequest = GetModelsRequest()) -> GetModelsResponse:
        return self.http_client.common_fetch(
            GET_MODELS_ENDPOINT, params, GetModelsResponse
        )

    @contextmanager
    def impersonate_user(self, user_id: str):
        try:
            self.http_client.set_impersonate_user_id(user_id)
            yield
        finally:
            self.clear_impersonation()

    def set_impersonate_user(self, user_id: str):
        self.http_client.set_impersonate_user_id(user_id)

    def clear_impersonation(self):
        self.http_client.set_impersonate_user_id('')

WAII = Waii(True)

class AsyncWaii:

    def __init__(self):
        self.http_client = None
        self.query = None
        self.database = None
        self.semantic_context = None
        self.chat = None
        self.chart = None
        self.user = None
        self.access_rules = None
        self.settings = None
        self.history = None
        self.knowledge_graph = None




    async def initialize(self, url: str = "https://tweakit.waii.ai/api/", api_key: str = "", verbose=False):
        http_client = WaiiHttpClient(url, api_key, verbose=verbose)
        self.http_client = http_client
        self.query = AsyncQueryImpl(http_client)
        self.database = AsyncDatabaseImpl(http_client)
        self.semantic_context = AsyncSemanticContextImpl(http_client)
        self.chat = AsyncChatImpl(http_client)
        self.chart = AsyncChartImpl(http_client)
        self.user = AsyncUserImpl(http_client)
        self.access_rules = AsyncAccessRuleImpl(http_client)
        self.settings = AsyncSettingsImpl(http_client)
        self.history = AsyncHistoryImpl(http_client)
        self.knowledge_graph = AsyncKnowledgeGraphImpl(http_client)
        result = await self.database.get_connections()

        conns = result.connectors
        if len(conns) > 0:
            await self.database.activate_connection(conns[0].key)

    @staticmethod
    def version():
        return importlib.metadata.version('waii-sdk-py')
