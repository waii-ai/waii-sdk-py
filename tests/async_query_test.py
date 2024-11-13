import asyncio
import time
import unittest
from unittest import IsolatedAsyncioTestCase

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
        params = QueryGenerationRequest(ask="List all tables in database")

        start = time.time()
        await self.async_waii_client.query.generate(params)
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




