# Waii Python SDK Documentation

The `waii-sdk-py` is a Python library that allows you to interact with the Waii API. It provides a powerful SQL and AI capability to your Python applications. 

## Installation

To install the `waii-sdk-py`, you can use pip:

```bash
pip install waii-sdk-py
```

## Importing & Initialize the SDK

```python
>>> from waii_sdk_py import WAII
>>> from waii_sdk_py.query import *
>>> WAII.initialize(api_key="<your-api-key>")
```
You can get your API key from the `tweakit.waii.ai` (You need to register and get access from [waii.ai](waii.ai) first).

![img.png](doc/img.png)

## Get started 

First you can print the list of available databases:

```python
>>> print([conn.key for conn in WAII.Database.get_connections().connectors])
```

Then, you can activate the database connection you want to use (from one of the key in the list above)

```python
>>> WAII.Database.activate_connection("snowflake://...&warehouse=COMPUTE_WH")
```

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

## Use Notebook

You can also use the SDK in Notebooks like Jupyter, you can follow the the doc [here](USE_NOTEBOOK.md)

## Modules

The SDK consists of the following modules:

- `Database`
- `Query`
- `SemanticContext`
- `History`

Each module encapsulates a certain functionality of the Waii API.

## Database

The `Database` module contains methods for handling database-related tasks.

Here are some of its methods:

### Modify Connections

```python
Database.modify_connections(params: ModifyDBConnectionRequest) -> ModifyDBConnectionResponse
```

This method allows to modify the database connections.

`ModifyDBConnectionRequest` contains the following properties:
- `updated`: Update or add new connections
- `removed`: Remove connections, by specifying the key of the connection
- `default_db_connection_key`: Set the default connection (by specifying key of connection)


To add connection, you need to create `DBConnection` Object, which include the following fields
- `key`: Set it to '', it will be auto generated
- `db_type`: Acceptable values are: `snowflake`, `postgresql`, `mongodb`, `mongodb+srv` (Mongo Atlas).
- `description`: Description of the connection
- `account_name`: Account name of the connection, apply to `Snowflake`
- `username`: Username of the connection, can be None if no username needed (such as localhost database)
- `password`: Password of the connection, can be None if no password. 
- `database`: Database name of the connection, you must specify it. Please note that it is case sensitive for most of the databases.
- `warehouse`: Warehouse name of the connection, apply to `Snowflake`
- `role`: Role name of the connection, apply to `Snowflake`
- `host`/`port`: Host/port of the connection, apply to `postgresql` and `mongodb`.
- `sample_col_values`: Do you want to let Waii to sample your string/variant columns. True if you want to sample, False if you don't want to sample. Default is False. This is optional, which can help Waii to generate better queries.

Examples of creating `DBConnection` Object

#### Snowflake
```python
DBConnection(
    key = '',
    db_type = 'snowflake',
    account_name = 'abcde-12345',
    username = 'username',
    password = 'password',
    database = 'database',
    warehouse = 'warehouse',
    role = 'role'
)
```

#### PostgreSQL
```python
DBConnection(
    key = '',
    db_type = 'postgresql',
    username = 'username',
    password = 'password',
    database = 'database',
    host = 'localhost',
    port = 5432
)
```

#### MongoDB
```python
DBConnection(
    key = '',
    db_type = 'mongodb', # or 'mongodb+srv' if you are using Mongo Atlas
    username = 'username',
    password = 'password',
    database = 'database',
    host = 'localhost',
    port = 27017 # if you are using Mongo Atlas, you shouldn't set port
)
```

### Get Connections

```python
Database.get_connections(params: GetDBConnectionRequest = GetDBConnectionRequest()) -> GetDBConnectionResponse
```

This method fetches the list of available database connections.

Response fields:
`connectors`: List of `DBConnection` objects (No password field)
`connector_status`: Status of the connection, are they being indexed or not. 

#### Activate Connection

```python
Database.activate_connection(key: str)
```

This method sets the scope of the current database connection.

You can run
```python
>>> Database.get_activated_connection()
```
To get the current activated connection.

### Get Catalogs

