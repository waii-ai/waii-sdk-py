from enum import Enum
from typing import Optional, List

from ..my_pydantic import BaseModel

from ..common import LLMBasedRequest
from ..query import GetQueryResultResponse, GeneratedQuery
from ..database import CatalogDefinition
from ..semantic_context import GetSemanticContextResponse
from ..chart import ChartGenerationResponse, ChartType
from ..waii_http_client import WaiiHttpClient

CHAT_MESSAGE_ENDPOINT = "chat-message"


class ChatModule(str, Enum):
    DATA = "data"
    TABLES = "tables"
    QUERY = "query"
    CHART = "chart"


class ChatRequest(LLMBasedRequest):
    ask: str

    # should we streaming the output?
    # no need to support for the first implementation
    streaming: bool = False

    # link to previous conversation, pick up where conversation left off
    parent_uuid: Optional[str]

    # optional chart type, default to plotly
    chart_type: Optional[ChartType]

    modules: Optional[List[ChatModule]]

    # optional by default there is no limit
    module_limit_in_response: Optional[int]


class ChatResponseData(BaseModel):
    data: Optional[GetQueryResultResponse]
    query: Optional[GeneratedQuery]
    chart: Optional[ChartGenerationResponse]
    semantic_context: Optional[GetSemanticContextResponse]
    tables: Optional[CatalogDefinition]


class ChatResponse(BaseModel):
    # template response
    response: str
    response_data: Optional[ChatResponseData]
    response_selected_fields: Optional[List[ChatModule]]
    is_new: Optional[bool] = False
    timestamp_ms: Optional[int]
    chat_uuid: str


class ChatImpl:

    def __init__(self, http_client: WaiiHttpClient):
        self.http_client = http_client

    def chat_message(self, params: ChatRequest) -> ChatResponse:
        return self.http_client.common_fetch(CHAT_MESSAGE_ENDPOINT, params.__dict__, ChatResponse)


Chat = ChatImpl(WaiiHttpClient.get_instance())