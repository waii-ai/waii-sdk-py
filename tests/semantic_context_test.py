"""
Copyright 2023–2025 Waii, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import unittest
import pytest
from waii_sdk_py import WAII
from waii_sdk_py.semantic_context import GetSemanticContextRequest

class TestSemanticContext(unittest.TestCase):
    def setUp(self):
        WAII.initialize(url="http://localhost:9859/api/")
        result = WAII.Database.get_connections()
        self.result = result
        WAII.Database.activate_connection(result.connectors[2].key)

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
