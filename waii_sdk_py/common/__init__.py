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
from typing import Optional, List, Dict, Any, Union

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
    info: Union[Optional[str], Any] = None


class AsyncObjectResponse(CommonResponse):
    uuid: str


class GetObjectRequest(CommonRequest):
    uuid: str
