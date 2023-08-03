from Database import Database, GetSchemaRequest
from Query import Query, QueryGenerationRequest, RunQueryRequest
from SemanticContext import SemanticContext, ModifySemanticContextRequest, SemanticStatement
from History import History, GetGeneratedQueryHistoryRequest

# Initialize a new database object
db = Database()

# Make a GetSchemaRequest to the database
get_schema_request = GetSchemaRequest(database='my_database')
schema = db.get_schema(get_schema_request)
print(f'Schema: {schema}')

# Modify the semantic context
semantic_context = SemanticContext()
modify_request = ModifySemanticContextRequest(
    updated=[SemanticStatement(scope='global', statement='California is a state')],
    deleted=None
)
response = semantic_context.modify_semantic_context(modify_request)
print(f'Modified context: {response}')

# Generate a new query
query_obj = Query()
generate_request = QueryGenerationRequest(ask="What's the population of California?")
generated_query = query_obj.generate(generate_request)
print(f'Generated Query: {generated_query}')

# Run the generated query
run_request = RunQueryRequest(query=generated_query.query)
query_result = query_obj.run(run_request)
print(f'Query Result: {query_result}')

# Retrieve query history
history_obj = History()
history_request = GetGeneratedQueryHistoryRequest()
query_history = history_obj.list(history_request)
print(f'Query History: {query_history}')
