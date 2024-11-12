---
id: database-module
title: Database
---

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
- `username`: Username of the connection, can be None if no username needed (such as localhost database or push based database)
- `password`: Password of the connection, can be None if no password. 
- `database`: Database name of the connection, you must specify it. Please note that it is case sensitive for most of the databases.
- `warehouse`: Warehouse name of the connection, apply to `Snowflake` (not needed for push based database)
- `role`: Role name of the connection, apply to `Snowflake` ((not needed for push based database))
- `host`/`port`: Host/port of the connection, apply to `postgresql` and `mongodb`. For push based database it does not have to be correct host. It just needs to be unique identifier.
- `sample_col_values`: Do you want to let Waii to sample your string/variant columns. True if you want to sample, False if you don't want to sample. Default is False. This is optional, which can help Waii to generate better queries.
- `db_content_filters`: If you want Waii to exclude certain columns , tables from database while generating the query, you can pass the db_content_filter. This is optional.
- `always_include_tables`: If it is not None, then these tables will always be included, even if table selector doesn't select them
- `embedding_model`: Embedding model used for similarity search within the knowledge graph.
- `alias`: Alias of the connection, which can be used to refer the connection in the query. If it is not set, then we will generate a key based on the connection details. This allows you to add multiple connections to the same database with different alias, you can set different db_content_filters, etc.

#### DBContentFilter

If you need to exclude certain columns, tables from database while generating the query, you can pass the db_content_filter. It has the following fields:
- `filter_scope`: DBContentFilterScope, it could be either `schema`, `table`, `column`
- `filter_type`: DBContentFilterType, it could be either `include` or `exclude`
- `filter_action_type`: DBContentFilterActionType, it could be either `visibility` or `access`
  - `visibility`: It will hide the columns/tables from the query generation, and it won't stored in the knowledge graph.
  - `sample_values`: It will hide the certain columns/tables from the sampling (even if the db_connection is set to sample_col_values=True).
- `pattern`: Regex pattern to match the schema/table/column name
  - For example, if you want to exclude all the tables which start with `temp_`, you can set the pattern to `^temp_.*`
  - Multiple patterns can be provided by separating them with `|`. For example, `(^sf1$|^sf100$)` will match `sf1` and `sf100`
  - You can also do exact match by setting the pattern to `^temp_table$`
- `ignore_case`: If it is True, then the pattern will be case insensitive. Default is True.
- `search_context`: List of `SearchContext` objects. If you want to apply the filter based on a subset of the tables/schema. By default it will apply to all the tables/schemas.
- Multiple filters can be applied, they are connected by `AND` operator:
  - For example, if you want to include table1, table2 from schema1, you can add two filters:
    - Filter1: scope=table, type=include, action=visibility, pattern=(^table1$|^table2$)
    - Filter2: scope=schema, type=include, action=visibility, pattern=schema1

Example of creating `DBContentFilter` object:

1) Filter tables from different schemas via search_context of `DBContentFilter`

```python
WAII.Database.modify_connections(ModifyDBConnectionRequest(
    updated=[
        DBConnection(
            db_type="...",
            username="...",
            password="...",
            database="test",
            host='1.2.3.4',
            port=1433,
            db_content_filters=[DBContentFilter(
                filter_scope=DBContentFilterScope.table,
                filter_type=DBContentFilterType.include,
                filter_action_type=DBContentFilterActionType.visibility,
                pattern='',  # empty regex pattern matches all
                search_context=[
                    SearchContext(db_name='*', schema_name='schema1', table_name='t1'),
                    SearchContext(db_name='*', schema_name='schema2', table_name='t2'),
                    SearchContext(db_name='*', schema_name='schema2', table_name='t3')
                ]
            )]
        )
    ]
))
```

The above example will include tables `t1` from `schema1`, `t2` and `t3` from `schema2` and exclude all other tables.

