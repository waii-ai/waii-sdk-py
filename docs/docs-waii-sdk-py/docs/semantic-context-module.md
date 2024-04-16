---
id: semantic-context-module
title: Semantic Context
---

The `SemanticContext` module contains methods related to semantic context handling.

Here are its methods:

### Modify Semantic Context

```python
SemanticContext.modify_semantic_context(params: ModifySemanticContextRequest) -> ModifySemanticContextResponse
```

example:
```python
SemanticContext.modify_semantic_context(ModifySemanticContextRequest(
    updated=[
        # ... list of SemanticStatement object
    ],
    deleted=[
        # ... list of statement id
    ]
))
```

This method allows you to modify the semantic context, which include two fields, `updated` and `deleted`.

For `updated`, you should include a list of `SemanticStatement` object, which include the following fields:

- `id`: (str) if you don't specify it, it will be auto generated. This is unique identifier of the semantic statement. You can use it to delete the statement later. We suggest you always include an id for the statement, so that you can find it easier. (Examples are JIRA_ID, PR_ID, CVE_ID, etc.)
- `statement`: (str), the statement you want to add. Such as `revenue is calculated by multiplying price and quantity`
- `scope`: (str), the scope of the statement, such as `*` (which means it applies to all queries), or `db.schema.table.column` (which means it applies to specific column of specific table of specific schema of specific database). This is optional, if not specified, it will be `*`. When `always_include` is False, `scope` will be ignored.
- `always_include`: should we always include this statement during query generation? True/False. Default is True. This is optional. When it is False, we will use embedding/LLM to do a RAG process and match statements during query generation.
- `lookup_summaries`: Only take effect when `always_include=False`, you can specify a list of search keys for this statement, if not specified, then use statement as search key. This is optional.
- `summarization_prompt`: extract prompt from the statement, if not specified, then use statement as extract prompt. This is optional.

There're several usage patterns of the `SemanticStatement` object:

**Add description to a database object (such as table, column, etc.)**
- Normally you want to do this to add a "description" to a table or column, so that Waii can use it to generate better query. Unless you want to apply it to the entire database, we suggest to always add a scope to the statement, such as `db.schema.table.column`, so that it only applies to specific column of specific table of specific schema of specific database.
- example: 
```python
statement = SemanticStatement(
    id = '',
    statement = 'The CUSTOMER_ADDRESS table contains information about the addresses of customers. It includes details such as address ID, city, country, ... This table can be used to retrieve customer addresses for various purposes, such as shipping, billing, or demographic analysis.',
    scope = 'my_db.finance.customer_address',
    always_include = True
)
```

**Add unstructured data source (such as json, or plain text document) as external knowledge base**

There're some cases you want to add unstructured data source as external knowledge base, so that Waii can use it to generate better query. You can add a statement with `always_include=False`, and specify `lookup_summaries` to specify the "search summaries" for this statement.

For example, assume you have a database of JIRA ticket, if you want to a knowledge base of all the JIRA tickets, you can add statements like this:

```python
statement = SemanticStatement(
    id = '',
    statement = """{
    "ticket_id": "JIRA-123",
    "summary": "User run into authentication issues when using the co-pilot feature",
    "description": "...",
    "assignee": "..."
    ... (other fields)
    }
    """,
    always_include = False,
    lookup_summaries = ['JIRA-123', 'User run into authentication issues when using the auto-pilot feature'],
    summarization_prompt = 'Output short summary (in 20 words) of the ticket ```{statement}```:'
)
```

When user ask question `Give me number of tickets related to co-pilot authentication issues`, Waii will use the `lookup_summaries` to match the statement. And bring the statement to the generated query.

You can specify multiple `lookup_summaries` to make sure it can match the statement in different cases. If you don't specify one, we will use the statement as search key. Our recommendation is, if you think a short summary can help to match the statement, you should specify it as `lookup_summaries`.

`Summarization_prompt` is used to extract content from the statement, if not specified, then use the entire statement as-is during query generation. If your statement is too long, a good practice is to specify a summarization prompt, so that Waii can use it to extract content from the statement. Alternatively, you can pre-summarize the original documentation and add it as `statement` field. But that also loses the flexibility of using the original documentation. 

There're two placeholders for `summarization_prompt`, `{statement}` and `{ask}`: You must include `{statement}` in the summarization prompt, which will be replaced by the statement. You can also include `{ask}` in the summarization prompt, which will be replaced by the ask in the query generation request.

### Get Semantic Context

```python
SemanticContext.get_semantic_context(params: GetSemanticContextRequest = GetSemanticContextRequest()) -> GetSemanticContextResponse
```

This method fetches the current semantic context.

Example: 

Fetch all statements (with pagination)
```python
# first get how many statements are there
s = WAII.SemanticContext.get_semantic_context(GetSemanticContextRequest(filter=GetSemanticContextRequestFilter(), limit=0))

# then iterate through the statement using pagination (100 per page)
for i in range(0, s.available_statements, 100):
    s = WAII.SemanticContext.get_semantic_context(GetSemanticContextRequest(filter=GetSemanticContextRequestFilter(), limit=100, offset=i))
    print(f"Retrieved {len(s.semantic_context)} statements, page {i//100+1}, remaining pages {s.available_statements//100 - i//100}")
```

Fetch always_include=False statements only
```python
from waii_sdk_py.semantic_context import GetSemanticContextRequest, GetSemanticContextRequestFilter

s = WAII.SemanticContext.get_semantic_context(GetSemanticContextRequest(
    filter=GetSemanticContextRequestFilter(always_include=False),
    search_text='log4j CVE', 
    limit=5)
)

# print all statements
print(s.semantic_context)
```

The above example searches the semantic context with the search text `log4j CVE`, and limit the result to 5. If you don't specify search_text, it will apply to all statements. If you don't specify limit, it will return first 1000 statements.
