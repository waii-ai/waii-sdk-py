from typing import List, Optional
from dataclasses import dataclass
from WaiiHttpClient import WaiiHttpClient  # Assuming WaiiHttpClient is properly imported
from Query import GeneratedQuery, QueryGenerationRequest  # Assuming these are the correct imports

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
        return WaiiHttpClient.getInstance().commonFetch(GET_ENDPOINT, params.__dict__)
