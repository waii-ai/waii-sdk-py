import asyncio
import time
import unittest
from unittest import IsolatedAsyncioTestCase

from tests.common_test_utils import load_db_conn1
from waii_sdk_py.database import TableDefinition, TableName, ColumnDefinition, UpdateTableDefinitionRequest, \
    ModifyDBConnectionRequest, TableReference
from waii_sdk_py.query import QueryGenerationRequest, GeneratedQuery
from waii_sdk_py.waii_sdk_py import AsyncWaii


async def generate_task(method, params, task_name, task_indicators, start_times):
    start_times.append((task_name, time.time()))
    task_indicators.append(f"{task_name}_started")

    result = await method(params) if params else await method()

    task_indicators.append(f"{task_name}_finished")
    start_times.append((task_name, time.time()))

    return result


class TestAsyncQuery(IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        async_waii_client = AsyncWaii()
        await async_waii_client.initialize(url="http://localhost:9859/api/")
        self.db_conn = load_db_conn1()
        self.async_waii_client = async_waii_client
        result = await self.async_waii_client.database.get_connections()
        self.result = result
        pg_connector = None
        for connector in result.connectors:
            if connector.db_type == "postgresql":
                pg_connector = connector
                break

        await self.async_waii_client.database.activate_connection(pg_connector.key)

    async def test_generate_query(self):
        params = QueryGenerationRequest(ask="List all tables in database")

        start = time.time()
        result = await self.async_waii_client.query.generate(params)
        isolated_execution_time = time.time() - start

        task_indicators = []
        start_times = []
        params = QueryGenerationRequest(ask="List all tables in database?.")
        task1 = asyncio.create_task(generate_task(
            self.async_waii_client.query.generate, params, "task1", task_indicators, start_times
        ))
        params = QueryGenerationRequest(ask="List all tables in database?...")
        task2 = asyncio.create_task(generate_task(
            self.async_waii_client.query.generate, params, "task2", task_indicators, start_times
        ))

        concurrent_start = time.time()
        await asyncio.gather(task1, task2)
        concurrent_execution_time = time.time() - concurrent_start
        print(f"Isolated execution time: {isolated_execution_time}")
        print(f"Concurrent execution time: {concurrent_execution_time}")
        self.assertLess(concurrent_execution_time, isolated_execution_time * 1.5,
                        "Tasks did not run concurrently, likely due to blocking HTTP client")

        # Validate order of task start and end times
        task1_start, task2_start = start_times[0][1], start_times[1][1]


        # Expect both tasks to overlap significantly in start times for async behavior
        self.assertLess(abs(task1_start - task2_start), 0.1, "Tasks should start concurrently")

        self.assertEqual("task1_started", task_indicators[0])
        self.assertEqual("task2_started", task_indicators[1])
        self.assertIn("task1_finished", task_indicators)
        self.assertIn("task2_finished", task_indicators)
        self.assertIsInstance(result, GeneratedQuery)
        assert result.uuid is not None
        assert len(result.detailed_steps) > 0
        assert len(result.query) > 0
        assert 'information_schema' in result.query.lower()
        assert len(result.tables) > 0
        assert hasattr(result.confidence_score, "confidence_value")

    async def test_modify_connections(self):
        # first try to delete te connection if it exists
        result = await self.async_waii_client.database.get_connections()
        result = result.connectors
        for conn in result:
            if (
                    conn.db_type == self.db_conn.db_type
                    and conn.account_name == self.db_conn.account_name
                    and self.db_conn.database == conn.database
                    and self.db_conn.username == conn.username
            ):
                result = await self.async_waii_client.database.modify_connections(
                    ModifyDBConnectionRequest(removed=[conn.key])
                )
                result = result.connectors
                break

        # then add the new connection
        new_result = await self.async_waii_client.database.modify_connections(
            ModifyDBConnectionRequest(updated=[self.db_conn])
        )
        new_result = new_result.connectors

        assert len(result) == len(new_result) - 1

        # then activate the new connection
        for conn in new_result:
            if (
                    conn.db_type == self.db_conn.db_type
                    and conn.account_name == self.db_conn.account_name
                    and self.db_conn.database == conn.database
                    and self.db_conn.username == conn.username
            ):
                await self.async_waii_client.database.activate_connection(conn.key)
                break
        else:
            raise Exception("Cannot find the new connection")

        # list databases
        result = await self.async_waii_client.database.get_catalogs()
        assert len(result.catalogs) > 0
        for catalog in result.catalogs:
            for schema in catalog.schemas:
                for table in schema.tables:
                    if len(table.refs) > 0:
                        assert type(table.refs[0]) == TableReference






