import unittest
from waii_sdk_py import WAII
from waii_sdk_py.database import ModifyDBConnectionRequest

class TestDatabase(unittest.TestCase):
    def setUp(self):
        WAII.initialize()
        result = WAII.Database.get_connections()
        self.result = result
        WAII.Database.activate_connection(result.connectors[0].key)

    def test_modify_connections(self):
        # Define test parameters
        params = ModifyDBConnectionRequest(
            updated = [],
            removed = []
        )
        # Call the function
        result = WAII.Database.modify_connections(params)
        # Check the result
        # Note: The specifics of this assertion would depend on what the function should return
        self.assertEqual(len(result.connectors), len(self.result.connectors))

    def test_get_connections(self):
        # Call the function
        result = WAII.Database.get_connections()
        # Check the result
        # Note: The specifics of this assertion would depend on what the function should return
        self.assertEqual(len(result.connectors), len(self.result.connectors))

    def test_activate_connection(self):
        # Define test parameters
        key = "Test"
        # Call the function
        WAII.Database.activate_connection(self.result.connectors[0].key)
        # Check the result
        # Note: The specifics of this assertion would depend on what the function should return
        # Assert the state of the database after calling the function
        
    def test_get_catalogs(self):
        # Call the function
        result = WAII.Database.get_catalogs()
        # Check the result
        # Note: The specifics of this assertion would depend on what the function should return
        #self.assertEqual(result, expected_result)


if __name__ == '__main__':
    unittest.main()
