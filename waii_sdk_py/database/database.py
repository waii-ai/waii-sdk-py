from dataclasses import dataclass
from waii_sdk_py.waii_http_client import WaiiHttpClient
from pydantic import BaseModel
import re
from typing import Optional, List, Dict, Any, Union
from urllib.parse import urlparse, parse_qs


MODIFY_DB_ENDPOINT = 'update-db-connect-info'
GET_CATALOG_ENDPOINT = 'get-table-definitions'

def no_quote_needed(identifier):
    # The regex will start the match from the start (^) of the string
    # and continue until the end ($), making sure the whole string matches the pattern.
    # The first character group ([A-Z_]) makes sure the string starts with an uppercase
    # English letter or an underscore. The second character group ([A-Z_0-9$]*) makes sure
    # the rest of the string (if it exists) contains only uppercase English letters,
    # underscores, decimal digits, and dollar signs.
    return bool(re.match(r'^[A-Z_][A-Z_0-9$]*$', identifier))


# for a given part, return if it needs quote, the part means either database_name, schema_name, or table_name
def get_quoted_part_if_needed(part: str, lower_case_if_no_quote=False) -> str:
    if not no_quote_needed(part):
        return f'"{part}"'

    if lower_case_if_no_quote:
        return part.lower()

    return part


def quoted_str_to_parts(quoted_str: str) -> List[str]:
    parts = []
    part = ""
    quoted = False
    escaped = False

    for char in quoted_str:
        if char == '"' and not escaped:
            quoted = not quoted
            if quoted:
                escaped = False
        elif char == '"' and quoted:
            part += char
            escaped = True
        elif char == '.' and not quoted:
            parts.append(part.strip())
            part = ""
        else:
            part += char
            escaped = False

    if quoted:
        raise ValueError(f'Quotes not closed in name: {quoted_str}')

    parts.append(part.strip())
    return parts


class SchemaName(BaseModel):
    schema_name: str
    database_name: Optional[str]

    def __hash__(self):
        return hash((self.schema_name, self.database_name))

    def __eq__(self, other):
        return (self.schema_name, self.database_name) == (
            other.schema_name, other.database_name)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        # for each database_name, schema_name, and table_name, check no_quote_needed, if yes, then connect them with dot, otherwise, quote each them need quote, and connect them with dot
        # if database_name is None, then skip it
        # if schema_name is None, then skip it
        return '.'.join(
            [get_quoted_part_if_needed(name) for name in
             [self.database_name, self.schema_name] if
             name is not None])

    @staticmethod
    def from_quoted_str(quoted_str: str):
        parts = quoted_str_to_parts(quoted_str)

        if len(parts) > 2 or not all(parts):
            raise ValueError(f'Invalid schema name: {quoted_str}')

        parts = [None] * (2 - len(parts)) + parts  # add None for missing parts
        db_name, schema_name = parts
        ret = SchemaName(schema_name=schema_name)
        if db_name:
            ret.database_name = db_name
        return ret


class TableName(BaseModel):
    table_name: str
    schema_name: Optional[str]
    database_name: Optional[str]

    def __hash__(self):
        return hash((self.table_name, self.schema_name, self.database_name))

    def __eq__(self, other):
        return (self.table_name, self.schema_name, self.database_name) == (
            other.table_name, other.schema_name, other.database_name)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        # for each database_name, schema_name, and table_name, check no_quote_needed, if yes, then connect them with dot, otherwise, quote each them need quote, and connect them with dot
        # if database_name is None, then skip it
        # if schema_name is None, then skip it
        return '.'.join(
            [get_quoted_part_if_needed(name) for name in
             [self.database_name, self.schema_name, self.table_name] if
             name is not None])

    def extract_schema_name(self) -> SchemaName:
        return SchemaName(schema_name=self.schema_name, database_name=self.database_name)

    def startwith_schema(self, prefix: SchemaName):
        return self.database_name == prefix.database_name and \
            self.schema_name == prefix.schema_name

    def compare_ignore_case(self, other) -> bool:
        if self.database_name is None and other.database_name is not None:
            return False
        if self.database_name is not None and other.database_name is None:
            return False
        if self.database_name is not None and other.database_name is not None:
            if self.database_name.lower() != other.database_name.lower():
                return False
        if self.schema_name is None and other.schema_name is not None:
            return False
        if self.schema_name is not None and other.schema_name is None:
            return False
        if self.schema_name is not None and other.schema_name is not None:
            if self.schema_name.lower() != other.schema_name.lower():
                return False
        return self.table_name.lower() == other.table_name.lower()

    @staticmethod
    def from_quoted_str(quoted_str: str):
        parts = quoted_str_to_parts(quoted_str)

        if len(parts) > 3 or not all(parts):
            raise ValueError(f'Invalid table name: {quoted_str}')

        parts = [None] * (3 - len(parts)) + parts  # add None for missing parts

        db_name, schema_name, table_name = parts
        ret = TableName(table_name=table_name)
        if schema_name:
            ret.schema_name = schema_name
        if db_name:
            ret.database_name = db_name

        return ret


class ColumnSampleValues(BaseModel):
    # value -> count
    values: Optional[Dict[str, int]]