2) Filter table1, table2, table3 from schema1, schema2
```python
DBConnection(
  # other fields
  # ...
  db_content_filters = [
    DBContentFilter(
        filter_scope=DBContentFilterScope.table,
        filter_type=DBContentFilterType.include,
        filter_action_type=DBContentFilterActionType.visibility,
        pattern='(^table1$|^table2$|^table3$)',
        ignore_case=True,
    ),
    DBContentFilter(
        filter_scope=DBContentFilterScope.schema,
        filter_type=DBContentFilterType.include,
        filter_action_type=DBContentFilterActionType.visibility,
        pattern='(^schema1$|^schema2$)',
        ignore_case=True,
    )
])
```

3) Exclude all columns start with `temp_` from all the tables

```python
db_content_filters = [
    DBContentFilter(
        filter_scope=DBContentFilterScope.column,
        filter_type=DBContentFilterType.exclude,
        filter_action_type=DBContentFilterActionType.visibility,
        pattern='^temp_.*',
        ignore_case=True,
    )
]
```


#### Examples of creating `DBConnection` Object

##### Snowflake
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

##### PostgreSQL / MySQL / Trino / SQLServer, etc.

This applies to all the databases which uses username/password/host/port to connect.

```python
DBConnection(
    key = '',
    db_type = 'postgresql' # or 'mysql', 'trino', 'sqlserver', etc.
    username = 'username',
    password = 'password',
    database = 'database',
    host = 'localhost',
    port = 5432
)
```

##### MongoDB
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

##### Push-based Database

Examples of creating push based `DBConnection` Object. It is same for all the databases, you just need to set db_type to the database you are using. And set push to True.
```python
DBConnection(
    key = '',
    db_type = 'snowflake'/'postgresql'/'mongodb', # depending on the db_type
    database = 'database',
    host = 'test_host', # it needs to be unique identifier
    push = True # required for push based database
)
```

##### Use alias to add multiple connections for the same database

Assume you have a SQL server database `test`, which has two schemas `schema1` and `schema2`. You want to add two connections for the same database, but with different schema filters. You can use alias to achieve this.

(Otherwise, Waii will generate a key based on the connection details, which is the same for both connections. So the latter connection will overwrite the former connection)

```python
response = WAII.Database.modify_connections(ModifyDBConnectionRequest(
    updated=[
        DBConnection(
            db_type="sqlserver",
            username="...",
            password="...",
            database="test",
            host='...',
            port=1433,
            alias='team_1_connection',
            db_content_filters=[DBContentFilter(
                filter_scope=DBContentFilterScope.table,
                filter_type=DBContentFilterType.include,
                filter_action_type=DBContentFilterActionType.visibility,
                pattern='',  # empty regex pattern matches all
                search_context=[
                    SearchContext(db_name='*', schema_name='common', table_name='*'),
                    SearchContext(db_name='*', schema_name='team1', table_name='t1'),
                    SearchContext(db_name='*', schema_name='team1', table_name='t2')
                ]
            )]
        )
    ]
))
print([c.key for c in Database.get_connections().connectors])
```

The above example will add a connection with alias `team_1_connection` and include tables `t1` and `t2` from `team1` schema and all tables from `common` schema.

The newly added connection will have a key = `waii://waii@host/team_1_connection` (which you can find it from the above print statement)

If you want to add another connection with different schema filters, you can do the following:

```python
response = WAII.Database.modify_connections(ModifyDBConnectionRequest(
    updated=[
        DBConnection(
            db_type="sqlserver",
            # .. other fields of the db connection
            alias='team_2_connection',
            db_content_filters=[DBContentFilter(
                filter_scope=DBContentFilterScope.table,
                filter_type=DBContentFilterType.include,
                filter_action_type=DBContentFilterActionType.visibility,
                pattern='',  # empty regex pattern matches all
                search_context=[
                    SearchContext(db_name='*', schema_name='common', table_name='def1'),
                    SearchContext(db_name='*', schema_name='team2', table_name='t2'),
                    SearchContext(db_name='*', schema_name='team2', table_name='t3')
                ]
            )]
        )
    ]
))
```

The above example will add a connection with alias `team_2_connection` and include tables `t2` and `t3` from `team2` schema and `def1` from `common` schema.

### Get Connections

```python
Database.get_connections(params: GetDBConnectionRequest = GetDBConnectionRequest()) -> GetDBConnectionResponse
```

This method fetches the list of available database connections.

Response fields:
`connectors`: List of `DBConnection` objects (No password field)
`connector_status`: Status of the connection, are they being indexed or not. 

