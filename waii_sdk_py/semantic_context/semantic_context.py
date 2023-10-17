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


class ModifySemanticContextRequest(BaseModel):
    updated: Optional[List[SemanticStatement]] = None
    deleted: Optional[List[str]] = None


class ModifySemanticContextResponse(BaseModel):
    updated: Optional[List[SemanticStatement]] = None
    deleted: Optional[List[str]] = None


class GetSemanticContextRequest(BaseModel):
    pass


class GetSemanticContextResponse(BaseModel):
    semantic_context: Optional[List[SemanticStatement]] = None


class SemanticContext:
    @staticmethod
    def modify_semantic_context(params: ModifySemanticContextRequest) -> ModifySemanticContextResponse:
        return WaiiHttpClient.get_instance().common_fetch(MODIFY_ENDPOINT, params.__dict__, ModifySemanticContextResponse)

    @staticmethod
    def get_semantic_context(params: GetSemanticContextRequest = GetSemanticContextRequest()) -> GetSemanticContextResponse:
        return WaiiHttpClient.get_instance().common_fetch(GET_ENDPOINT, params.__dict__, GetSemanticContextResponse)