class ColumnDefinition(BaseModel):
    name: str
    type: str
    comment: Optional[str]
    sample_values: Optional[ColumnSampleValues]

    def __lt__(self, other):
        return self.name < other.name


class TableReference(BaseModel):
    src_table: Optional[TableName]  # table name
    src_cols: Optional[List[str]]  # source table columns
    ref_table: Optional[TableName]  # ref table name
    ref_cols: Optional[List[str]]  # ref table columns


class TableNameToDescription(BaseModel):
    name: str
    description: str


class SchemaDescription(BaseModel):
    summary: Optional[str]
    common_questions: Optional[List[str]]
    common_tables: Optional[List[TableNameToDescription]]


class TableDefinition(BaseModel):
    name: TableName
    columns: Optional[List[ColumnDefinition]]
    comment: Optional[str]
    last_altered_time: Optional[int]
    refs: Optional[List[TableReference]]
    description: Optional[str]


class SchemaDefinition(BaseModel):
    name: SchemaName
    tables: Optional[List[TableDefinition]]
    description: Optional[SchemaDescription]


class CatalogDefinition(BaseModel):
    name: str
    schemas: Optional[List[SchemaDefinition]]

class DBConnection(BaseModel):
    key: str
    # Snowflake, ...
    db_type: str
    description: Optional[str]
    account_name: Optional[str]
    username: Optional[str]
    password: Optional[str]
    database: Optional[str]
    warehouse: Optional[str]
    role: Optional[str]
    path: Optional[str]
    parameters: Optional[Dict[str, Any]]

    # scope is the key uniquely identifying the connection
    def get_scope_key_url(self):
        if self.db_type == 'snowflake':
            return f"snowflake://{self.username}@{self.account_name}/{self.database}?role={self.role}&warehouse={self.warehouse}"

    @classmethod
    def from_scope_url(cls, scope_key_url: str):
        # parse url, and construct DBConnection
        parsed = urlparse(scope_key_url)

        if parsed.scheme != 'snowflake':
            raise ValueError(f'Unsupported scheme {parsed.scheme}')

        # Get username and account_name
        username, account_name = parsed.netloc.split('@')

        # Get database
        database = parsed.path.lstrip('/')

        print('parsed URL=' + str(parsed))

        # Get role and warehouse
        params = parse_qs(parsed.query)
        role = params.get('role')[0]
        warehouse = params.get('warehouse')[0]

        # Construct and return the DBConnection instance
        return cls(
            key=account_name,  # Update this as per your logic
            db_type=parsed.scheme,
            username=username,
            account_name=account_name,
            database=database,
            role=role,
            warehouse=warehouse
        )

    def get_org_id(self):
        # for snowflake, org_id consists of db_type and account_name
        if self.db_type == 'snowflake':
            return f"{self.db_type}_{self.account_name}"

    def get_scope_name(self):
        # for snowflake, scope_name consists of database and role
        if self.db_type == 'snowflake':
            return f"{self.database}_{self.role}"

    def __eq__(self, other):
        return self.key == other.key and \
            self.db_type == other.db_type and \
            self.description == other.description and \
            self.account_name == other.account_name and \
            self.username == other.username and \
            self.password == other.password and \
            self.database == other.database and \
            self.warehouse == other.warehouse and \
            self.role == other.role and \
            self.path == other.path


class ModifyDBConnectionRequest(BaseModel):
    updated: Optional[List[DBConnection]]
    removed: Optional[List[str]]
    validate_before_save: Optional[bool] = None
    user_id: Optional[str] = None
    default_db_connection_key: Optional[str] = None


class ModifyDBConnectionResponse(BaseModel):
    connectors: Optional[List[DBConnection]]
    diagnostics: Optional[str]
    default_db_connection_key: Optional[str] 


class SearchContext(BaseModel):
    db_name: Optional[str] = '*'
    schema_name: Optional[str] = '*' 
    table_name: Optional[str] = '*'

class GetCatalogRequest(BaseModel):
    pass

class GetDBConnectionRequest(BaseModel):
    pass

class GetDBConnectionResponse(BaseModel):
    connectors: Optional[List[DBConnection]]
    diagnostics: Optional[str]
    default_db_connection_key: Optional[str] 


class GetCatalogResponse(BaseModel):
    catalogs: Optional[List[CatalogDefinition]] = None

class Database:
    @staticmethod
    def modify_connections(params: ModifyDBConnectionRequest) -> ModifyDBConnectionResponse:
        return WaiiHttpClient.get_instance().common_fetch(MODIFY_DB_ENDPOINT, params.__dict__, ModifyDBConnectionResponse)

    @staticmethod
    def get_connections(params: GetDBConnectionRequest = GetDBConnectionRequest()) -> GetDBConnectionResponse:
        return WaiiHttpClient.get_instance().common_fetch(MODIFY_DB_ENDPOINT, params.__dict__, GetDBConnectionResponse)

    @staticmethod
    def activate_connection(key: str):
        WaiiHttpClient.get_instance().set_scope(key)

    @staticmethod
    def get_catalogs(params: GetCatalogRequest = GetCatalogRequest()) -> GetCatalogResponse:
        return WaiiHttpClient.get_instance().common_fetch(GET_CATALOG_ENDPOINT, params.__dict__, GetCatalogResponse)
