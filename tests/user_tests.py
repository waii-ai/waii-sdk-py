import unittest

from tests.common_test_utils import org_exists, tenant_exists, user_exists
from waii_sdk_py.user import User as UserModel, BaseModel, DeleteTenantRequest, DeleteOrganizationRequest, \
    CreateOrganizationRequest, Organization, ListOrganizationsRequest, UpdateOrganizationRequest, CreateTenantRequest, \
    Tenant, ListTenantsRequest, UpdateTenantRequest
from waii_sdk_py import WAII
from waii_sdk_py.user import CreateAccessKeyRequest, DelAccessKeyRequest, DelAccessKeyResponse, GetAccessKeyRequest, \
    GetUserInfoRequest, GetUserInfoResponse, UpdateConfigRequest, CreateUserRequest, User, DeleteUserRequest, \
    CommonResponse, ListUsersRequest, UpdateUserRequest
from waii_sdk_py.waii_sdk_py import Waii


class TestUser(unittest.TestCase):
    def setUp(self):
        WAII.initialize(url="http://localhost:9859/api/")

    def test_create_access_key(self):
        params = DelAccessKeyRequest(names=["test1"])
        resp = WAII.User.delete_access_key(params)
        params = CreateAccessKeyRequest(name="test1")
        resp = WAII.User.create_access_key(params)
        test1_key = [key for key in resp.access_keys if key.name == "test1"]
        assert len(test1_key) > 0

    def test_delete_access_key(self):
        params = DelAccessKeyRequest(names=["test2"])
        resp = WAII.User.delete_access_key(params)
        params = CreateAccessKeyRequest(name="test2")
        resp = WAII.User.create_access_key(params)
        test2_key = [key for key in resp.access_keys if key.name == "test2"]
        assert len(test2_key) > 0

        params = GetAccessKeyRequest()
        resp = WAII.User.list_access_keys(params)
        test2_key = [key for key in resp.access_keys if key.name == "test2"]
        assert len(test2_key) > 0

        params = DelAccessKeyRequest(names=["test2"])
        resp = WAII.User.delete_access_key(params)
        assert isinstance(resp, DelAccessKeyResponse)

        params = GetAccessKeyRequest()
        resp = WAII.User.list_access_keys(params)
        test2_key = [key for key in resp.access_keys if key.name == "test2"]
        assert len(test2_key) == 0

    def test_list_access_keys(self):
        params = DelAccessKeyRequest(names=["test2"])
        resp = WAII.User.delete_access_key(params)

        params = GetAccessKeyRequest()
        resp = WAII.User.list_access_keys(params)
        test2_key = [key for key in resp.access_keys if key.name == "test2"]
        assert len(test2_key) == 0

        params = CreateAccessKeyRequest(name="test2")
        resp = WAII.User.create_access_key(params)
        test2_key = [key for key in resp.access_keys if key.name == "test2"]
        assert len(test2_key) > 0

        params = GetAccessKeyRequest()
        resp = WAII.User.list_access_keys(params)
        test2_key = [key for key in resp.access_keys if key.name == "test2"]
        assert len(test2_key) > 0

        params = DelAccessKeyRequest(names=["test2"])
        resp = WAII.User.delete_access_key(params)

    def test_get_user_info(self):
        params = GetUserInfoRequest()
        resp = WAII.User.get_user_info(params)
        assert isinstance(resp, GetUserInfoResponse)

    def test_update_config(self):
        params = UpdateConfigRequest(updated={"key1": "value1", "key2": "value2"})
        resp = WAII.User.update_config(params)
        assert resp.configs['key1'] == 'value1'
        assert resp.configs['key2'] == 'value2'
        params = UpdateConfigRequest(deleted=["key1"], updated={"key3": "value3"})
        resp = WAII.User.update_config(params)
        assert 'key1' not in resp.configs
        assert resp.configs['key3'] == 'value3'
        params = UpdateConfigRequest()
        resp = WAII.User.update_config(params)
        assert resp.configs['key2'] == 'value2'
        assert resp.configs['key3'] == 'value3'

    def test_manage_user(self):
        params = DeleteUserRequest(id="user1")
        try:
            resp = WAII.User.delete_user(params)
        except:
            pass
        params = CreateUserRequest(
            user=UserModel(id="user1", name="Wangda Tan", tenant_id="my_tenant_id", org_id="my_org_id"))
        resp = WAII.User.create_user(params)
        assert isinstance(resp, CommonResponse)

        params = ListUsersRequest(lookup_org_id="my_org_id")
        resp = WAII.User.list_users(params)
        user1 = [user for user in resp.users if user.id == "user1"]
        assert len(user1) > 0

        params = UpdateUserRequest(
            user=UserModel(id="user1", name="Pravin", tenant_id="my_tenant_id", org_id="my_org_id"))
        resp = WAII.User.update_user(params)
        assert isinstance(resp, CommonResponse)

        params = ListUsersRequest(lookup_org_id="my_org_id")
        resp = WAII.User.list_users(params)
        user1 = [user for user in resp.users if user.id == "user1"]
        assert user1[0].name == "Pravin"

        params = DeleteUserRequest(id="user1")
        resp = WAII.User.delete_user(params)
        assert isinstance(resp, CommonResponse)

        params = ListUsersRequest(lookup_org_id="my_org_id")
        resp = WAII.User.list_users(params)
        user1 = [user for user in resp.users if user.id == "user1"]
        assert len(user1) == 0

    def test_manage_org(self):
        params = DeleteOrganizationRequest(id="o1")
        try:
            resp = WAII.User.delete_org(params)
        except:
            pass
        params = CreateOrganizationRequest(organization=Organization(id="o1", name="My Org"))
        resp = WAII.User.create_org(params)
        assert isinstance(resp, CommonResponse)
        params = ListOrganizationsRequest()
        resp = WAII.User.list_orgs(params)
        org1 = [org for org in resp.organizations if org.id == "o1"]
        assert len(org1) > 0
        params = UpdateOrganizationRequest(organization=Organization(id="o1", name="My Org2"))
        resp = WAII.User.update_org(params)
        assert isinstance(resp, CommonResponse)
        params = ListOrganizationsRequest()
        resp = WAII.User.list_orgs(params)
        org1 = [org for org in resp.organizations if org.id == "o1"][0]
        assert org1.name == "My Org2"
        params = DeleteOrganizationRequest(id="o1")
        resp = WAII.User.delete_org(params)
        assert isinstance(resp, CommonResponse)
        params = ListOrganizationsRequest()
        resp = WAII.User.list_orgs(params)
        org1 = [org for org in resp.organizations if org.id == "o1"]
        assert len(org1) == 0

    def test_manage_tenant(self):
        #delete all users with tenant id = tenant1
        params = ListOrganizationsRequest()
        orgs = WAII.User.list_orgs(params)
        for org in orgs.organizations:
            print(org)
            params = ListUsersRequest(lookup_org_id=org.id)
            users_resp = WAII.User.list_users(params)
            for user in users_resp.users:
                print(user)
                if user.tenant_id == "tenant1":
                    WAII.User.delete_user(DeleteUserRequest(id = user.id))


        params = CreateOrganizationRequest(organization=Organization(id="o1", name="My Org"))
        del_tenant = DeleteTenantRequest(id="tenant1")
        try:
            resp = WAII.User.create_org(params)
        except:
            pass
        try:
            resp = WAII.User.delete_tenant(del_tenant)
        except Exception as e:
            pass
        params = CreateTenantRequest(tenant=Tenant(id="tenant1", name="Test Tenant", org_id="o1"))
        resp = WAII.User.create_tenant(params)
        assert isinstance(resp, CommonResponse)
        params = ListTenantsRequest(lookup_org_id="o1")
        resp = WAII.User.list_tenants(params)
        tenant1 = [tenant for tenant in resp.tenants if tenant.id == "tenant1"]
        assert len(tenant1) > 0
        params = UpdateTenantRequest(tenant=Tenant(id="tenant1", name="Test Tenant2", org_id="o1"))
        resp = WAII.User.update_tenant(params)
        assert isinstance(resp, CommonResponse)
        params = ListTenantsRequest(lookup_org_id="o1")
        resp = WAII.User.list_tenants(params)
        tenant1 = [tenant for tenant in resp.tenants if tenant.id == "tenant1"][0]
        assert tenant1.name == "Test Tenant2"
        params = DeleteTenantRequest(id="tenant1")
        resp = WAII.User.delete_tenant(params)
        assert isinstance(resp, CommonResponse)
        params = ListTenantsRequest()
        resp = WAII.User.list_tenants(params)
        tenant1 = [tenant for tenant in resp.tenants if tenant.id == "tenant1"]
        assert len(tenant1) == 0

    def test_impersonation(self):
        client = Waii()
        client.initialize(url="http://localhost:9859/api/")

        # create an hierarchy of organizations, tenants and users
        if not org_exists(client, "org1"):
            org = Organization(id="org1", name="My Org")
            WAII.User.create_org(CreateOrganizationRequest(organization=org))

        if not tenant_exists(client, "org1", "tenant1"):
            tenant = Tenant(id="tenant1", name="Test Tenant", org_id="org1")
            WAII.User.create_tenant(CreateTenantRequest(tenant=tenant))

        if not user_exists(client, "org1", "user1"):
            user = User(id="user1", name="Wangda Tan", tenant_id="tenant1", org_id="org1")
            WAII.User.create_user(CreateUserRequest(user=user))

        if not user_exists(client, "org1", "user2"):
            user = User(id="user2", name="Pravin", tenant_id="tenant1", org_id="org1")
            WAII.User.create_user(CreateUserRequest(user=user))

        # impersonate the user
        client.set_impersonate_user("user1")

        # get the user info
        resp = client.user.get_user_info(GetUserInfoRequest())
        assert isinstance(resp, GetUserInfoResponse)
        assert resp.id == "user1"
        assert resp.name == "Wangda Tan"

        # test impersonation, with block
        with client.impersonate_user("user1"):
            resp = client.user.get_user_info(GetUserInfoRequest())
            assert isinstance(resp, GetUserInfoResponse)
            assert resp.id == "user1"
            assert resp.name == "Wangda Tan"

        resp = client.user.get_user_info(GetUserInfoRequest())
        assert isinstance(resp, GetUserInfoResponse)
        assert resp.id == "my_org_id"
        assert resp.name == "J.A.R.V.I.S."

        with client.impersonate_user("user2"):
            resp = client.user.get_user_info(GetUserInfoRequest())
            assert isinstance(resp, GetUserInfoResponse)
            assert resp.id == "user2"
            assert resp.name == "Pravin"


if __name__ == '__main__':
    unittest.main()
