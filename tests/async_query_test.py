import asyncio
import unittest
from unittest import IsolatedAsyncioTestCase

from waii_sdk_py.query import QueryGenerationRequest, GeneratedQuery
from waii_sdk_py.waii_sdk_py import AsyncWaii


class TestAsyncQuery(IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        async_waii_client = AsyncWaii()
        await async_waii_client.initialize(url="http://localhost:9859/api/")
        self.async_waii_client = async_waii_client
        result = await self.async_waii_client.database.get_connections()
        self.result = result
        pg_connector = None
        for connector in result.connectors:
            if connector.db_type == "postgresql":
                pg_connector = connector
                break

        await self.async_waii_client.database.activate_connection(pg_connector.key)

    async def test_generate_async(self):
        # Define parameters for concurrent testing
        params1 = QueryGenerationRequest(ask="How many tables are there?", use_cache=False)
        params2 = QueryGenerationRequest(ask="List all table names.", use_cache=False)

        # Shared list to check task start and end
        task_indicators = []

        async def generate_task(params, task_name):
            task_indicators.append(f"{task_name}_started")
            result = await self.async_waii_client.query.generate(params)
            task_indicators.append(f"{task_name}_finished")
            return result

        # Run generate tasks concurrently
        task1 = asyncio.create_task(generate_task(params1, "task1"))
        task2 = asyncio.create_task(generate_task(params2, "task2"))

        result1, result2 = await asyncio.gather(task1, task2)

        self.assertEqual("task1_started", task_indicators[0])
        self.assertEqual("task2_started", task_indicators[1])
        self.assertEqual("task1_finished", task_indicators[2])
        self.assertEqual("task2_finished", task_indicators[3])

        self.assertIsInstance(result1, GeneratedQuery)
        self.assertIsInstance(result2, GeneratedQuery)

