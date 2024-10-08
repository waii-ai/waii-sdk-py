from contextlib import contextmanager
from typing import Optional, List

from .access_rules import AccessRuleImpl
from .chart import ChartImpl, Chart
from .chat import ChatImpl, Chat
from .history import HistoryImpl, History
from .query import QueryImpl, Query
from .database import DatabaseImpl, Database
from .semantic_context import SemanticContextImpl, SemanticContext
from .settings import SettingsImpl
from .user import UserImpl
from .user.user_static import User
from .waii_http_client import WaiiHttpClient
import importlib.metadata
from .my_pydantic import BaseModel

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
        self.user = None
        self.access_rules = None
        self.settings = None
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

        if self.initialize_legacy_fields:
            self.History = self.history
            self.Query = self.query
            self.Database = self.database
            self.SemanticContext = self.semantic_context
            self.Chart = self.chart
            self.Chat = self.chat
            self.User = self.user
            Query.http_client = http_client
            History.http_client = http_client
            Database.http_client = http_client
            SemanticContext.http_client = http_client
            User.http_client = http_client
            Chat.http_client = http_client
            Chart.http_client = http_client


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
