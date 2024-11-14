---
id: async-client
title: Async Client
---

### Async Client

This guide explains how to set up and use the `AsyncWaii` client to make asynchronous API calls.

#### Creating an Async Client Instance
To initialize an instance of the async client, use the following code:

```python
client = AsyncWaii()
await client.initialize(url='...', api_key="<your-api-key>")
```

#### Using the Async Client

The AsyncWaii client follows the same interface as the synchronous client, with some examples provided below.

###### Activating a Database Connection

Use the activate_connection method to activate a database connection asynchronously:
```python
conn_resp = await client.database.activate_connection("<db_conn_key>")
```

######Generating a Query

To generate a query with the async client, pass a QueryGenerationRequest to the generate method:
```python
ask = QueryGenerationRequest(ask="sample ask")
query_gen_resp = await client.query.generate(ask)
```

Refer to the respective module for additional use cases, as both clients use the same interface.


