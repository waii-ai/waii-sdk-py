from typing import List, Optional
from dataclasses import dataclass
from ..waii_http_client import WaiiHttpClient
from ..query import GeneratedQuery, QueryGenerationRequest

GET_ENDPOINT = 'get-generated-query-history'


@dataclass
class GeneratedQueryHistoryEntry:
    query: Optional[GeneratedQuery] = None
    request: Optional[QueryGenerationRequest] = None


@dataclass
class GetGeneratedQueryHistoryRequest:
    pass


@dataclass
class GetGeneratedQueryHistoryResponse:
    history: Optional[List[GeneratedQueryHistoryEntry]] = None


class History:
    @staticmethod
    def list(params: GetGeneratedQueryHistoryRequest = GetGeneratedQueryHistoryRequest()) -> GetGeneratedQueryHistoryResponse:
        return WaiiHttpClient.get_instance().common_fetch(GET_ENDPOINT, params.__dict__)
