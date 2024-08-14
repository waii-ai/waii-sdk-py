from enum import Enum
from typing import List, Optional

from ..chat import ChatRequest, ChatResponse
from ..my_pydantic import BaseModel
from ..query import GeneratedQuery, QueryGenerationRequest
from ..chart import ChartGenerationRequest, ChartGenerationResponse
from ..waii_http_client import WaiiHttpClient

LIST_ENDPOINT = "get-generated-query-history"
GET_ENDPOINT = "get-history"


class GeneratedHistoryEntryBase(BaseModel):
    history_type: str
    # milliseconds since epoch
    timestamp_ms: Optional[int]


class GeneratedChartHistoryEntry(GeneratedHistoryEntryBase):
    request: Optional[ChartGenerationRequest]
    response: Optional[ChartGenerationResponse]


class GeneratedChatHistoryEntry(GeneratedHistoryEntryBase):
    request: Optional[ChatRequest]
    response: Optional[ChatResponse]


class GeneratedHistoryEntryType(str, Enum):
    query = "query"
    chart = "chart"
    chat = "chat"


class GeneratedQueryHistoryEntry(GeneratedHistoryEntryBase):
    query: Optional[GeneratedQuery] = None
    request: Optional[QueryGenerationRequest] = None


class GetGeneratedQueryHistoryRequest(BaseModel):
    pass


class GetGeneratedQueryHistoryResponse(BaseModel):
    history: Optional[List[GeneratedQueryHistoryEntry]] = None


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


class GetHistoryResponse:
    def __init__(self, objs):
        self.history = []
        if 'history' not in objs:
            raise Exception(f"history is required, but not found in the response, {objs}")

        objs = objs['history']
        for h in objs:
            if 'history_type' not in h:
                raise Exception(f"history_type is required, but not found in the response, {h}")

            history_type = h['history_type']

            if history_type == GeneratedHistoryEntryType.query:
                self.history.append(GeneratedQueryHistoryEntry(**h))
            elif history_type == GeneratedHistoryEntryType.chart:
                self.history.append(GeneratedChartHistoryEntry(**h))
            elif history_type == GeneratedHistoryEntryType.chat:
                self.history.append(GeneratedChatHistoryEntry(**h))

class GetHistoryRequest(BaseModel):
    # by default include query for backward compatibility
    included_types: Optional[List[GeneratedHistoryEntryType]] = [GeneratedHistoryEntryType.query,
                                                                 GeneratedHistoryEntryType.chart,
                                                                 GeneratedHistoryEntryType.chat]

    # for pagination
    limit: Optional[int] = 1000
    offset: Optional[int] = 0

    # latest first (default)
    timestamp_sort_order: Optional[SortOrder] = SortOrder.desc

    # filter by uuid of the entry
    uuid_filter: Optional[str] = None

    # filter by the liked query flag, by default it will include both liked and unliked queries.
    # when this is set to not None, you must only include query as included_types.
    liked_query_filter: Optional[bool] = None


class HistoryImpl:
    def __init__(self, http_client: WaiiHttpClient):
        self.http_client = http_client

    # this is deprecated, use get() instead
    def list(
            self,
            params: GetGeneratedQueryHistoryRequest = GetGeneratedQueryHistoryRequest(),
    ) -> GetGeneratedQueryHistoryResponse:
        print("This method is deprecated, use get() instead")
        return self.http_client.common_fetch(
            LIST_ENDPOINT, params.__dict__, GetGeneratedQueryHistoryResponse
        )

    def get(
            self,
            params: GetHistoryRequest = GetHistoryRequest(),
    ) -> GetHistoryResponse:
        objs = self.http_client.common_fetch(
            GET_ENDPOINT, params.__dict__, ret_json=True
        )
        return GetHistoryResponse(objs)


History = HistoryImpl(WaiiHttpClient.get_instance())
