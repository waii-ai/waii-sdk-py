# Waii Python SDK Documentation

The `waii-sdk-py` is a Python library that allows you to interact with the Waii API. It provides a powerful SQL and AI capability to your Python applications. 

## Installation

To install the `waii-sdk-py`, you can use pip:

```bash
pip install waii-sdk-py
```

## Importing the SDK

```python
from waii_sdk_py import WAII
```

## Initializing the SDK

Before using any of the functionality of the SDK, you must initialize it:

```python
WAII.initialize("<your-api-url>", "<your-api-key>")
```

## Modules

The SDK consists of the following modules:

- `Database`
- `Query`
- `SemanticContext`
- `History`

Each module encapsulates a certain functionality of the Waii API.

### Database

The `Database` module contains methods for handling database-related tasks.

Here are some of its methods:

#### Modify Connections

```python
Database.modify_connections(params: ModifyDBConnectionRequest) -> ModifyDBConnectionResponse
```

This method allows to modify the database connections.

#### Get Connections

```python
Database.get_connections(params: GetDBConnectionRequest = GetDBConnectionRequest()) -> GetDBConnectionResponse
```

This method fetches the list of available database connections.

#### Activate Connection

```python
Database.activate_connection(key: str)
```

This method sets the scope of the current database connection.

#### Get Default Connection
```python
Database.get_default_connection()
```

This method gets the scope of the current database connection.

#### Get Catalogs

```python
Database.get_catalogs(params: GetCatalogRequest = GetCatalogRequest()) -> GetCatalogResponse
```

This method retrieves the list of available catalogs.

#### Update Table and Schema Descriptions

```python
Database.update_table_description(params: UpdateTableDescriptionRequest) -> UpdateTableDescriptionResponse
Database.update_schema_description(params: UpdateSchemaDescriptionRequest) -> UpdateSchemaDescriptionResponse
```

These methods update the corresponding descriptions of the objects within the database

### Query

The `Query` module contains methods related to SQL query handling.

Here are some of its methods:

#### Generate

```python
Query.generate(params: QueryGenerationRequest) -> GeneratedQuery
```

This method generates a SQL query based on the provided parameters.

#### Run

```python
Query.run(params: RunQueryRequest) -> GetQueryResultResponse
```

This method runs a SQL query and fetches the results.

#### Like

```python
Query.like(params: LikeQueryRequest) -> LikeQueryResponse
```

This method marks a query as "liked".

#### Submit

```python
Query.submit(params: RunQueryRequest) -> RunQueryResponse
```

This method submits a SQL query.

#### Get Results

```python
Query.get_results(params: GetQueryResultRequest) -> GetQueryResultResponse
```

This method fetches the result of a previously submitted query.

#### Cancel

```python
Query.cancel(params: CancelQueryRequest) -> CancelQueryResponse
```

This method cancels a previously submitted query.

#### Describe

```python
Query.describe(params: DescribeQueryRequest) -> DescribeQueryResponse
```

This method fetches a description of a SQL query.

#### Diff

```python
Query.diff(params: DiffQueryRequest) -> DiffQueryResponse
```

This method generates a description of the difference between two SQL queries

#### Auto Complete

```python
Query.auto_complete(params: AutoCompleteRequest) -> AutoCompleteResponse
```

This method allows you to automatically complete a partial query


#### Analyze Performance

```python
Query.analyze_performance(params: QueryPerformanceRequest) -> QueryPerformanceResponse
```

This method provides a summary of the runtime of a query as well as recommendations on how to make the query run faster

### Semantic Context

The `SemanticContext` module contains methods related to semantic context handling.

Here are some of its methods:

#### Modify Semantic Context

```python
SemanticContext.modify_semantic_context(params: ModifySemanticContextRequest) -> ModifySemanticContextResponse
```

This method allows you to modify the semantic context.

#### Get Semantic Context

```python
SemanticContext.get_semantic_context(params: GetSemanticContextRequest = GetSemanticContextRequest()) -> GetSemanticContextResponse
```

This method fetches the current semantic context.

### History

The `History` module contains methods related to history handling.

Here are some of its methods:

#### List

```python
History.list(params: GetGeneratedQueryHistoryRequest = GetGeneratedQueryHistoryRequest()) -> GetGeneratedQueryHistoryResponse
```

This method fetches the history of generated queries.

For detailed information about the request and response objects and the available properties, refer to the respective Python files of each module.
