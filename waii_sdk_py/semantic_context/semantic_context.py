from typing import List, Optional

from ..common import LLMBasedRequest, CommonRequest, CommonResponse
from ..database import SearchContext
from ..my_pydantic import WaiiBaseModel
from waii_sdk_py.utils import wrap_methods_with_async
from ..waii_http_client import WaiiHttpClient

MODIFY_ENDPOINT = 'update-semantic-context'
GET_ENDPOINT = 'get-semantic-context'
ENABLE_ENDPOINT = 'enable-semantic-context'
DISABLE_ENDPOINT = 'disable-semantic-context'


class SemanticStatementWarning(WaiiBaseModel):
    message: str


class SemanticStatement(WaiiBaseModel):
    id: Optional[str]
    statement: str
    labels: Optional[List[str]]
    scope: Optional[str]

    # always include this statement in the context, if data_type is specified in statement, then always_include is True
    # when data_type matches
    always_include: Optional[bool] = True

    # Check the application of the rule in a second step after query gen when the rule is within scope
    critical: Optional[bool] = False

    # Search keys for this statement, if not specified, then use statement as search key
    # you can specify multiple search keys, for example, if you have a CVE doc, you can search by CVE number, or library
    # name, etc.
    lookup_summaries: Optional[List[str]]

    # extract prompt from the statement, if not specified, then use statement as extract prompt
    summarization_prompt: Optional[str] = None

    # Whether this semantic statement is enabled
    enabled: Optional[bool] = True

    # Warnings associated with this semantic statement
    warnings: Optional[List[SemanticStatementWarning]] = None

    # filters for user, tenant and org
    user_id: Optional[str] = '*'
    tenant_id: Optional[str] = '*'
    org_id: Optional[str] = '*'

    semantic_constraint: Optional[str] = None


class ModifySemanticContextRequest(LLMBasedRequest):
    updated: Optional[List[SemanticStatement]] = None
    deleted: Optional[List[str]] = None


class GetSemanticContextRequestFilter(WaiiBaseModel):
    # do we want to filter "always_include" rules or not?
    # - None: both
    # - True: only return rules with always_include=True
    # - False: only return rules with always_include=False
    always_include: Optional[bool] = None

    # Filter by labels, scope, statement.
    # They are connected by "AND", and we use substring match for them
    # Match is case insensitive
    labels: Optional[List[str]] = None  # labels to filter the rules
    scope: Optional[str] = None  # scope to filter the rules
    statement: Optional[str] = None  # statement to filter the rules

class ModifySemanticContextResponse(WaiiBaseModel):
    updated: Optional[List[SemanticStatement]] = None
    deleted: Optional[List[str]] = None


class GetSemanticContextRequest(LLMBasedRequest):
    filter: GetSemanticContextRequestFilter = GetSemanticContextRequestFilter()
    offset: int = 0
    limit: int = 1000
    search_text: Optional[str] = None
    search_context: Optional[List[SearchContext]] = None


class GetSemanticContextResponse(WaiiBaseModel):
    semantic_context: Optional[List[SemanticStatement]] = None
    available_statements: Optional[int] = 0


class EnableSemanticContextRequest(CommonRequest):
    statement_ids: List[str]


class EnableSemanticContextResponse(CommonResponse):
    statement_ids: List[str]  # successfully enabled statement ids


class DisableSemanticContextRequest(CommonRequest):
    statement_ids: List[str]


class DisableSemanticContextResponse(CommonResponse):
    statement_ids: List[str]  # successfully disabled statement ids


class SemanticContextImpl:

    def __init__(self, http_client: WaiiHttpClient):
        self.http_client = http_client

    def modify_semantic_context(self, params: ModifySemanticContextRequest) -> ModifySemanticContextResponse:
        return self.http_client.common_fetch(MODIFY_ENDPOINT, params, ModifySemanticContextResponse)

    def get_semantic_context(self, params: Optional[GetSemanticContextRequest] = None) -> GetSemanticContextResponse:
        if params == None:
            params = GetSemanticContextRequest()
        return self.http_client.common_fetch(GET_ENDPOINT, params, GetSemanticContextResponse)

    def enable_semantic_context(self, params: EnableSemanticContextRequest) -> EnableSemanticContextResponse:
        return self.http_client.common_fetch(ENABLE_ENDPOINT, params, EnableSemanticContextResponse)

    def disable_semantic_context(self, params: DisableSemanticContextRequest) -> DisableSemanticContextResponse:
        return self.http_client.common_fetch(DISABLE_ENDPOINT, params, DisableSemanticContextResponse)


class AsyncSemanticContextImpl:
    def __init__(self, http_client: WaiiHttpClient):
        self._semantic_context_impl = SemanticContextImpl(http_client)
        wrap_methods_with_async(self._semantic_context_impl, self)


SemanticContext = SemanticContextImpl(WaiiHttpClient.get_instance())