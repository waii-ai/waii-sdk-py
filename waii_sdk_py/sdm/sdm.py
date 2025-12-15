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

from typing import Optional, List
from waii_sdk_py.common import CommonRequest, CommonResponse
from waii_sdk_py.my_pydantic import WaiiBaseModel
from waii_sdk_py.waii_http_client.waii_http_client import WaiiHttpClient
from waii_sdk_py.utils import wrap_methods_with_async

INDEX_SDM_ENDPOINT = "index-sdm"
LIST_SDMS_ENDPOINT = "list-sdms"
DELETE_SDM_ENDPOINT = "delete-sdm"


class IndexSdmRequest(CommonRequest):
    db_id: str
    scope: str
    user_id: Optional[str] = None
    org_id: Optional[str] = None
    tenant_id: Optional[str] = None
    sdm_name: str
    content: Optional[str] = None
    path: Optional[str] = None


class IndexSdmResponse(CommonResponse):
    success: bool
    message: str


class SdmObjectInfo(WaiiBaseModel):
    api_name: str
    label: str
    object_type: str  # "sdm", "data_object", "calculated_measurement", "calculated_dimension"
    description: Optional[str] = None


class ListSdmsRequest(CommonRequest):
    db_id: str
    scope: str
    user_id: Optional[str] = None
    org_id: Optional[str] = None
    tenant_id: Optional[str] = None
    sdm_name: Optional[str] = None


class ListSdmsResponse(CommonResponse):
    objects: List[SdmObjectInfo]


class DeleteSdmRequest(CommonRequest):
    db_id: str
    scope: str
    user_id: Optional[str] = None
    org_id: Optional[str] = None
    tenant_id: Optional[str] = None
    sdm_name: Optional[str] = None


class DeleteSdmResponse(CommonResponse):
    success: bool
    message: str
    count: Optional[int] = None


class SdmImpl:

    def __init__(self, http_client: WaiiHttpClient):
        self.http_client = http_client

    def index_sdm(
            self, params: IndexSdmRequest
    ) -> IndexSdmResponse:
        return self.http_client.common_fetch(
            INDEX_SDM_ENDPOINT,
            params,
            IndexSdmResponse
        )

    def list_sdms(
            self, params: ListSdmsRequest
    ) -> ListSdmsResponse:
        return self.http_client.common_fetch(
            LIST_SDMS_ENDPOINT,
            params,
            ListSdmsResponse
        )

    def delete_sdm(
            self, params: DeleteSdmRequest
    ) -> DeleteSdmResponse:
        return self.http_client.common_fetch(
            DELETE_SDM_ENDPOINT,
            params,
            DeleteSdmResponse
        )


class AsyncSdmImpl:
    def __init__(self, http_client: WaiiHttpClient):
        self._sdm_impl = SdmImpl(http_client)
        wrap_methods_with_async(self._sdm_impl, self)


Sdm = SdmImpl(WaiiHttpClient.get_instance())

