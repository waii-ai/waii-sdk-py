from typing import Optional, List

from .chart import ChartImpl
from .chat import ChatImpl
from .history import HistoryImpl, History
from .query import QueryImpl, Query
from .database import DatabaseImpl, Database
from .semantic_context import SemanticContextImpl, SemanticContext
from .waii_http_client import WaiiHttpClient
import importlib.metadata
from pydantic import BaseModel

GET_MODELS_ENDPOINT = "get-models"


class GetModelsRequest(BaseModel):
    pass


class ModelType(BaseModel):
    name: str
    description: Optional[str]
    vendor: Optional[str]


class GetModelsResponse(BaseModel):
    models: Optional[List[ModelType]]


class Waii:

    def __init__(self, initialize_legacy_fields: bool = False):
        self.history = None
        self.query = None
        self.database = None
        self.semantic_context = None
        self.chat = None
        self.chart = None
        self.initialize_legacy_fields = initialize_legacy_fields
        self.http_client = None

    def initialize(self, url: str = "https://tweakit.waii.ai/api/", api_key: str = ""):
        http_client = WaiiHttpClient(url, api_key)
        self.http_client = http_client
        self.history = HistoryImpl(http_client)
        self.query = QueryImpl(http_client)
        self.database = DatabaseImpl(http_client)
        self.semantic_context = SemanticContextImpl(http_client)
        self.chat = ChatImpl(http_client)
        self.chart = ChartImpl(http_client)

        if self.initialize_legacy_fields:
            self.History = self.history
            self.Query = self.query
            self.Database = self.database
            self.SemanticContext = self.semantic_context
            Query.http_client = http_client
            History.http_client = http_client
            Database.http_client = http_client
            SemanticContext.http_client = http_client

        conns = self.database.get_connections().connectors
        if len(conns) > 0:
            self.database.activate_connection(conns[0].key)

    @staticmethod
    def version():
        return importlib.metadata.version('waii-sdk-py')

    def get_models(self, params: GetModelsRequest = GetModelsRequest()) -> GetModelsResponse:
        return self.http_client.common_fetch(
            GET_MODELS_ENDPOINT, params.__dict__, GetModelsResponse
        )


WAII = Waii(True)
