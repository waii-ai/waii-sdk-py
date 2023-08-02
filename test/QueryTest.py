import unittest
from Query import Query, QueryGenerationRequest, RunQueryRequest, LikeQueryRequest, GetQueryResultRequest, CancelQueryRequest, DescribeQueryRequest

class TestQuery(unittest.TestCase):
    def setUp(self):
        self.query = Query()

    def test_generate(self):
        params = QueryGenerationRequest()
        result = self.query.generate(params)
        self.assertIsInstance(result, GeneratedQuery)

    def test_run(self):
        params = RunQueryRequest(query="SELECT * FROM test_table")
        result = self.query.run(params)
        self.assertIsInstance(result, GetQueryResultResponse)

    def test_like(self):
        params = LikeQueryRequest(query_uuid="some-query-uuid", liked=True)
        result = self.query.like(params)
        self.assertIsInstance(result, LikeQueryResponse)

    def test_submit(self):
        params = RunQueryRequest(query="SELECT * FROM test_table")
        result = self.query.submit(params)
        self.assertIsInstance(result, RunQueryResponse)

    def test_getResults(self):
        params = GetQueryResultRequest(query_id="some-query-id")
        result = self.query.getResults(params)
        self.assertIsInstance(result, GetQueryResultResponse)

    def test_cancel(self):
        params = CancelQueryRequest(query_id="some-query-id")
        result = self.query.cancel(params)
        self.assertIsInstance(result, CancelQueryResponse)

    def test_describe(self):
        params = DescribeQueryRequest(query="SELECT * FROM test_table")
        result = self.query.describe(params)
        self.assertIsInstance(result, DescribeQueryResponse)


if __name__ == '__main__':
    unittest.main()
