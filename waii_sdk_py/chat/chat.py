"""
Copyright 2023–2025 Waii, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from enum import Enum
from typing import Optional, List

from waii_sdk_py.database import SearchContext

from waii_sdk_py.semantic_context import SemanticStatement

from ..my_pydantic import WaiiBaseModel

from ..common import LLMBasedRequest, GetObjectRequest, AsyncObjectResponse
from ..query import GetQueryResultResponse, GeneratedQuery
from ..database import CatalogDefinition
from ..semantic_context import GetSemanticContextResponse
from ..chart import ChartGenerationResponse, ChartType
from waii_sdk_py.utils import wrap_methods_with_async
from ..waii_http_client import WaiiHttpClient

CHAT_MESSAGE_ENDPOINT = "chat-message"
SUBMIT_CHAT_MESSAGE_ENDPOINT = "submit-chat-message"
GET_CHAT_RESPONSE_ENDPOINT = "get-chat-response"


class ChatModule(str, Enum):
    DATA = "data"
    TABLES = "tables"
    QUERY = "query"
    CHART = "chart"
    CONTEXT = "context"


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

    additional_context: Optional[List[SemanticStatement]] = None

    search_context: Optional[List[SearchContext]] = None



class ChatResponseData(WaiiBaseModel):
    data: Optional[GetQueryResultResponse]
    query: Optional[GeneratedQuery]
    chart: Optional[ChartGenerationResponse]
    semantic_context: Optional[GetSemanticContextResponse]
    tables: Optional[CatalogDefinition]

class ChatResponseStep(str, Enum):
    routing_request = "Routing Request"
    generating_query = "Generating Query"
    retrieving_context = "Retrieving Context"
    retrieving_tables = "Retrieving Tables"
    running_query = "Running Query"
    generating_chart = "Generating Chart"
    preparing_result = "Preparing Result"
    completed = "Completed"


class ChatResponse(WaiiBaseModel):
    # template response
    response: Optional[str] = None
    current_step: Optional[ChatResponseStep] = None
    response_data: Optional[ChatResponseData]
    response_selected_fields: Optional[List[ChatModule]]
    is_new: Optional[bool] = False
    timestamp_ms: Optional[int]
    chat_uuid: str


class ChatImpl:

    def __init__(self, http_client: WaiiHttpClient):
        self.http_client = http_client

    def chat_message(self, params: ChatRequest) -> ChatResponse:
        return self.http_client.common_fetch(CHAT_MESSAGE_ENDPOINT, params, ChatResponse)

    def submit_chat_message(
            self, params: ChatRequest
    ) -> AsyncObjectResponse:
        return self.http_client.common_fetch(
            SUBMIT_CHAT_MESSAGE_ENDPOINT, params, AsyncObjectResponse
        )

    def get_chat_response(
            self, params: GetObjectRequest
    ) -> ChatResponse:
        return self.http_client.common_fetch(
            GET_CHAT_RESPONSE_ENDPOINT, params, ChatResponse
        )


class AsyncChatImpl:
    def __init__(self, http_client: WaiiHttpClient):
        self._chat_impl = ChatImpl(http_client)
        wrap_methods_with_async(self._chat_impl, self)


Chat = ChatImpl(WaiiHttpClient.get_instance())