import unittest
from unittest.mock import Mock, patch
from enum import Enum
from typing import Optional, List
from datetime import datetime

from waii_sdk_py import WAII
from waii_sdk_py.chat import Chat, ChatRequest, ChatResponse, ChatResponseData, ChatModule
from waii_sdk_py.query import GeneratedQuery
from waii_sdk_py.database import CatalogDefinition
from waii_sdk_py.semantic_context import GetSemanticContextResponse
from waii_sdk_py.chart import ChartGenerationResponse, ChartType

class TestChatV2(unittest.TestCase):
    def setUp(self):
        WAII.initialize(url="http://localhost:9859/api/")
        result = WAII.Database.get_connections()
        self.result = result
        snowflake_connector = None
        for connector in result.connectors:
            if connector.db_type == "snowflake":
                snowflake_connector = connector
                break

        WAII.Database.activate_connection(snowflake_connector.key)

        self.chat = Chat

    def test_chat_message_query(self):

        chat_request = ChatRequest(
            ask="Show me movies data",
            streaming=False,
            parent_uuid=None,
            chart_type=None,
            modules=[ChatModule.QUERY],
            module_limit_in_response=1
        )

        result = self.chat.chat_message(chat_request)

        self.assertIsInstance(result, ChatResponse)
        self.assertIsNotNone(result.response_data)
        self.assertIsNotNone(result.response_data.query)
        self.assertEqual(result.response_selected_fields, [ChatModule.QUERY])
        self.assertTrue(result.is_new)
        self.assertIsNotNone(result.timestamp_ms)

    def test_chat_message_chart(self):
        chat_request = ChatRequest(
            ask="Show me a bar chart of movie ratings",
            streaming=False,
            parent_uuid=None,
            chart_type=ChartType.SUPERSET,
            modules=[ChatModule.CHART, ChatModule.QUERY],
            module_limit_in_response=2
        )

        result = self.chat.chat_message(chat_request)

        self.assertIsInstance(result, ChatResponse)
        self.assertIsNotNone(result.response)
        self.assertIsNotNone(result.response_data)
        self.assertIsNotNone(result.response_data.chart)
        self.assertIsNotNone(result.response_data.query)
        self.assertIn(ChatModule.CHART, result.response_selected_fields)
    def test_chat_message_semantic_context(self):
        chat_request = ChatRequest(
            ask="What tables are available for movie data?",
            streaming=False,
            parent_uuid=None,
            chart_type=None,
            modules=[ChatModule.DATA],
            module_limit_in_response=1
        )

        result = self.chat.chat_message(chat_request)

        self.assertIsInstance(result, ChatResponse)
        self.assertIsNotNone(result.response)
        self.assertIsNotNone(result.response_data)
        self.assertIsNotNone(result.response_data.data)
        self.assertIn(ChatModule.DATA, result.response_selected_fields)

    def test_chat_message_tables(self):
        chat_request = ChatRequest(
            ask="Show me the schema for the movies table",
            streaming=False,
            parent_uuid=None,
            chart_type=None,
            modules=[ChatModule.TABLES],
            module_limit_in_response=1
        )

        result = self.chat.chat_message(chat_request)

        self.assertIsInstance(result, ChatResponse)
        self.assertIsNotNone(result.response)
        self.assertIsNotNone(result.response_data)
        self.assertIsNotNone(result.response_data.tables)

    def test_chat_conversation(self):
        # Initial question
        chat_request1 = ChatRequest(
            ask="What's the rating of movies?",
            streaming=False,
            parent_uuid=None,
            modules=[ChatModule.QUERY, ChatModule.DATA],
            module_limit_in_response=2
        )

        result1 = self.chat.chat_message(chat_request1)

        self.assertIsInstance(result1, ChatResponse)
        self.assertIsNotNone(result1.chat_uuid)

        # Follow-up question
        chat_request2 = ChatRequest(
            ask="Now show me this data in a bar chart",
            streaming=False,
            parent_uuid=result1.chat_uuid,
            chart_type=ChartType.SUPERSET,
            modules=[ChatModule.CHART],
            module_limit_in_response=1
        )

        result2 = self.chat.chat_message(chat_request2)

        self.assertIsInstance(result2, ChatResponse)
        self.assertIsNotNone(result2.response_data.chart)
        self.assertIn(ChatModule.CHART, result2.response_selected_fields)

if __name__ == '__main__':
    unittest.main()