import unittest
from waii_sdk_py import WAII
from waii_sdk_py.query import *

class TestQuery(unittest.TestCase):
    def setUp(self):
        WAII.initialize()
        result = WAII.Database.get_connections()
        self.result = result
        WAII.Database.activate_connection(result.connectors[0].key)

    def test_generate(self):
        params = QueryGenerationRequest(ask = "How many tables are there?")
        result = WAII.Query.generate(params)
        self.assertIsInstance(result, GeneratedQuery)

        params = LikeQueryRequest(query_uuid=result.uuid, liked=True)
        result = WAII.Query.like(params)
        self.assertIsInstance(result, LikeQueryResponse)

    def test_run(self):
        params = RunQueryRequest(query="SELECT 42")
        result = WAII.Query.run(params)
        self.assertIsInstance(result, GetQueryResultResponse)

    def test_submit(self):
        params = RunQueryRequest(query="SELECT 42")
        result = WAII.Query.submit(params)
        self.assertIsInstance(result, RunQueryResponse)

        params = GetQueryResultRequest(query_id=result.query_id)
        result = WAII.Query.get_results(params)
        self.assertIsInstance(result, GetQueryResultResponse)

    #def test_cancel(self):
    #    params = CancelQueryRequest(query_id="some-query-id")
    #    result = WAII.Query.cancel(params)
    #    self.assertIsInstance(result, CancelQueryResponse)

    def test_describe(self):
        params = DescribeQueryRequest(query="SELECT 42")
        result = WAII.Query.describe(params)
        self.assertIsInstance(result, DescribeQueryResponse)


if __name__ == '__main__':
    unittest.main()
