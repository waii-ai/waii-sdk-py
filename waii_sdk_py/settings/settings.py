from enum import Enum

from waii_sdk_py.waii_http_client import WaiiHttpClient
from ..common import CommonRequest
from ..my_pydantic import BaseModel
from typing import Optional, List, Dict, Any

from ..user import CommonResponse

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


class ParameterInfo(BaseModel):
    value: Optional[Any]
    possible_values: Optional[List[Any]]


class ListParametersResponse(CommonResponse):
    parameters: Dict[str, ParameterInfo]


class Parameters(str, Enum):
    LIKED_QUERIES_ENABLED = "PUBLIC.LIKED_QUERIES.ENABLED"
    LIKED_QUERIES_LEARNING_MODE = "PUBLIC.LIKED_QUERIES.LEARNING_MODE"
    REFLECTION_ENABLED = "PUBLIC.REFLECTION.ENABLED"


class SettingsImpl:
    def __init__(self, http_client: WaiiHttpClient):
        self.http_client = http_client

    def update_parameter(
            self, params: UpdateParameterRequest
    ) -> CommonResponse:
        return self.http_client.common_fetch(
            UPDATE_PARAMETER_ENDPOINT, params.__dict__, CommonResponse
        )

    def list_parameters(
            self
    ) -> ListParametersResponse:
        return self.http_client.common_fetch(
            LIST_PARAMETER_ENDPOINT, CommonRequest().__dict__, ListParametersResponse
        )

    def delete_parameter(
            self, params: DeleteParameterRequest
    ) -> CommonResponse:
        return self.http_client.common_fetch(
            DELETE_PARAMETER_ENDPOINT, params.__dict__, CommonResponse
        )