### Activate Connection

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

Request fields:
- `ask`: You can do semantic search by providing a question here. For example, "How many cars sold in 2021?". Waii will try to filter the tables/cols based on the question.
  - Notes: It is possible that the question cannot be answered by the database, in that case, you will get an empty response.
- `search_context`: List[SearchContext] - You can provide a list of search contexts to filter the tables/cols. For example, you can provide a list of table names, column names, etc. Waii will try to filter the tables/cols based on the search contexts.

You can run 
```python
>>> WAII.Database.get_catalogs()
```
To get all catalogs. 

Or you can run
```python
tables = WAII.Database.get_catalogs(
    GetCatalogRequest(ask=
                      'give me tables which i can use to answer "how many ssh_keys do i have"'))
```

To do a semantic search.

Response fields:

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
        - `description`: Auto generated description of the column
      - `comment`: Comment of the table (fetched from underlying database)
      - `last_altered_time`: Last altered time of the table
      - `refs`: List of referential constraints
      - `inferred_refs`: List of auto-inferred referential constraints
      - `inferred_constraints`: List of auto-inferred constraints (pks, etc.)
      - `description`: Auto generated table description

Waii automatically generate table/schema descriptions when you add them, you can fetch them by using `description` field of table and schema from `get_catalogs` method.

Description of table looks like: 

```
The CUSTOMER_ADDRESS table contains information about the addresses of customers. It includes details such as address ID, city, country, ... This table can be used to retrieve customer addresses for various purposes, such as shipping, billing, or demographic analysis.
```

### Update Table, Schema Descriptions

You can use the following methods to update the descriptions of tables and schemas (if you are not satisfied with the auto generated descriptions)

```python
Database.update_table_description(params: UpdateTableDescriptionRequest) -> UpdateTableDescriptionResponse
Database.update_schema_description(params: UpdateSchemaDescriptionRequest) -> UpdateSchemaDescriptionResponse
```

Examples:

```python
response = WAII.Database.update_table_description(UpdateTableDescriptionRequest(
    table_descriptions=[
        TableDescription(
            table_name=TableName(database_name='WAII', schema_name='PUBLIC', table_name='CUSTOMER_ADDRESS'),
            description='The CUSTOMER_ADDRESS table contains information about the addresses of customers. It includes details such as address ID, city, country, ... This table can be used to retrieve customer addresses for various purposes, such as shipping, billing, or demographic analysis.'
        )
    ]
))
```

### Update Column Description

API:

```python
Database.update_column_description(params: UpdateColumnDescriptionRequest) -> UpdateColumnDescriptionResponse
```

Example:

```python
# update col description 
col_desc = [
    # you can add multiple tables in one request
    TableToColumnDescription(
        # table name, you need to include schema_name, database_name, and they are case sensitive
        table_name=TableName(database_name='WAII', schema_name='BATTLE_DEATH', table_name='BATTLE'),
      
        # a list of column descriptions, you can add multiple columns in one request
        column_descriptions=[
            ColumnDescription(column_name='id', description='manual updated id'),
            ColumnDescription(column_name='battle_deaths', description='Number of deaths in the battle'),
            ColumnDescription(column_name='name', description='manual updated name'),
            ColumnDescription(column_name='description', description='Description of the battle')
        ]
    )
  
    # more tables if you want
]

response = WAII.Database.update_column_description(UpdateColumnDescriptionRequest(
    col_descriptions=col_desc
))

print(f"Successfully updated table to columns: {response.updated_table_to_cols}")
```

The response will be `UpdateColumnDescriptionResponse` object, which includes

```
class UpdatedTableToCol(BaseModel):
    table_name: TableName
    column_names: Optional[List[str]]


class UpdateColumnDescriptionResponse(BaseModel):
    updated_table_to_cols: Optional[List[UpdatedTableToCol]]
```

You should check the `updated_table_to_cols` to see which tables/columns are updated successfully. We will ignore the columns that are not found in the database.

### Add/Update Table definitions

You can use the following method to update table definitions for push based database

```python
Database.update_table_definition(params: UpdateTableDefinitionRequest) -> UpdateTableDefinitionResponse
```

