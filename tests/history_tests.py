import unittest
from waii_sdk_py import WAII
from waii_sdk_py.history import *

class TestHistory(unittest.TestCase):
    def setUp(self):
        WAII.initialize(url="http://localhost:9859/api/")
        result = WAII.Database.get_connections()
        self.result = result
        WAII.Database.activate_connection(result.connectors[0].key)

    def test_list(self):
        # Call the function
        result = WAII.History.list()
        # Check the result
        # Note: The specifics of this assertion would depend on what the function should return
        self.assertGreater(len(result.history), 0)
        # TODO: not working right now
        params = GetGeneratedQueryHistoryRequest(limit=1, offset=1)
        result = WAII.History.list(params)
        print(result)
        # self.assertEqual(len(result.history), 1)



if __name__ == '__main__':
    unittest.main()
