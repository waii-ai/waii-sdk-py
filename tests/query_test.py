import unittest
from waii_sdk_py import WAII
from waii_sdk_py.query import *


class TestQuery(unittest.TestCase):
    def setUp(self):
        WAII.initialize(url="http://localhost:9859/api/")
        result = WAII.Database.get_connections()
        self.result = result
        pg_connector = None
        for connector in result.connectors:
            if connector.db_type == "postgresql":
                pg_connector = connector
                break

        WAII.Database.activate_connection(pg_connector.key)

    def test_generate(self):
        params = QueryGenerationRequest(ask="How many tables are there?", use_cache=False)
        result = WAII.Query.generate(params)
        self.assertIsInstance(result, GeneratedQuery)
        assert result.uuid is not None
        assert len(result.detailed_steps) > 0
        assert len(result.query) > 0
        assert 'information_schema' in result.query.lower()
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
        params = TranscodeQueryRequest(source_dialect="mysql", target_dialect="postgres", source_query="SELECT 42")
        result = WAII.Query.transcode(params)
        self.assertIsInstance(result, GeneratedQuery)
        assert len(result.query) > 0
        assert '42' in result.query.lower()

    def test_like_query(self):
        params = LikeQueryRequest(liked=True,ask="like test ask", query="SELECT S_STATE FROM STORE",
                                  detailed_steps=["step3", "step4"])
        result = WAII.Query.like(params)
        self.assertIsInstance(result, LikeQueryResponse)
        params = QueryGenerationRequest(ask="like test ask")
        result = WAII.Query.generate(params)
        assert result.detailed_steps == ["step3", "step4"]


if __name__ == '__main__':
    unittest.main()
