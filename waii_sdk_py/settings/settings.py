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

from waii_sdk_py.waii_http_client import WaiiHttpClient
from ..common import CommonRequest
from ..my_pydantic import WaiiBaseModel
from typing import Optional, List, Dict, Any

from ..user import CommonResponse
from waii_sdk_py.utils import wrap_methods_with_async
UPDATE_PARAMETER_ENDPOINT = "update-parameter"
LIST_PARAMETER_ENDPOINT = "list-parameters"
DELETE_PARAMETER_ENDPOINT = "delete-parameter"


class DeleteParameterRequest(CommonRequest):
    parameter: str
    target_org_id: Optional[str] = None
    target_tenant_id: Optional[str] = None
    target_user_id: Optional[str] = None
    target_connection_key: Optional[str] = None


class UpdateParameterRequest(CommonRequest):
    parameter: str
    value: Any
    target_org_id: Optional[str] = None
    target_tenant_id: Optional[str] = None
    target_user_id: Optional[str] = None
    target_connection_key: Optional[str] = None


class ParameterInfo(WaiiBaseModel):
    value: Optional[Any]
    possible_values: Optional[List[Any]]


class ListParametersResponse(CommonResponse):
    parameters: Dict[str, ParameterInfo]


class Parameters(str, Enum):
    LIKED_QUERIES_ENABLED = "PUBLIC.LIKED_QUERIES.ENABLED"
    LIKED_QUERIES_LEARNING_MODE = "PUBLIC.LIKED_QUERIES.LEARNING_MODE"
    REFLECTION_ENABLED = "PUBLIC.REFLECTION.ENABLED"
    GUARDRAIL_INVALID_QUESTION_CHECKER_ENABLED = "PUBLIC.GUARDRAIL.INVALID_QUESTION_CHECKER.ENABLED"
    QUERY_GENERATION_ANALYSIS_ENABLE_ALL = "PUBLIC.QUERY_GENERATION.ANALYSIS.ENABLE_ALL"
    DEEP_THINKING_ENABLED = "PUBLIC.DEEP_THINKING.ENABLED"

class SettingsImpl:
    def __init__(self, http_client: WaiiHttpClient):
        self.http_client = http_client

    def update_parameter(
            self, params: UpdateParameterRequest
    ) -> CommonResponse:
        return self.http_client.common_fetch(
            UPDATE_PARAMETER_ENDPOINT, params, CommonResponse
        )

    def list_parameters(
            self
    ) -> ListParametersResponse:
        return self.http_client.common_fetch(
            LIST_PARAMETER_ENDPOINT, CommonRequest(), ListParametersResponse
        )

    def delete_parameter(
            self, params: DeleteParameterRequest
    ) -> CommonResponse:
        return self.http_client.common_fetch(
            DELETE_PARAMETER_ENDPOINT, params, CommonResponse
        )


class AsyncSettingsImpl:
    def __init__(self, http_client: WaiiHttpClient):
        self._settings_impl = SettingsImpl(http_client)
        wrap_methods_with_async(self._settings_impl, self)
