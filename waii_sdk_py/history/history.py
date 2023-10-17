from typing import List, Optional
from pydantic import BaseModel

from ..waii_http_client import WaiiHttpClient
from ..query import GeneratedQuery, QueryGenerationRequest

GET_ENDPOINT = 'get-generated-query-history'


class GeneratedQueryHistoryEntry(BaseModel):
    query: Optional[GeneratedQuery] = None
    request: Optional[QueryGenerationRequest] = None


class GetGeneratedQueryHistoryRequest(BaseModel):
    limit: Optional[int] = None
    offset: Optional[int] = None


class GetGeneratedQueryHistoryResponse(BaseModel):
    history: Optional[List[GeneratedQueryHistoryEntry]] = None


class History:
    @staticmethod
    def list(params: GetGeneratedQueryHistoryRequest = GetGeneratedQueryHistoryRequest()) -> GetGeneratedQueryHistoryResponse:
        return WaiiHttpClient.get_instance().common_fetch(GET_ENDPOINT, params.__dict__, GetGeneratedQueryHistoryResponse)
