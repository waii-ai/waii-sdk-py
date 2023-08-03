from uuid import uuid4
from typing import List, Dict, Optional
from ..waii_http_client import WaiiHttpClient

MODIFY_ENDPOINT = 'update-semantic-context'
GET_ENDPOINT = 'get-semantic-context'

class SemanticStatement:
    def __init__(self, scope: str = '*', statement: str = '', labels: List[str] = None):
        self.id = str(uuid4())
        self.scope = scope
        self.statement = statement
        self.labels = labels if labels else []


class ModifySemanticContextRequest:
    def __init__(self, updated: Optional[List[SemanticStatement]] = None, deleted: Optional[List[str]] = None):
        self.updated = updated
        self.deleted = deleted


class ModifySemanticContextResponse:
    def __init__(self, updated: Optional[List[SemanticStatement]] = None, deleted: Optional[List[str]] = None):
        self.updated = updated
        self.deleted = deleted


class GetSemanticContextRequest:
    def __init__(self):
        pass


class GetSemanticContextResponse:
    def __init__(self, semantic_context: Optional[List[SemanticStatement]] = None):
        self.semantic_context = semantic_context


class SemanticContext:
    @staticmethod
    def modify_semantic_context(params: ModifySemanticContextRequest) -> ModifySemanticContextResponse:
        return WaiiHttpClient.get_instance().common_fetch(MODIFY_ENDPOINT, params.__dict__)

    @staticmethod
    def get_semantic_context(params: GetSemanticContextRequest = GetSemanticContextRequest()) -> GetSemanticContextResponse:
        return WaiiHttpClient.get_instance().common_fetch(GET_ENDPOINT, params.__dict__)