Examples:

```python

table_definition =  TableDefinition(
            name=TableName(
                database_name="db1", schema_name="schema2", table_name="table2"
            ),
            columns=[
                ColumnDefinition(name="col1", type="int"),
                ColumnDefinition(name="col2", type="int"),
                ColumnDefinition(name="col3", type="int"),
                ]
            )
update_table_req = UpdateTableDefinitionRequest(updated_tables = [table_definition]
                                                )
result = WAII.Database.update_table_definition(update_table_req)
```

### Remove Tables

You can use the following method to remove tables from push based database

```python
Database.update_table_definition(params: UpdateTableDefinitionRequest) -> UpdateTableDefinitionResponse
```

Examples:

```python

table_name = TableName(
                database_name="db1", schema_name="schema2", table_name="table2"
            )


update_table_req = UpdateTableDefinitionRequest(removed_tables = [table_name]
                                                )
result = WAII.Database.update_table_definition(update_table_req)
```

### Update Constraints

API:

```python
Database.update_constraint(params: UpdateConstraintRequest) -> UpdateConstraintResponse
```
`UpdateConstraintRequest` contains the following properties:
- `updated_constraints`: List of TableConstraints to be updated

`TableConstraints` contains the following properties:
- `table_name`: `TableName` for which constraints to be updated
- `constraints` List of `Constraint` object to be updated
- `constraint_type`: Type of constraint that needs to be updated.It could be either ConstraintType.primary or ConstraintType.foreign.
                     Note: Only one kind of Constraint can be updated at a time. So in list of constraint all constraints should be either of primary type or 
                     all constraint should be of foreign type.

`Constraint` contains the following properties:
- `table`: `TableName` for which constraints is getting updated.
- `cols`: List of string representing column names of constraint.
- `constraint_type`: Type of the constraint. it could be either ConstraintType.primary or ConstraintType.foreign
- `src_table`: Only applicable when you are adding ConstraintType.foreign constraint. It is `TableName` where foreign key is referenced to.
- `src_cols`: Only applicable when you are adding ConstraintType.foreign constraint.It is list of string representing column names of constraint in src_table.
- `comment`: Any comment you want to add for constraint(Optional)

Update constraint function returns `UpdateConstraintResponse`.It containts following properties.

`updated_tables`: List of `TableName` which got updated

Examples:
```python
--- For updating foreign key constraints
Suppose there are two tables `orders` and `products`. There is a column in orders table called `product_id`
which is a foreign key reference to `id` column in products table.
If you want to add this constraint, our request will be 

table_name = TableName(table_name= 'products', schema_name = 'schema1', database_name = 'db1')
src_table_name = TableName(table_name= 'orders', schema_name = 'schema1', database_name = 'db1')
constraint = Constraint(table=table_name, cols=['product_id'],constraint_type = ConstraintType.foreign,
                        src_table = src_table_name, src_cols = ['id'])
table_constraints = TableConstraint(table_name = table_name, constraints = [constraint], constraint_type = ConstraintType.foreign)
req = UpdateConstraintRequest(updated_constraints = [table_constraints])
result = WAII.Database.update_constraint(req)

--- For updating primary key constraint
Suppose we want to set id column as primary key in products table. The request would look like.
table_name = TableName(table_name= 'products', schema_name = 'schema1', database_name = 'db1')
constraint = Constraint(table=table_name, cols=['id'],constraint_type = ConstraintType.primary)
table_constraints =  TableConstraint(table_name = table_name, constraints = [constraint],
                                     constraint_type = ConstraintType.primary)
req = UpdateConstraintRequest(updated_constraints = [table_constraints])
result = WAII.Database.update_constraint(req)

```

### Index Column Values

#### Overview

This document describes how to use the methods related to similarity search indexing in the Waii SDK. These methods allow you to update, get, and delete column value indexes for similarity search.

#### Method Signatures

##### Update Similarity Search Index

```python
Database.update_similarity_search_index(request: UpdateSimilaritySearchIndexRequest) -> CommonResponse
```

##### Get Similarity Search Index

```python
Database.get_similarity_search_index(request: GetSimilaritySearchIndexRequest) -> GetSimilaritySearchIndexResponse
```

