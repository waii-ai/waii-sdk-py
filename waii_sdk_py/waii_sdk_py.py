from .history import HistoryImpl, History
from .query import QueryImpl, Query
from .database import DatabaseImpl, Database
from .semantic_context import SemanticContextImpl, SemanticContext
from .waii_http_client import WaiiHttpClient


class Waii:

    def __init__(self, initialize_legacy_fields: bool = False):
        self.history = None
        self.query = None
        self.database = None
        self.semantic_context = None
        self.initialize_legacy_fields = initialize_legacy_fields

    def initialize(self, url: str = "https://tweakit.waii.ai/api/", api_key: str = ""):
        http_client = WaiiHttpClient(url, api_key)
        self.history = HistoryImpl(http_client)
        self.query = QueryImpl(http_client)
        self.database = DatabaseImpl(http_client)
        self.semantic_context = SemanticContextImpl(http_client)

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


WAII = Waii(True)
