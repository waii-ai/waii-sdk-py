import unittest

from waii_sdk_py import WAII
from waii_sdk_py.user import CreateAccessKeyRequest, DelAccessKeyRequest, DelAccessKeyResponse, GetAccessKeyRequest, \
    GetUserInfoRequest, GetUserInfoResponse, UpdateConfigRequest, User, CreateUserRequest, UserDTO, DeleteUserRequest, \
    CommonResponse, ListUsersRequest, UpdateUserRequest


class TestUser(unittest.TestCase):
    def setUp(self):
        WAII.initialize(url="http://localhost:9859/api/")
    def test_create_access_key(self):
        params = DelAccessKeyRequest(names = ["test1"])
        resp = WAII.User.delete_access_key(params)
        params = CreateAccessKeyRequest(name = "test1")
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
        params = DeleteUserRequest(id = "user1")
        try:
            resp = WAII.User.delete_user(params)
        except:
            pass
        params = CreateUserRequest(user=UserDTO( id="user1",name="Wangda Tan",tenant_id="my_tenant_id",org_id="my_org_id"))
        resp = WAII.User.create_user(params)
        assert isinstance(resp, CommonResponse)

        params = ListUsersRequest(lookup_org_id = "my_org_id")
        resp = WAII.User.list_users(params)
        user1 = [user for user in resp.users if user.id == "user1"]
        assert len(user1) > 0

        params = UpdateUserRequest(user=UserDTO( id="user1",name="Pravin",tenant_id="my_tenant_id",org_id="my_org_id"))
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















if __name__ == '__main__':
    unittest.main()
