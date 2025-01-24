from enum import Enum
from typing import Optional, List, Dict, Any

from ..my_pydantic import WaiiBaseModel

class CommonRequest(WaiiBaseModel):
    tags: Optional[List[str]] = None
    parameters: Optional[Dict[str, Any]] = None


class LLMBasedRequest(WaiiBaseModel):
    tags: Optional[List[str]] = None
    parameters: Optional[Dict[str, Any]] = None
    model: Optional[str] = None
    # should we use cache?
    use_cache: Optional[bool] = True


class CommonResponse(WaiiBaseModel):
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


class AsyncObjectResponse(CommonResponse):
    uuid: str


class GetObjectRequest(CommonRequest):
    uuid: str
