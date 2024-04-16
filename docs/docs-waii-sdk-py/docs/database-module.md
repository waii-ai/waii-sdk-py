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