##### Delete Similarity Search Index

```python
Database.delete_similarity_search_index(request: DeleteSimilaritySearchIndexRequest) -> CommonResponse
```

#### Request and Response Objects

##### UpdateSimilaritySearchIndexRequest

- `column`: ColumnName - Specifies the column to be indexed
- `values`: Optional[List[ColumnValue]] - Optional list of column values to be indexed

##### GetSimilaritySearchIndexRequest

- `column`: ColumnName - Specifies the column for which to retrieve the index

##### GetSimilaritySearchIndexResponse

- `column`: ColumnName - The column for which the index was retrieved
- `values`: Optional[List[ColumnValue]] - The indexed column values

##### DeleteSimilaritySearchIndexRequest

- `column`: ColumnName - Specifies the column for which to delete the index

##### ColumnValue Object

A `ColumnValue` object has two fields:
- `value`: The actual value of the column in the table
- `additional_info`: Optional list of strings providing additional meanings for the value

#### Methods to Provide Column Values

##### 1. Manual Value Provision

Manually provide a list of `ColumnValue` objects:

```python
WAII.database.update_similarity_search_index(UpdateSimilaritySearchIndexRequest(
    column=movie_title_column,
    values=[
        ColumnValue(value="Avengers: Final Chapter", additional_info=["Avengers: Endgame (2019)"]),
        ColumnValue(value="The Good, the Bad and the Ugly", additional_info=["Le Bon, la Brute et le Truand"]),
        ColumnValue(value="Interstellar"),
    ]
))
```

When you use the `additional_info` field, consider the following:

Use the `additional_info` field in the following scenarios:

1. For code values where additional_info provides the meaning
   - Example: `NY.GDP.MKTP.CD` is a code for GDP in the World Bank dataset, the additional info would be `GDP (current US$)`
2. For alternative names or translations of a value
   - Example: `The Good, the Bad and the Ugly` is also known as `Le Bon, la Brute et le Truand` (in French)
3. Leave empty if the value is self-explanatory
   - Example: `Interstellar`

##### 2. Specify Column Only

Let Waii query the database for unique values of the specified column:

```python
WAII.database.update_similarity_search_index(UpdateSimilaritySearchIndexRequest(
    column=movie_title_column
))
```

Internally, Waii will run a `SELECT DISTINCT <COLUMN_NAME> FROM <TABLE_NAME>` query to fetch unique values for the specified column.

##### 3. Use Query Results

Use a custom query to fetch values and create `ColumnValue` objects, then update the index:

Since Waii has API to run queries, you can use the query results to create `ColumnValue` objects and update the index.

```python
query_results = WAII.query.run(RunQueryRequest(
    query="select distinct asset_title, asset_local_name from movies_and_tv.movies limit 5"
))

column_values = [
    ColumnValue(value=row['ASSET_TITLE'], additional_info=[row['ASSET_LOCAL_NAME']])
    for row in query_results.rows
    if row['ASSET_TITLE'] is not None
]

WAII.database.update_similarity_search_index(UpdateSimilaritySearchIndexRequest(
    column=movie_title_column,
    values=column_values
))
```

The above example fetches the `ASSET_TITLE` and `ASSET_LOCAL_NAME` (more like an alternative name) columns from the `movies_and_tv.movies` table and creates `ColumnValue` objects for each row.

#### Getting Similarity Search Index

To retrieve the current similarity search index for a column:

```python
response = WAII.database.get_similarity_search_index(GetSimilaritySearchIndexRequest(
    column=movie_title_column
))

# Access the indexed values
indexed_values = response.values
```

#### Deleting Similarity Search Index

To delete the similarity search index for a column:

```python
WAII.database.delete_similarity_search_index(DeleteSimilaritySearchIndexRequest(
    column=movie_title_column
))
```

#### Notes and Limitations

- Currently only works for text columns
- Maximum of 5000 ColumnValues per column
- The update method is a synchronous call that computes embeddings for column values, so it may not be immediate

#### Responses

- `update_similarity_search_index` and `delete_similarity_search_index` return a `CommonResponse` object.
- `get_similarity_search_index` returns a `GetSimilaritySearchIndexResponse` object containing the indexed column values.