from typing import List, Optional
from ..my_pydantic import BaseModel
from ..waii_http_client import WaiiHttpClient

MODIFY_ENDPOINT = 'update-semantic-context'
GET_ENDPOINT = 'get-semantic-context'


class SemanticStatement(BaseModel):
    id: Optional[str]
    statement: str
    labels: Optional[List[str]]
    scope: Optional[str]

    # always include this statement in the context, if data_type is specified in statement, then always_include is True
    # when data_type matches
    always_include: Optional[bool] = True

    # Search keys for this statement, if not specified, then use statement as search key
    # you can specify multiple search keys, for example, if you have a CVE doc, you can search by CVE number, or library
    # name, etc.
    lookup_summaries: Optional[List[str]]

    # extract prompt from the statement, if not specified, then use statement as extract prompt
    summarization_prompt: Optional[str] = None


class ModifySemanticContextRequest(BaseModel):
    updated: Optional[List[SemanticStatement]] = None
    deleted: Optional[List[str]] = None


class GetSemanticContextRequestFilter(BaseModel):
    # do we want to filter "always_include" rules or not?
    # - None: both
    # - True: only return rules with always_include=True
    # - False: only return rules with always_include=False
    always_include: Optional[bool] = None

    # Filter by labels, scope, statement.
    # They are connected by "AND", and we use substring match for them
    # Match is case insensitive
    labels: Optional[List[str]]  # labels to filter the rules
    scope: Optional[str]  # scope to filter the rules
    statement: Optional[str]  # statement to filter the rules

class ModifySemanticContextResponse(BaseModel):
    updated: Optional[List[SemanticStatement]] = None
    deleted: Optional[List[str]] = None


class GetSemanticContextRequest(BaseModel):
    filter: GetSemanticContextRequestFilter = GetSemanticContextRequestFilter()
    offset = 0
    limit = 1000
    search_text: Optional[str] = None

class GetSemanticContextResponse(BaseModel):
    semantic_context: Optional[List[SemanticStatement]] = None

    available_statements: Optional[int] = 0


class SemanticContextImpl:

    def __init__(self, http_client: WaiiHttpClient):
        self.http_client = http_client

    def modify_semantic_context(self,params: ModifySemanticContextRequest) -> ModifySemanticContextResponse:
        return self.http_client.common_fetch(MODIFY_ENDPOINT, params.__dict__, ModifySemanticContextResponse)


    def get_semantic_context(self,params: GetSemanticContextRequest = GetSemanticContextRequest()) -> GetSemanticContextResponse:
        return self.http_client.common_fetch(GET_ENDPOINT, params.__dict__, GetSemanticContextResponse)


SemanticContext = SemanticContextImpl(WaiiHttpClient.get_instance())