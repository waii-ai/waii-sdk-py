from enum import Enum
from typing import Optional, List, Dict, Any

from ..my_pydantic import BaseModel


class CommonRequest(BaseModel):
    tags: Optional[List[str]]
    parameters: Optional[Dict[str, Any]]


class LLMBasedRequest(CommonRequest):
    model: Optional[str]
    # should we use cache?
    use_cache: Optional[bool] = True


class CommonResponse(BaseModel):
    pass


class CheckOperationStatusRequest(CommonRequest):
    op_id: str


class OperationStatus(str, Enum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    IN_PROGRESS = "in_progress"
    NOT_EXISTS = "not_exists"


class CheckOperationStatusResponse(CommonResponse):
    op_id: str
    status: OperationStatus
    info: Optional[str] = None
