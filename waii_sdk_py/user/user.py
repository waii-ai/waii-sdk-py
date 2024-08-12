from typing import Optional, List

from waii_sdk_py.waii_http_client import WaiiHttpClient
from pydantic import BaseModel

LIST_ACCESS_KEY_ENDPOINT = "list-access-keys"
DELETE_ACCESS_KEY_ENDPOINT = "delete-access-keys"
CREATE_KEY_ENDPOINT = "create-key"


class CreateAccessKeyRequest(BaseModel):
    name: str

class AccessKey(BaseModel):
    access_key: str
    user_id: str
    description: Optional[str]
    name: Optional[str]
    created_at: Optional[int]

class GetAccessKeyResponse(BaseModel):
    access_keys: Optional[List[AccessKey]]

class GetAccessKeyRequest(BaseModel):
    pass


class DelAccessKeyRequest(BaseModel):
    names:List[str]
class DelAccessKeyResponse(BaseModel):
    pass


class UserImpl:

    def __init__(self, http_client: WaiiHttpClient):
        self.http_client = http_client

    def create_access_key(self, params:CreateAccessKeyRequest):
        return self.http_client.common_fetch(
            CREATE_KEY_ENDPOINT, params.__dict__, GetAccessKeyResponse
        )

    def list_access_keys(self, params:GetAccessKeyRequest):
        return self.http_client.common_fetch(LIST_ACCESS_KEY_ENDPOINT,params.__dict__, GetAccessKeyResponse)

    def delete_access_key(self, params:DelAccessKeyRequest):
        return self.http_client.common_fetch(DELETE_ACCESS_KEY_ENDPOINT, params.__dict__,DelAccessKeyResponse)


User = UserImpl(WaiiHttpClient.get_instance())