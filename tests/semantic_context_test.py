import unittest
import pytest
from waii_sdk_py import WAII
from waii_sdk_py.semantic_context import GetSemanticContextRequest

class TestSemanticContext(unittest.TestCase):
    def setUp(self):
        WAII.initialize(url="http://localhost:9859/api/")
        result = WAII.Database.get_connections()
        self.result = result
        WAII.Database.activate_connection(result.connectors[10].key)

    def test_modify_semantic_context(self):
        # Define test parameters
        # params = ModifySemanticContextRequest(updated=[SemanticStatement(statement="Example statement")])
        # Call the function
        # result = self.semantic_context.modifySemanticContext(params)
        # Check the result
        # Note: The specifics of this assertion would depend on what the function should return
        # self.assertIsInstance(result, ModifySemanticContextResponse)
        # self.assertEqual(len(result.updated), 1)
        # self.assertEqual(result.updated[0].statement, "Example statement")
        pass

    def test_get_semantic_context(self):
        # Call the function
        result = WAII.SemanticContext.get_semantic_context()
        # Check the result
        # Note: The specifics of this assertion would depend on what the function should return
        self.assertGreater(len(result.semantic_context), 0)
    
    def test_unknown_fields_error(self):
        with pytest.raises(ValueError):
            result = WAII.SemanticContext.get_semantic_context(
                GetSemanticContextRequest(search_txt='val') # search_txt field doesn't exist
            )

if __name__ == '__main__':
    unittest.main()
