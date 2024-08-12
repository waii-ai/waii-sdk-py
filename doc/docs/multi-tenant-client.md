---
id: multi-tenant-client-module
title: Multi-tenant Waii SDK Client
---
You can create multiple instances of Waii SDK client

```python
client1_sdk = Waii()
client1_sdk.initialize(url='...', api_key="<your-api-key>")
client1_sdk = Waii()
client2_sdk.initialize(url='...', api_key="<your-api-key>")
```
You can activate different database connection on different client and query it. For example
```python
client1_sdk.database.activate_connection("<db1_conn_key>")
client2_sdk.database.activate_connection("<db2_conn_key>")
ask1 = QueryGenerationRequest(ask="<ask_for_db1>")
ask2 = QueryGenerationRequest(ask="<ask_for_db2>")
client1_sdk.query.generate(ask1)
client2_sdk.query.generate(ask2)
```
You can notice that in static client for accessing query module we used to use WAII.Query but here we are using
client1_sdk.query

Below is the table for accessing different module from above client

| Module          | Static Client          | Multi-Tenant Client            |
|-----------------|------------------------|--------------------------------|
| Database        | `WAII.Database`        | `client1_sdk.database`         |
| History         | `WAII.History`         | `client1_sdk.history`          |
| Query           | `WAII.Query`           | `client1_sdk.query`            |
| SemanticContext | `WAII.SemanticContext` | `client1_sdk.semantic_context` |
| User            | `WAII.user`            | `client1_sdk.user`             |
| Chart           | `WAII.chart`           | `client1_sdk.chart`            |
| Chat            | `WAII.chat`            | `client1_sdk.chat`             |




