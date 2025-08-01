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
from typing import Optional, List, Dict, Union

from waii_sdk_py.database import SearchContext

from waii_sdk_py.semantic_context import SemanticStatement

from ..my_pydantic import WaiiBaseModel

from ..common import LLMBasedRequest, GetObjectRequest, AsyncObjectResponse, CommonRequest, CommonResponse
from ..query import GetQueryResultResponse, GeneratedQuery
from ..database import CatalogDefinition
from ..semantic_context import GetSemanticContextResponse
from ..chart import ChartGenerationResponse, ChartType
from waii_sdk_py.utils import wrap_methods_with_async
from ..waii_http_client import WaiiHttpClient

CHAT_MESSAGE_ENDPOINT = "chat-message"
SUBMIT_CHAT_MESSAGE_ENDPOINT = "submit-chat-message"
GET_CHAT_RESPONSE_ENDPOINT = "get-chat-response"

# Research template endpoints
CREATE_RESEARCH_TEMPLATE_ENDPOINT = "create-research-template"
GET_RESEARCH_TEMPLATE_ENDPOINT = "get-research-template"
LIST_RESEARCH_TEMPLATES_ENDPOINT = "list-research-templates"
UPDATE_RESEARCH_TEMPLATE_ENDPOINT = "update-research-template"
DELETE_RESEARCH_TEMPLATE_ENDPOINT = "delete-research-template"


class ChatModule(str, Enum):
    DATA = "data"
    TABLES = "tables"
    QUERY = "query"
    CHART = "chart"
    CONTEXT = "context"


class ChatRequestMode(str, Enum):
    automatic = "automatic"
    single_turn = "single_turn"
    multi_turn = "multi_turn"
    deep_research = "deep_research"


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

    mode: ChatRequestMode = ChatRequestMode.single_turn


class ChatResponseData(WaiiBaseModel):
    data: Optional[GetQueryResultResponse]
    query: Optional[GeneratedQuery]
    chart: Optional[ChartGenerationResponse]
    semantic_context: Optional[GetSemanticContextResponse]
    tables: Optional[CatalogDefinition]


class ChatResponseDataV2(WaiiBaseModel):
    data: Optional[Dict[str, GetQueryResultResponse]] = None
    query: Optional[Dict[str, GeneratedQuery]] = None
    chart: Optional[Dict[str, ChartGenerationResponse]] = None
    semantic_context: Optional[Dict[str, SemanticStatement]] = None
    tables: Optional[CatalogDefinition] = None

    error_info: Optional[dict] = None


class ChatResponseStep(str, Enum):
    routing_request = "Routing Request"
    generating_query = "Generating Query"
    retrieving_context = "Retrieving Context"
    retrieving_tables = "Retrieving Tables"
    running_query = "Running Query"
    generating_chart = "Generating Chart"
    preparing_result = "Preparing Result"
    completed = "Completed"


class ChatStatusUpdateEvent(WaiiBaseModel):
    title: Optional[str]
    summary: Optional[str]
    timestamp: Optional[int]
    step_status: Optional[str]  # in-progress and completed
    percentage: Optional[float]


class ChatResponse(WaiiBaseModel):
    # template response
    response: Optional[str] = None

    # use union for the two
    response_data: Optional[Union[ChatResponseData, ChatResponseDataV2]] = None
    is_new: Optional[bool] = False
    timestamp_ms: Optional[int] = None
    chat_uuid: str
    elapsed_time_ms: Optional[int] = None
    session_title: Optional[str] = None
    research_plan: Optional[str] = None

    # old way to display status, routing info, we have to keep it
    current_step: Optional[ChatResponseStep] = None
    routing_info: Optional[Dict[str, str]] = None
    response_selected_fields: Optional[List[ChatModule]] = None

    # newly added status update
    status_update_events: Optional[List[ChatStatusUpdateEvent]] = None


class ResearchTemplate(WaiiBaseModel):
    template_id: Optional[str] = None
    title: str
    template: str


class CreateResearchTemplateRequest(CommonRequest):
    research_template: ResearchTemplate


class GetResearchTemplateRequest(CommonRequest):
    template_id: str


class ListResearchTemplatesRequest(CommonRequest):
    limit: Optional[int] = 10
    search_text: Optional[str] = None


class GetResearchTemplateResponse(CommonResponse):
    research_template: Optional[ResearchTemplate] = None


class ListResearchTemplatesResponse(CommonResponse):
    research_templates: List[ResearchTemplate] = []


class UpdateResearchTemplateRequest(CommonRequest):
    research_template: ResearchTemplate


class DeleteResearchTemplateRequest(CommonRequest):
    template_id: str

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

    # Research Template Methods
    def create_research_template(self, params: CreateResearchTemplateRequest) -> CommonResponse:
        return self.http_client.common_fetch(
            CREATE_RESEARCH_TEMPLATE_ENDPOINT, params, CommonResponse
        )

    def get_research_template(self, params: GetResearchTemplateRequest) -> GetResearchTemplateResponse:
        return self.http_client.common_fetch(
            GET_RESEARCH_TEMPLATE_ENDPOINT, params, GetResearchTemplateResponse
        )

    def list_research_templates(self, params: ListResearchTemplatesRequest) -> ListResearchTemplatesResponse:
        return self.http_client.common_fetch(
            LIST_RESEARCH_TEMPLATES_ENDPOINT, params, ListResearchTemplatesResponse
        )

    def update_research_template(self, params: UpdateResearchTemplateRequest) -> CommonResponse:
        return self.http_client.common_fetch(
            UPDATE_RESEARCH_TEMPLATE_ENDPOINT, params, CommonResponse
        )

    def delete_research_template(self, params: DeleteResearchTemplateRequest) -> CommonResponse:
        return self.http_client.common_fetch(
            DELETE_RESEARCH_TEMPLATE_ENDPOINT, params, CommonResponse
        )



class AsyncChatImpl:
    def __init__(self, http_client: WaiiHttpClient):
        self._chat_impl = ChatImpl(http_client)
        wrap_methods_with_async(self._chat_impl, self)


Chat = ChatImpl(WaiiHttpClient.get_instance())