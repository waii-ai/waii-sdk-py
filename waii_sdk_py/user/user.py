from typing import Optional, List, Dict, Any

from waii_sdk_py.waii_http_client import WaiiHttpClient
from pydantic import BaseModel

LIST_ACCESS_KEY_ENDPOINT = "list-access-keys"
DELETE_ACCESS_KEY_ENDPOINT = "delete-access-keys"
CREATE_KEY_ENDPOINT = "create-key"
GET_USER_INFO_ENDPOINT = "get-user-info"
UPDATE_CONFIG_ENDPOINT = "update-config"
CREATE_USER_ENDPOINT = "create-user"
DELETE_USER_ENDPOINT = "delete-user"
UPDATE_USER_ENDPOINT = "update-user"
LIST_USERS_ENDPOINT = "list-users"




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


class GetUserInfoRequest:
    pass


class GetUserInfoResponse(BaseModel):
    id: str
    name: str
    email: str
    roles: List[str]
    permissions: List[str]


class UpdateConfigRequest(BaseModel):
    updated: Optional[Dict[str, Any]]
    deleted: Optional[List[str]]

class UpdateConfigResponse(BaseModel):
    configs: Dict[str, Any]

class UserDTO(BaseModel):
    id: str  # unique id for the user
    name: Optional[str]  # display name for the user
    tenant_id: Optional[str]  # tenant id for the user
    org_id: Optional[str]  # org id for the user
    variables: Optional[Dict[str, Any]]  # variables for the user
    roles: Optional[List[str]] = []  # roles for the user

class CreateUserRequest(BaseModel):
    user: UserDTO

class UpdateUserRequest(BaseModel):
    user: UserDTO

class DeleteUserRequest(BaseModel):
    id: str

class CommonResponse(BaseModel):
    pass

class ListUsersRequest(BaseModel):
    lookup_org_id: Optional[str]

class ListUsersResponse(CommonResponse):
    users: List[UserDTO]





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

    def get_user_info(self, params:GetUserInfoRequest):
        return self.http_client.common_fetch(GET_USER_INFO_ENDPOINT, params.__dict__,GetUserInfoResponse)

    def update_config(self, params:UpdateConfigRequest):
        return self.http_client.common_fetch(UPDATE_CONFIG_ENDPOINT, params.__dict__,UpdateConfigResponse)

    def create_user(self, params:CreateUserRequest):
        return self.http_client.common_fetch(CREATE_USER_ENDPOINT, params.__dict__,CommonResponse)

    def delete_user(self, params:DeleteUserRequest):
        return self.http_client.common_fetch(DELETE_USER_ENDPOINT, params.__dict__, CommonResponse)

    def update_user(self, params:UpdateUserRequest):
        return self.http_client.common_fetch(UPDATE_USER_ENDPOINT, params.__dict__, CommonResponse)

    def list_users(self, params:ListUsersRequest):
        return self.http_client.common_fetch(LIST_USERS_ENDPOINT, params.__dict__, ListUsersResponse)



User = UserImpl(WaiiHttpClient.get_instance())