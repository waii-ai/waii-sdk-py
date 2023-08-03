from .history import History
from .query import Query
from .database import Database
from .semantic_context import SemanticContext
from .waii_http_client import WaiiHttpClient

class WAII:
    History = History
    SemanticContext = SemanticContext
    Query = Query
    Database = Database

    @staticmethod
    def initialize(url: str = 'http://localhost:9859/api/', api_key: str = ''):
        WaiiHttpClient.get_instance(url, api_key)