```python
Database.get_catalogs(params: GetCatalogRequest = GetCatalogRequest()) -> GetCatalogResponse
```

This method retrieves the list of available catalogs. It includes a hierarchical list of schemas and tables.

You can run 
```python
>>> WAII.Database.get_catalogs()
```
To get catalogs, response fields:

**CatalogDefinition:**
- `name`: Name of the catalog (database)
  - `schemas`: List of schemas 
    - `name`: Name of the schema 
    - `description`: Description of the schema 
      - `summary`: generated description of the schema 
      - `common_questions`: list of generated common questions
      - `common_tables`: list of common tables used in the schema
      - `tables`: all tables belong to the schema
        - `name`: Name of the table
        - `columns`: List of columns 
          - `name`: Name of the column 
          - `type`: Type of the column 
        - `comment`: Comment of the table (fetched from underlying database) 
        - `last_altered_time`: Last altered time of the table 
        - `refs`: List of referential constraints 
        - `description`: Auto generated table description

Waii automatically generate table/schema descriptions when you add them, you can fetch them by using `description` field of table and schema from `get_catalogs` method.

Description of table looks like: 

```
The CUSTOMER_ADDRESS table contains information about the addresses of customers. It includes details such as address ID, city, country, ... This table can be used to retrieve customer addresses for various purposes, such as shipping, billing, or demographic analysis.
```

### Update Table and Schema Descriptions

You can use the following two methods to update the descriptions of tables and schemas (if you are not satisfied with the auto generated descriptions)

```python
Database.update_table_description(params: UpdateTableDescriptionRequest) -> UpdateTableDescriptionResponse
Database.update_schema_description(params: UpdateSchemaDescriptionRequest) -> UpdateSchemaDescriptionResponse
```

## Query

The `Query` module contains methods related to SQL query handling. 
**Important:** You need to activate the database connection first before using the methods in this module. Otherwise you may trying to generate query from a wrong database.

Here are some of its methods:

### Generate

```python
Query.generate(params: QueryGenerationRequest) -> GeneratedQuery
```

This method generates a SQL query based on the provided parameters.

