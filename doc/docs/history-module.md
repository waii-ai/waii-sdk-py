---
id: history-module
title: History
---

The `History` module contains methods related to history handling.

**Initialization & Imports**
```python
from waii_sdk_py import WAII
from waii_sdk_py.chat import *
from waii_sdk_py.query import *
from waii_sdk_py.database import *
from waii_sdk_py.semantic_context import *
from waii_sdk_py.chart import *
from waii_sdk_py.history import *

WAII.initialize(url="https://your-waii-instance/api/", api_key="your-api-key")
```

Here are some of its methods:

### Get

```python
History.get(params: GetGeneratedQueryRequest = GetGeneratedQueryRequest()) -> GetGeneratedQueryResponse
```

Request fields:
- `included_types` (List[GeneratedHistoryEntryType], optional): The types of entries to include in the response. Defaults to `[GeneratedHistoryEntryType.query, GeneratedHistoryEntryType.chart, GeneratedHistoryEntryType.chat]`.  
- `limit` (int, optional): The maximum number of entries to return. Defaults to `1000`.
- `offset` (int, optional): The number of entries to skip. Defaults to `0`.
- `timestamp_sort_order` (SortOrder, optional): The order in which to sort the entries by timestamp. Defaults to `SortOrder.desc`.
- `uuid_filter` (str, optional): The UUID of the entry to filter by.
- `liked_query_filter` (bool, optional): The flag to filter by liked queries. Defaults to `None`, which includes both liked and unliked queries. When this is set to `True` or `False`, you should only include `GeneratedHistoryEntryType.query` in the `included_types` field.

Response fields:
- `entries` (List[GeneratedHistoryEntry]): The list of generated history entries, it can be a query, chart, or chat.

#### Examples

Get all queries (use offset and limits to paginate):

```python
all_history_queries = []

offset = 0

while True:
    queries = History.get(GetHistoryRequest(included_types=[GeneratedHistoryEntryType.query], limit=1000, offset=offset)).history
    if queries:
        all_history_queries.extend(queries)
        offset += 1000
    else:
        break
```

### List (This is deprecated, use `get` instead)

```python
History.list(params: GetGeneratedQueryHistoryRequest = GetGeneratedQueryHistoryRequest()) -> GetGeneratedQueryHistoryResponse
```

This method fetches the history of generated queries.

For detailed information about the request and response objects and the available properties, refer to the respective Python files of each module.
