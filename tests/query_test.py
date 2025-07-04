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
from waii_sdk_py.query import *


class TestQuery(unittest.TestCase):
    def setUp(self):
        WAII.initialize(url="http://localhost:9859/api/")
        result = WAII.Database.get_connections()
        self.result = result
        pg_connector = None
        for connector in result.connectors:
            if connector.db_type == "postgresql" and connector.database == 'waii_sdk_test':
                pg_connector = connector
                break

        WAII.Database.activate_connection(pg_connector.key)

    def test_generate(self):
        params = QueryGenerationRequest(ask="How many movies are there?", use_cache=False)
        result = WAII.Query.generate(params)
        self.assertIsInstance(result, GeneratedQuery)
        assert result.uuid is not None
        assert len(result.detailed_steps) > 0
        assert len(result.query) > 0
        assert 'public.movies' in result.query.lower()
        assert len(result.tables) > 0
        assert hasattr(result.confidence_score, "confidence_value")

        params = LikeQueryRequest(query_uuid=result.uuid, liked=True)
        result = WAII.Query.like(params)
        self.assertIsInstance(result, LikeQueryResponse)

    def test_tweak(self):
        params = QueryGenerationRequest(ask = "only return 10 results", tweak_history=[Tweak(sql="select * from information_schema.tables", ask="give me all tables")])
        result = WAII.Query.generate(params)
        print(result)
        assert "limit 10" in result.query.lower()
        assert len(result.what_changed) > 0

    def test_run(self):
        params = RunQueryRequest(query="SELECT 42")
        result = WAII.Query.run(params)
        self.assertIsInstance(result, GetQueryResultResponse)
        assert len(result.column_definitions) > 0
        assert '42' in str(result.rows[0])



    def test_submit(self):
        params = RunQueryRequest(query="SELECT 42")
        result = WAII.Query.submit(params)
        self.assertIsInstance(result, RunQueryResponse)
        assert result.query_id is not None

        params = GetQueryResultRequest(query_id=result.query_id)
        result = WAII.Query.get_results(params)
        self.assertIsInstance(result, GetQueryResultResponse)
        assert '42' in str(result.rows[0])

    def test_describe(self):
        params = DescribeQueryRequest(query="SELECT 42")
        result = WAII.Query.describe(params)
        self.assertIsInstance(result, DescribeQueryResponse)
        print(result)
        assert len(result.detailed_steps) > 0
        assert len(result.summary) > 0

    def test_transcode(self):
        params = TranscodeQueryRequest(source_dialect="mysql", target_dialect="postgres", source_query="SELECT * FROM movies")
        result = WAII.Query.transcode(params)
        self.assertIsInstance(result, GeneratedQuery)
        assert len(result.query) > 0
        assert 'movies' in result.query.lower()

    def test_like_query(self):
        params = LikeQueryRequest(liked=True,ask="like test ask", query="SELECT S_STATE FROM STORE",
                                  detailed_steps=["step3", "step4"])
        result = WAII.Query.like(params)
        self.assertIsInstance(result, LikeQueryResponse)
        params = QueryGenerationRequest(ask="like test ask")
        result = WAII.Query.generate(params)
        assert result.detailed_steps == ["step3", "step4"]

    def test_error_with_unknown_fields(self):
        params = QueryGenerationRequest(ask='like test ask', q_id='unknown id')
        
        with pytest.raises(ValueError):
            result = WAII.Query.generate(params)


if __name__ == '__main__':
    unittest.main()
