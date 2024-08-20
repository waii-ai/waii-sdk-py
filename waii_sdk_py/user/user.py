from typing import Optional, List, Dict, Any

from waii_sdk_py.common import CommonRequest, CommonResponse
from waii_sdk_py.waii_http_client import WaiiHttpClient
from ..my_pydantic import BaseModel

LIST_ACCESS_KEY_ENDPOINT = "list-access-keys"
DELETE_ACCESS_KEY_ENDPOINT = "delete-access-keys"
CREATE_KEY_ENDPOINT = "create-key"
GET_USER_INFO_ENDPOINT = "get-user-info"
UPDATE_CONFIG_ENDPOINT = "update-config"
CREATE_USER_ENDPOINT = "create-user"
DELETE_USER_ENDPOINT = "delete-user"
UPDATE_USER_ENDPOINT = "update-user"
LIST_USERS_ENDPOINT = "list-users"
CREATE_TENANT_ENDPOINT = "create-tenant"
UPDATE_TENANT_ENDPOINT = "update-tenant"
DELETE_TENANT_ENDPOINT = "delete-tenant"
LIST_TENANTS_ENDPOINT = "list-tenants"
CREATE_ORG_ENDPOINT = "create-org"
UPDATE_ORG_ENDPOINT = "update-org"
DELETE_ORG_ENDPOINT = "delete-org"
LIST_ORGS_ENDPOINT = "list-orgs"


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
    names: List[str]


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


class Organization(BaseModel):
    id: str  # unique id for the organization
    name: str  # display name for the organization
    variables: Optional[Dict[str, Any]]  # variables for the organization


class Tenant(BaseModel):
    id: str  # unique id for the tenant
    name: str  # display name for the tenant
    org_id: Optional[str]  # org id for the tenant
    variables: Optional[Dict[str, Any]]  # variables for the tenant


class User(BaseModel):
    id: str  # unique id for the user
    name: Optional[str]  # display name for the user
    tenant_id: Optional[str]  # tenant id for the user
    org_id: Optional[str]  # org id for the user
    variables: Optional[Dict[str, Any]]  # variables for the user
    roles: Optional[List[str]] = []  # roles for the user

# Roles of the user
class WaiiRoles:
    WAII_TRIAL_USER = 'waii-trial-user'
    WAII_USER = 'waii-user'
    WAII_API_USER = 'waii-api-user'
    WAII_ADMIN_USER = 'waii-admin-user'
    WAII_ORG_ADMIN_USER = 'waii-org-admin-user'
    WAII_SUPER_ADMIN_USER = 'waii-super-admin-user'

class CreateUserRequest(CommonRequest):
    user: User


class UpdateUserRequest(CommonRequest):
    user: User


class DeleteUserRequest(CommonRequest):
    id: str


class ListUsersRequest(CommonRequest):
    # lookup by org, by default it will lookup users within the same org
    lookup_org_id: Optional[str]

    # lookup by tenant, by default it will lookup all users within the org (depends on lookup_org_id)
    lookup_tenant_id: Optional[str]

    # lookup by user, by default it will return all users after apply the above filters
    lookup_user_id: Optional[str]


class ListUsersResponse(CommonResponse):
    users: List[User]


class CreateTenantRequest(BaseModel):
    tenant: Tenant


class UpdateTenantRequest(BaseModel):
    tenant: Tenant


class DeleteTenantRequest(BaseModel):
    id: str


class ListTenantsRequest(CommonRequest):
    lookup_org_id: Optional[str]


class ListTenantsResponse(CommonResponse):
    tenants: List[Tenant]


class CreateOrganizationRequest(BaseModel):
    organization: Organization


class UpdateOrganizationRequest(BaseModel):
    organization: Organization


class DeleteOrganizationRequest(BaseModel):
    id: str


class ListOrganizationsRequest(CommonRequest):
    pass


class ListOrganizationsResponse(CommonResponse):
    organizations: List[Organization]


class UserImpl:

    def __init__(self, http_client: WaiiHttpClient):
        self.http_client = http_client

    def create_access_key(self, params: CreateAccessKeyRequest):
        return self.http_client.common_fetch(
            CREATE_KEY_ENDPOINT, params.__dict__, GetAccessKeyResponse
        )

    def list_access_keys(self, params: GetAccessKeyRequest):
        return self.http_client.common_fetch(LIST_ACCESS_KEY_ENDPOINT, params.__dict__, GetAccessKeyResponse)

    def delete_access_key(self, params: DelAccessKeyRequest):
        return self.http_client.common_fetch(DELETE_ACCESS_KEY_ENDPOINT, params.__dict__, DelAccessKeyResponse)

    def get_user_info(self, params: GetUserInfoRequest):
        return self.http_client.common_fetch(GET_USER_INFO_ENDPOINT, params.__dict__, GetUserInfoResponse)

    def update_config(self, params: UpdateConfigRequest):
        return self.http_client.common_fetch(UPDATE_CONFIG_ENDPOINT, params.__dict__, UpdateConfigResponse)

    def create_user(self, params: CreateUserRequest):
        return self.http_client.common_fetch(CREATE_USER_ENDPOINT, params.__dict__, CommonResponse)

    def delete_user(self, params: DeleteUserRequest):
        return self.http_client.common_fetch(DELETE_USER_ENDPOINT, params.__dict__, CommonResponse)

    def update_user(self, params: UpdateUserRequest):
        return self.http_client.common_fetch(UPDATE_USER_ENDPOINT, params.__dict__, CommonResponse)

    def list_users(self, params: ListUsersRequest):
        return self.http_client.common_fetch(LIST_USERS_ENDPOINT, params.__dict__, ListUsersResponse)

    def create_tenant(self, params: CreateTenantRequest):
        return self.http_client.common_fetch(CREATE_TENANT_ENDPOINT, params.__dict__, CommonResponse)

    def update_tenant(self, params: UpdateTenantRequest):
        return self.http_client.common_fetch(UPDATE_TENANT_ENDPOINT, params.__dict__, CommonResponse)

    def delete_tenant(self, params: DeleteTenantRequest):
        return self.http_client.common_fetch(DELETE_TENANT_ENDPOINT, params.__dict__, CommonResponse)

    def list_tenants(self, params: ListTenantsRequest):
        return self.http_client.common_fetch(LIST_TENANTS_ENDPOINT, params.__dict__, ListTenantsResponse)

    def create_org(self, params: CreateOrganizationRequest):
        return self.http_client.common_fetch(CREATE_ORG_ENDPOINT, params.__dict__, CommonResponse)

    def update_org(self, params: UpdateOrganizationRequest):
        return self.http_client.common_fetch(UPDATE_ORG_ENDPOINT, params.__dict__, CommonResponse)

    def delete_org(self, params: DeleteOrganizationRequest):
        return self.http_client.common_fetch(DELETE_ORG_ENDPOINT, params.__dict__, CommonResponse)

    def list_orgs(self, params: ListOrganizationsRequest):
        return self.http_client.common_fetch(LIST_ORGS_ENDPOINT, params.__dict__, ListOrganizationsResponse)
