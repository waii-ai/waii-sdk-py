---
id: sql-query-module
title: SQL Query
---


The `Query` module contains methods related to SQL query handling.

**Important:** You need to activate the database connection first before using the methods in this module. Otherwise you may trying to generate query from a wrong database.
```python
WAII.Database.activate_connection("snowflake://...&warehouse=COMPUTE_WH")
```

Here are some of its methods:

### Generate Query

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
>>> WAII.Query.generate(QueryGenerationRequest(ask = """
    Give me all stores in California that have more than 1000
    customers, include the store name, store address, and the number of 
    customers."""))
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
- `confidence_score`: returns logprob confidence score based on the tokens from generated queries.
- `llm_usage_stats`: token consumption during the query generation.
  - `token_total`: total token usage (prompt + completed), this doesn't include cached tokens. So if you see the total_total = 0, the query is fetched from the cache.
- `is_new`: whether the query is new or tweak
- `timestamp_ms`: total elapsed time (in milli-seconds) between RPC request/response.

### Generate Question

You can also generate questions based on your database schema, which can be useful when you want to show to your user what kind of questions can be asked to the database.

```python
>>> Query.generate_question(GenerateQuestionRequest(schema_name='PUBLIC',
                                                    n_questions=10,
                                                    complexity=GeneratedQuestionComplexity.hard))
```

Parameter fields:
- `schema_name`: The schema name you want to generate questions. This is must be specified.
- `n_questions`: Number of questions you want to generate. Default is 10. You can choose a number between 1 to 30. 
- `complexity`: Complexity of the questions you want to generate. Default is `GeneratedQuestionComplexity.hard`. You can choose `easy`, `medium`, `hard`.

Output `GenerateQuestionResponse`, fields:
- `questions`: List of generated questions. For each question it has `question` (string content of the question), `complexity` (complexity of the question) and tables (tables used in the question)


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


`Query.transcode` returns `GeneratedQuery` object

### Run a query (sync)

```python
Query.run(params: RunQueryRequest) -> GetQueryResultResponse
```

Request fields:
- `query`: The SQL query you want to run
- `session_id`: Session ID of the query, default is None (which means Waii will generate a new session ID for you)
- `current_schema`: current schema to run the query, default is None (which means Waii will use the default schema of the connection). It is `SchemaName` object, which has `database_name` (optional), `schema_name` fields.
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

Run with default schema
```python
from waii_sdk_py.database import *
>>> WAII.Query.run(RunQueryRequest(query='select current_schema(), current_database();', current_schema=SchemaName(schema_name='INFORMATION_SCHEMA')))
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

`LikeQueryRequest` has the following fields:
```
    query_uuid: Optional[str]
    ask: Optional[str]
    query: Optional[str]
    liked: Optional[bool] = True
    rewrite_question: Optional[bool] = True
```

You can specify a query is liked or unliked by set `liked` to True/False

You can either like an generated query by specifying `query_uuid` (the `uuid` from `GeneratedQuery`, not the id from run query).

Or, you can specify `ask` and `query` to like a query.

Important: `rewrite_question` is optional, if you set it to True (default), the system will rewrite the ask based on query and the ask. Why we do this because sometimes the ask itself is wrong, ambiguous, etc. and we want to make sure the ask is clear. 
However, sometimes you may want to keep the original ask, you can set it to False.

Examples: 

Like a generated query
```python
WAII.Query.like(LikeQueryRequest(query_uuid='01afbd1e-0001-d31e-0022-ba8700a8209e', liked=True))
```

Like a query by specifying `ask` and `query`
```python
WAII.Query.like(LikeQueryRequest(ask='How many tables are there?', 
                                 query='SELECT COUNT(DISTINCT table_name) FROM waii.information_schema.tables', liked=True))
```

You will get an exception if the call is failed.


### Describe

If you want to translate SQL to natural language, and explain step-by-step plans, you can use `Query.describe` method.

```python
Query.describe(params: DescribeQueryRequest) -> DescribeQueryResponse
```

This method fetches a description of a SQL query.

Parameters:
- `query`: The SQL query you want to describe
- `search_context`: When describe the query, you may want to restrict which table/schema you want to use as context. Normally it is not required, and you should skip it.
- `current_schema`: current schema of the query

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


#### Analyze Performance (Experimental)

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
