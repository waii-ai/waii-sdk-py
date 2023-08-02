from History import History  # Assuming History is properly imported
from Query import Query  # Assuming Query is properly imported
from Database import Database  # Assuming Database is properly imported
from SemanticContext import SemanticContext  # Assuming SemanticContext is properly imported
from WaiiHttpClient import WaiiHttpClient  # Assuming WaiiHttpClient is properly imported

class WAII:
    History = History
    SemanticContext = SemanticContext
    Query = Query
    Database = Database

    @staticmethod
    def initialize(url: str = 'http://localhost:9859/api/', api_key: str = ''):
        WaiiHttpClient.getInstance(url, api_key)
