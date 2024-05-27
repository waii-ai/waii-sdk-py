from typing import List, Optional
from ..my_pydantic import BaseModel

from ..waii_http_client import WaiiHttpClient
from ..query import GeneratedQuery, QueryGenerationRequest

GET_ENDPOINT = "get-generated-query-history"


class GeneratedQueryHistoryEntry(BaseModel):
    query: Optional[GeneratedQuery] = None
    request: Optional[QueryGenerationRequest] = None


class GetGeneratedQueryHistoryRequest(BaseModel):
    limit: Optional[int] = None
    offset: Optional[int] = None


class GetGeneratedQueryHistoryResponse(BaseModel):
    history: Optional[List[GeneratedQueryHistoryEntry]] = None


class HistoryImpl:
    def __init__(self, http_client: WaiiHttpClient):
        self.http_client = http_client

    def list(
        self,
        params: GetGeneratedQueryHistoryRequest = GetGeneratedQueryHistoryRequest(),
    ) -> GetGeneratedQueryHistoryResponse:
        return self.http_client.common_fetch(
            GET_ENDPOINT, params.__dict__, GetGeneratedQueryHistoryResponse
        )


History = HistoryImpl(WaiiHttpClient.get_instance())
