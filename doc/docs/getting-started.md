---
id: getting-started
title: Getting Started
---

First you can print the list of available databases:

Install and initialize the SDK
```python
>>> from waii_sdk_py import WAII
>>> from waii_sdk_py.query import *
>>> WAII.initialize(url='...', api_key="<your-api-key>")
```
(Refer to the [Installation](install.md) section for more details how to set url and api_key)

```python
>>> print([conn.key for conn in WAII.Database.get_connections().connectors])
```

Then, you can activate the database connection you want to use (from one of the key in the list above)

```python
>>> WAII.Database.activate_connection("snowflake://...&warehouse=COMPUTE_WH")
```

If you need to do some operations which don't need to connect to a specific database (e.g. list users, list databases, add new databases, etc.), you can skip the activation step.

```python 

Get Database name of the active connection

```python
>>> print([catalog.name for catalog in WAII.Database.get_catalogs().catalogs])
```

```python
>>> print(WAII.Query.generate(QueryGenerationRequest(ask = "How many tables are there?")).query)

SELECT COUNT(DISTINCT table_name)
FROM waii.information_schema.tables
```

Run the query

```python
>>> print(WAII.Query.run(RunQueryRequest(query = "SELECT COUNT(DISTINCT table_name) FROM waii.information_schema.tables")))

rows=[{'COUNT(DISTINCT TABLE_NAME)': 112}] more_rows=0 column_definitions=[ColumnDefinition(name='COUNT(DISTINCT TABLE_NAME)', type='FIXED')] query_uuid='01afbd1e-0001-d31e-0022-ba8700a8209e'
```

In order to know more details, you can check the following detailed API documentation.
