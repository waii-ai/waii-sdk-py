from uuid import uuid4
from typing import List, Dict, Optional
from pydantic import BaseModel
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
    # - True: only return rules with always_include=True
    # - False: only return rules with always_include=False
    always_include: bool = True

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


class SemanticContext:
    @staticmethod
    def modify_semantic_context(params: ModifySemanticContextRequest) -> ModifySemanticContextResponse:
        return WaiiHttpClient.get_instance().common_fetch(MODIFY_ENDPOINT, params.__dict__, ModifySemanticContextResponse)

    @staticmethod
    def get_semantic_context(params: GetSemanticContextRequest = GetSemanticContextRequest()) -> GetSemanticContextResponse:
        return WaiiHttpClient.get_instance().common_fetch(GET_ENDPOINT, params.__dict__, GetSemanticContextResponse)
