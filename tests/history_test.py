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
from waii_sdk_py.history import *
from waii_sdk_py.query import RunQueryRequest


class TestHistory(unittest.TestCase):
    def setUp(self):
        WAII.initialize(url="http://localhost:9859/api/")
        result = WAII.Database.get_connections()
        self.result = result
        WAII.Database.activate_connection(result.connectors[0].key)

    def test_list_legacy_api(self):
        # do a list and see if it returns something
        result = WAII.History.list()
        if not result.history:
            # first we need to create some queries
            result = WAII.Query.generate(QueryGenerationRequest(ask='how many tables are there in the database', parent_uuid=None))
            WAII.Query.run(RunQueryRequest(query=result.query))

        # Call the function
        result = WAII.History.list()
        # Check the result
        # Note: The specifics of this assertion would depend on what the function should return
        self.assertGreater(len(result.history), 0)

        params = GetGeneratedQueryHistoryRequest(limit=1, offset=1)
        result = WAII.History.get(params)
        self.assertTrue(len(result.history) >= 1)

    def test_get_new_api(self):
        result = WAII.History.get(GetHistoryRequest())
        if not result.history:
            # Then generate some chats
            asks = [
                "tell me how many tables are there in the database",
                "list number of columns for each table"
            ]
            parent_uuid = None
            for a in asks:
                chat_request = ChatRequest(ask=a, parent_uuid=parent_uuid)
                chat_response = WAII.Chat.chat_message(chat_request)
                print('Ask:', a)
                print(chat_response.response)
                if chat_response.response_data.sql:
                    print(chat_response.response_data.sql.query)
                if chat_response.response_data.data:
                    print(f"There're {len(chat_response.response_data.data.rows)} rows")
                parent_uuid = chat_response.chat_uuid

        # Then use the get method
        result = WAII.History.get(GetHistoryRequest())

        # Check the result
        self.assertGreater(len(result.history), 0)

        total_result = len(result.history)

        # Test with limit
        result = WAII.History.get(GetHistoryRequest(limit=1))
        self.assertEqual(len(result.history), 1)

        # Test with offset
        result = WAII.History.get(GetHistoryRequest(offset=1))
        self.assertEqual(len(result.history), total_result - 1)

        # Test error with unknown fields
        with pytest.raises(ValueError):
            result = WAII.History.get(
                GetHistoryRequest(offset=1, lt=5, id=4) # lt and id fields don't exist
            )



if __name__ == '__main__':
    unittest.main()
