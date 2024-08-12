import unittest

from waii_sdk_py import WAII
from waii_sdk_py.user import CreateAccessKeyRequest, DelAccessKeyRequest, DelAccessKeyResponse, GetAccessKeyRequest


class TestUser(unittest.TestCase):
    def setUp(self):
        WAII.initialize(url="http://localhost:9859/api/")
    def test_create_access_key(self):
        params = DelAccessKeyRequest(names = ["test1"])
        resp = WAII.user.delete_access_key(params)
        params = CreateAccessKeyRequest(name = "test1")
        resp = WAII.user.create_access_key(params)
        test1_key = [key for key in resp.access_keys if key.name == "test1"]
        assert len(test1_key) > 0

    def test_delete_access_key(self):
        params = DelAccessKeyRequest(names=["test2"])
        resp = WAII.user.delete_access_key(params)
        params = CreateAccessKeyRequest(name="test2")
        resp = WAII.user.create_access_key(params)
        test2_key = [key for key in resp.access_keys if key.name == "test2"]
        assert len(test2_key) > 0

        params = GetAccessKeyRequest()
        resp = WAII.user.list_access_keys(params)
        test2_key = [key for key in resp.access_keys if key.name == "test2"]
        assert len(test2_key) > 0

        params = DelAccessKeyRequest(names=["test2"])
        resp = WAII.user.delete_access_key(params)
        assert isinstance(resp, DelAccessKeyResponse)

        params = GetAccessKeyRequest()
        resp = WAII.user.list_access_keys(params)
        test2_key = [key for key in resp.access_keys if key.name == "test2"]
        assert len(test2_key) == 0

    def test_list_access_keys(self):
        params = DelAccessKeyRequest(names=["test2"])
        resp = WAII.user.delete_access_key(params)

        params = GetAccessKeyRequest()
        resp = WAII.user.list_access_keys(params)
        test2_key = [key for key in resp.access_keys if key.name == "test2"]
        assert len(test2_key) == 0

        params = CreateAccessKeyRequest(name="test2")
        resp = WAII.user.create_access_key(params)
        test2_key = [key for key in resp.access_keys if key.name == "test2"]
        assert len(test2_key) > 0

        params = GetAccessKeyRequest()
        resp = WAII.user.list_access_keys(params)
        test2_key = [key for key in resp.access_keys if key.name == "test2"]
        assert len(test2_key) > 0

        params = DelAccessKeyRequest(names=["test2"])
        resp = WAII.user.delete_access_key(params)









if __name__ == '__main__':
    unittest.main()
