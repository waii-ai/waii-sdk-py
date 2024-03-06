from .history import  HistoryManager
from .query import QueryManager
from .database import DatabaseManager
from .semantic_context import SemanticContext
from .waii_http_client import WaiiHttpClient



class Waii:
    def __init__(self):
        self.history = None
        self.query = None
        self.database = None
        self.semantic_context = None

    def initialize(self,url: str = 'https://tweakit.waii.ai/api/', api_key: str = '' ):
        http_client = WaiiHttpClient.get_instance(url,api_key)
        self.history = HistoryManager(http_client)
        self.History = self.history
        self.query = QueryManager(http_client)
        self.Query = self.query
        self.database = DatabaseManager(http_client)
        self.Database = self.database
        self.semantic_context = SemanticContext(http_client)
        self.SemanticContext = self.semantic_context

        conns = self.database.get_connections().connectors
        if len(conns) > 0:
            self.database.activate_connection(conns[0].key)


WAII = Waii()
