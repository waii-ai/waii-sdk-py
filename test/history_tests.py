import unittest
from waii_sdk_py import WAII

class TestDatabase(unittest.TestCase):
    def setUp(self):
        WAII.initialize()
        result = WAII.Database.get_connections()
        self.result = result
        WAII.Database.activate_connection(result.connectors[0].key)

    def test_list(self):
        # Call the function
        result = WAII.History.list()
        # Check the result
        # Note: The specifics of this assertion would depend on what the function should return
        self.assertGreater(len(result.history), 0)

if __name__ == '__main__':
    unittest.main()
