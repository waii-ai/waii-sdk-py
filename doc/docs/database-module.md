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
Examples of creating push based `DBConnection` Object. It is same for `Snowflake` ,`postgresql` and `mongodb`
```python
DBConnection(
    key = '',
    db_type = 'snowflake'/'postgresql'/'mongodb', # depending on the db_type
    database = 'database',
    host = 'test_host', # it needs to be unique identifier
    push = True # required for push based database
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
