---
id: multi-tenant-client-module
title: Multi-tenant Waii SDK Client
---
The Waii SDK allows you to create multiple instances of the client, enabling you to manage different configurations and databases independently.

**Initialization & Imports**

```python
# in order to use this, you need to make sure waii-sdk-py is >= 1.28.2
# otherwise, you should do 
# from waii_sdk_py import Waii
from waii_sdk_py import Waii
from waii_sdk_py.chat import *
from waii_sdk_py.query import *
from waii_sdk_py.database import *
from waii_sdk_py.semantic_context import *
from waii_sdk_py.chart import *
```

### Creating Multiple Client Instances
You can initialize multiple instances of the Waii SDK as shown below:

```python
client1_sdk = Waii()
client1_sdk.initialize(url='...', api_key="<your-api-key>")
client1_sdk = Waii()
client2_sdk.initialize(url='...', api_key="<your-api-key>")
```

### Activating Different Database Connections
With different client instances, you can activate and query separate database connections:

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

### Module Access in Multi-Tenant Clients

The table below summarizes how to access different modules in both the static and multi-tenant client setups:

| Module          | Static Client          | Multi-Tenant Client            |
|-----------------|------------------------|--------------------------------|
| Database        | `WAII.Database`        | `<waii_sdk_client>.database`         |
| History         | `WAII.History`         | `<waii_sdk_client>.history`          |
| Query           | `WAII.Query`           | `<waii_sdk_client>.query`            |
| SemanticContext | `WAII.SemanticContext` | `<waii_sdk_client>.semantic_context` |
| User            | `WAII.User`            | `<waii_sdk_client>.user`             |
| Chart           | `WAII.Chart`           | `<waii_sdk_client>.chart`            |
| Chat            | `WAII.Chat`            | `<waii_sdk_client>.chat`             |

This setup provides flexibility by allowing different clients to interact with different databases and configurations, all within the same application.

### Example of using multi-tenant module

See this notebook: https://github.com/waii-ai/waii-sdk-py/blob/main/doc/docs/waii-multi-user-example.ipynb


