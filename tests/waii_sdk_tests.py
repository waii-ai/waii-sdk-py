import unittest

from waii_sdk_py.database import Database
from waii_sdk_py.query import *
from waii_sdk_py.waii_sdk_py import Waii, WAII

'''
movie and chinook are two database
create the database named chinook from here https://github.com/morenoh149/postgresDBSamples/tree/master/chinook-1.4
user name of database should be waii and password should be password

create the database named called movie by taking data from here
https://www.notion.so/waii-ai/Use-PG-WAII-eac9d02bb7894f748ed55aaaf8796e3c

'''


class WaiiSDKTests(unittest.TestCase):
    def setUp(self):
        movie_waii = Waii()
        chinook_waii = Waii()
        movie_waii.initialize(url="http://localhost:9859/api/")
        chinook_waii.initialize(url="http://localhost:9859/api/")
        result = movie_waii.database.get_connections()
        movie_conn = [conn for conn in result.connectors if conn.database == "movie"][0]
        chinook_conn = [
            conn for conn in result.connectors if conn.database == "chinook"
        ][0]
        WAII.initialize(url="http://localhost:9859/api/")
        self.movie_conn = movie_conn
        self.chinook_conn = chinook_conn
        self.movie_waii = movie_waii
        self.chinook_waii = chinook_waii

    def test_movie_generate(self):
        self.movie_waii.database.activate_connection(self.movie_conn.key)
        params = QueryGenerationRequest(
            ask="Give me 5 movie names sorted by movie name"
        )
        result = self.movie_waii.query.generate(params)
        self.assertIsInstance(result, GeneratedQuery)
        assert result.uuid is not None
        assert len(result.detailed_steps) > 0
        assert len(result.query) > 0
        assert "cine_tele_data" in result.query.lower()
        assert len(result.tables) > 0

        params = LikeQueryRequest(query_uuid=result.uuid, liked=True)
        result = self.movie_waii.query.like(params)
        self.assertIsInstance(result, LikeQueryResponse)

    def test_movie_run(self):
        self.movie_waii.database.activate_connection(self.movie_conn.key)
        params = QueryGenerationRequest(
            ask="Give me 5 movie names sorted by movie name"
        )
        result = self.movie_waii.query.generate(params)
        params = RunQueryRequest(query=result.query)
        result = self.movie_waii.query.run(params)
        self.assertIsInstance(result, GetQueryResultResponse)
        assert len(result.column_definitions) > 0
        assert "102 Dalmatians" in str(result.rows[0])

    def test_chinook_generate(self):
        self.movie_waii.database.activate_connection(self.chinook_conn.key)
        params = QueryGenerationRequest(ask="Give me 5 album names sorted by name")
        result = self.chinook_waii.query.generate(params)
        self.assertIsInstance(result, GeneratedQuery)
        assert result.uuid is not None
        assert len(result.detailed_steps) > 0
        assert len(result.query) > 0
        assert "public" in result.query.lower()
        assert len(result.tables) > 0

        params = LikeQueryRequest(query_uuid=result.uuid, liked=True)
        result = self.chinook_waii.query.like(params)
        self.assertIsInstance(result, LikeQueryResponse)

    def test_chinook_run(self):
        self.chinook_waii.database.activate_connection(self.chinook_conn.key)
        params = QueryGenerationRequest(ask="Give me 5 album names sorted by name")
        result = self.chinook_waii.query.generate(params)
        params = RunQueryRequest(query=result.query)
        result = self.chinook_waii.query.run(params)
        self.assertIsInstance(result, GetQueryResultResponse)
        assert len(result.column_definitions) > 0
        assert "...And Justice For All" in str(result.rows[0])


    def test_legacy_generate(self):
        WAII.Database.activate_connection(self.movie_conn.key)
        params = QueryGenerationRequest(
            ask="Give me 5 movie names sorted by movie name"
        )
        result = WAII.Query.generate(params)
        self.assertIsInstance(result, GeneratedQuery)
        assert result.uuid is not None
        assert len(result.detailed_steps) > 0
        assert len(result.query) > 0
        assert "cine_tele_data" in result.query.lower()
        assert len(result.tables) > 0

        params = LikeQueryRequest(query_uuid=result.uuid, liked=True)
        result = WAII.Query.like(params)
        self.assertIsInstance(result, LikeQueryResponse)



    def test_legacy_run(self):
        WAII.Database.activate_connection(self.movie_conn.key)
        params = QueryGenerationRequest(
            ask="Give me 5 movie names sorted by movie name"
        )
        result = WAII.Query.generate(params)
        params = RunQueryRequest(query=result.query)
        result = WAII.Query.run(params)
        self.assertIsInstance(result, GetQueryResultResponse)
        assert len(result.column_definitions) > 0
        assert "102 Dalmatians" in str(result.rows[0])

    def test_legacy_run_without_WAII(self):
        Database.activate_connection(self.movie_conn.key)
        params = QueryGenerationRequest(
            ask="Give me 5 movie names sorted by movie name"
        )
        result = Query.generate(params)
        params = RunQueryRequest(query=result.query)
        result = Query.run(params)
        self.assertIsInstance(result, GetQueryResultResponse)
        assert len(result.column_definitions) > 0
        assert "102 Dalmatians" in str(result.rows[0])

    def test_activate_connection(self):
        Database.activate_connection(self.movie_conn.key)
        result = Database.get_activated_connection()
        assert(self.movie_conn.key == result)



