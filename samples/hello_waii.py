from waii_sdk_py.query import Query, QueryGenerationRequest, RunQueryRequest
from waii_sdk_py.semantic_context import SemanticContext, ModifySemanticContextRequest, SemanticStatement
from waii_sdk_py.history import History, GetGeneratedQueryHistoryRequest
from waii_sdk_py.database import Database, ModifyDBConnectionRequest, DBConnection

# Initialize a new database object
db = Database()
# WAII.initialize(connection, '')

# Define the connection data to be updated
connection_data = DBConnection(
    key='',  # will be generated by the system
    db_type='snowflake',
    account_name='<your account name>',
    username='<your username>',
    password='<your password>',
    database='<your database>',
    warehouse='<your warehouse>',
    role='<your role>'
    
)

# Create a request object
modify_request = ModifyDBConnectionRequest(
    updated=[connection_data]
)

# Modify the connection using the Database class
response = db.modify_connections(modify_request)

# Activating the database connection
if response.connectors:
    db.activate_connection(response.connectors[2].key)

query = Query()
# Generating a query
gen_query = query.generate(QueryGenerationRequest(
    ask= 'show me all the tables in this database')).query

print('-----Generated Query-----')
print(gen_query)

# Running the query
if gen_query:
    result = query.run(RunQueryRequest(query = gen_query)).rows
    j = 0
    print('-----Result of Query-----')
    while j < len(result):
        print(result[j]['table_name'])
        j = j + 1


# Getting the semantic context
semantic_context = SemanticContext.get_semantic_context().semantic_context
i = 0
print('-----Semantic Context-----')
#while loop prints only the semantic statement
while i < len(semantic_context):
    print(semantic_context[i].statement)
    i = i + 1



# Getting query history
history = History()
query_history = history.list().history
query_history_questions = []
x = 0
while x < len(query_history):
    query_history_questions.append(query_history[x].request)
    query_history_questions[x] = getattr(query_history_questions[x], 'ask')
    x = x + 1
print('-----Query History-----')

print(query_history_questions )