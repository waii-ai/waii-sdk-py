---
id: async-client
title: Async Client
---

### Async Client

This guide explains how to set up and use the `AsyncWaii` client to make asynchronous API calls.

**Initialization & Imports**
```python
# in order to use this, you need to make sure waii-sdk-py is >= 1.28.2
# otherwise, you should do 
# from waii_sdk_py.waii_sdk_py import AsyncWaii
from waii_sdk_py import AsyncWaii
from waii_sdk_py.database import *

client = AsyncWaii()
await client.initialize(url='...', api_key="<your-api-key>")
```

#### Using the Async Client

The AsyncWaii client follows the same interface as the synchronous client, with some examples provided below.

###### Activating a Database Connection

Use the activate_connection method to activate a database connection asynchronously:
```python
# put it under the async function
async def your_async_function():
    conn_resp = await client.database.activate_connection("<db_conn_key>")
```

###### Generating a Query

To generate a query with the async client, pass a QueryGenerationRequest to the generate method:
```python
# put it under the async function
async def your_async_function():
    ask = QueryGenerationRequest(ask="sample ask")
    query_gen_resp = await client.query.generate(ask)
```

Refer to the respective module for additional use cases, as both clients use the same interface.