Parameter fields:
- `ask`: The question you want to ask Waii to generate, such as `How many tables are there?`
- `dialect`: What is the dialect of the generated query, such as `snowflake`, `postgresql`, `mongodb`
- `tweak_history`: We can support both asking new question, or tweak the previous question. If you want to tweak the previous question, you can set this field. (It's list of `Tweak` object). Each of `Tweak` object looks like:
  - `sql`: The SQL query you want to tweak
  - `ask`: The previous question you asked.
- `search_context`: List of scopes to limit tables/schemas used to generate query (By default it searches all objects from the database). It's list of `SearchContext` object. Each of `SearchContext` object looks like:
  - `db_name`: Catalog name (database name), default is `*`
  - `schema_name`: Schema name, default is `*`
  - `table_name`: Table name, default is `*`

**Examples:**
    
Ask a new question:
```python
>>> WAII.Query.generate(QueryGenerationRequest(ask = "How many tables are there?"))
```

**Ask a complex question:**
```python
>>> WAII.Query.generate(QueryGenerationRequest(ask = "Give me all stores in California that have more than 1000 customers, include the store name, store address, and the number of customers."))
```

**Generate query with search context (limited to specific tables, schemas, etc.)**

By default, Waii search all tables in the database, if you know which tables you want to use, you can specify the search context to limit the tables used to generate query.

```python
>>> WAII.Query.generate(QueryGenerationRequest(
    ask = "How many cars we produced in Q2", 
    search_context=[SearchContext(db_name="*",
                                  schema_name="schema1",
                                  table_name="table1"),
                    SearchContext(db_name="*",
                                  schema_name="schema2",
                                  table_name="*")]))
```

The above query will only search tables from `schema1.table1` and `schema2.*`

**Tweak the previous question:**
```python
>>> WAII.Query.generate(QueryGenerationRequest(
    ask = "only return 10 results", 
    tweak_history=[Tweak(sql="select * from information_schema.tables", 
                         ask="give me all tables")]))
```
(The above tweak will return the first 10 results of the previous query)

#### `Query.generate` returns `GeneratedQuery` object, which contains the following fields:
- `uuid`: UUID of the generated query
- `liked`: Whether the query is liked or not (True/False). You can like a query by using `Query.like` method.
- `query`: The generated query text
- `tables`: Tables used in the generated query
- `semantic_context`: Semantic context applied to the generated query
- `detailed_steps`: Detailed steps of how the query work (in natural language)
- `what_changed`: If you do a tweak, it will tell you what changed in the query
- `compilation_error`: If there is any compilation error, it will show here. (Waii will try to fix the compilation error automatically, but if it tried multiple times and still cannot fix it, it will show here)

### Transcode

```python
>>> WAII.Query.transcode(TranscodeQueryRequest(source_dialect="postgres", source_query="select ...;", target_dialect="snowflake", ask="..."))
```

Parameter fields:
- `search_context`: Same as `Query.generate`, you can specify the search context to limit the tables/schemas used to transcode.
- `source_dialect`: The dialect of the source query, such as `snowflake`, `postgresql`, `mongodb`
- `source_query`: The source query you want to transcode
- `target_dialect`: The dialect of the target query, such as `snowflake`, `postgresql`, `mongodb`
- `ask`: The intructions you want to ask Waii to add when transcode the query, such as `place tables under schema1`. It is optional.


#### `Query.transcode` returns `GeneratedQuery` object



### Run a query (sync)

```python
Query.run(params: RunQueryRequest) -> GetQueryResultResponse
```

Request fields:
- `query`: The SQL query you want to run
- `session_id`: Session ID of the query, default is None (which means Waii will generate a new session ID for you)
- `current_schema`: current schema to run the query, default is None (which means Waii will use the default schema of the connection)
- `session_parameter`: a key value pairs to set the connection parameters, such as auto_commit, isolation_level, etc. Default is None (which means Waii will use the default connection parameters of the connection)

Response fields:
- `rows`: List of rows returned. Each of row is json object, with column name as key, and column value as value.
- `more_rows`: Whether there are more rows or not (True/False), it can be True when `max_returned_rows` is set and generated rows are more than `max_returned_rows`
- `column_definitions`: List of column definitions. Each of column definition has name and type
- `query_uuid`: UUID of the query (it is different from generate query UUID, this UUID is generated by underlying database and Snowflake)

Example:

```python
>>> print(WAII.Query.run(RunQueryRequest(query = "SELECT COUNT(DISTINCT table_name) FROM waii.information_schema.tables")))

rows=[{'COUNT(DISTINCT TABLE_NAME)': 112}] more_rows=0 column_definitions=[ColumnDefinition(name='COUNT(DISTINCT TABLE_NAME)', type='FIXED', comment=None, sample_values=None)] query_uuid='01afbd1e-0001-d31e-0022-ba8700a8209e'
```


### Async submit a query

In order to async submit query, you need 3 methods: `Query.submit`, `Query.get_results`, `Query.cancel`

#### Submit

```python
Query.submit(params: RunQueryRequest) -> RunQueryResponse
```

Request fields same as `Query.run`

Response field:
- `query_id`: the query id you need to get result of the query, or cancel the query

#### Get Results

```python
Query.get_results(params: GetQueryResultRequest) -> GetQueryResultResponse
```

Return query result by providing uuid, same as `Query.run`, but you need to specify `query_id` instead of `query` in the request.

#### Cancel

```python
Query.cancel(params: CancelQueryRequest) -> CancelQueryResponse
```

Cancel a running query by providing `query_id`, it is a no-op if the query is completed or failed.

### Like

```python
Query.like(params: LikeQueryRequest) -> LikeQueryResponse
```

This method marks a query (by specifying `uuid` for generated query, not id from run query) as "liked", which you can fetch it from history.

### Describe

If you want to translate SQL to natural language, and explain step-by-step plans, you can use `Query.describe` method.

```python
Query.describe(params: DescribeQueryRequest) -> DescribeQueryResponse
```

This method fetches a description of a SQL query.

Parameters:
- `query`: The SQL query you want to describe
- `search_context`: When describe the query, you may want to restrict which table/schema you want to use as context. Normally it is not required, and you should skip it.

Output:
- `summary`: A summary of the query
- `detailed_steps`: Detailed steps of how the query work (in natural language)
- `tables`: Tables used in the query

Example:

```python
>>> print(WAII.Query.describe(DescribeQueryRequest(query='SELECT COUNT(DISTINCT table_name) FROM information_schema.tables')))

summary='How many distinct table names are there in the information_schema.tables?' detailed_steps=['Step 1: Access the information_schema.tables table.', 'Step 2: Count the number of distinct table names.', 'Step 3: Return the count of distinct table names.'] tables=[TableName(table_name='TABLES', schema_name='INFORMATION_SCHEMA', database_name='WAII')]
```

### Diff

This method generates a description of the difference between two SQL queries
```python
Query.diff(params: DiffQueryRequest) -> DiffQueryResponse
```

Parameters:
- Similar to `Query.describe`, you need to specify two queries you want to diff, and optionally you can specify the search context.
- `query`: The SQL query you want to describe
- `previous_query`: The previous SQL query you want to describe

Output:
- Same as `Query.describe`, but it will also include `what_changed` field, which tells you what changed in the query.

Example:

```python
>>> print(WAII.Query.diff(DiffQueryRequest(query='SELECT COUNT(DISTINCT table_name) FROM information_schema.tables', previous_query='SELECT COUNT(DISTINCT table_name) FROM information_schema.tables WHERE table_name LIKE \'%a%\'')))

summary='...' detailed_steps=[...] what_changed="The new query does not have any filter on 'table_name' column."
```

#### Auto Complete (Experimental)

This method allows you to automatically complete a partial query, this can be useful when you want to build a query editor with Github co-pilot-like auto complete feature.

This is an experimental feature, it may not work well in some cases.

```python
Query.auto_complete(params: AutoCompleteRequest) -> AutoCompleteResponse
```

Parameters:
- `text`: (required) The partial query you want to auto complete
- `cursor_offset`: (required) The cursor offset of the partial query, it can be in the middle of the text (if you want to insert text in the middle. By default you should set it to 
- `dialect`: The dialect of the query, such as `snowflake`, `postgresql`, `mongodb`
- `search_context`: Same as `Query.describe`, you can specify the search context to limit the tables/schemas used to auto complete.
- `max_output_tokens`: (required) Maximum number of tokens returned, you should set it to a lower value like 50 to make sure it can return within a few seconds.

Output: 
- `text` completed text

Example:
```python
>>> print(WAII.Query.auto_complete(AutoCompleteRequest(text='select from', cursor_offset=11, max_output_tokens=50)))

text='WAII.WORLD.CITY WHERE POPULATION > 1000000'
```


#### Analyze Performance

Note: this feature currently only support Snowflake

```python
Query.analyze_performance(params: QueryPerformanceRequest) -> QueryPerformanceResponse
```

Parameters:
- `query_id`: The query id you want to analyze performance (it should be a run query id, not generated query id

Output:
- `summary`: A summary of the runtime of a query as well as recommendations on how to make the query run faster
- `recommendations`: List of recommendations on how to make the query run faster
- `query_text`: The query text of the query (based on query_id) 
- `execution_time_ms`: The execution time of the query (based on query_id)
- `compilation_time_ms`: The compilation time of the query (based on query_id)

This method provides a summary of the runtime of a query as well as recommendations on how to make the query run faster

Examples: 

```python
>>> print(WAII.Query.analyze_performance(QueryPerformanceRequest(query_id='...')))

'summary': [
    'The metadata operation in Step 1 took 1.0 ms, which is 82% of the total execution time.',
],
'recommendations': [
    "The query is already optimal as it is a simple count distinct operation on the 'table_name' column of the 'waii.information_schema.tables' table. No further optimization is required.",
      ...
],
'query_text': "SELECT COUNT(DISTINCT table_name) FROM waii.information_schema.tables",
'execution_time_ms': 312,
'compilation_time_ms': 247
```

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
