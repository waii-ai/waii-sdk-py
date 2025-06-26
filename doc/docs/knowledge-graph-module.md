---
id: knowledge-graph-module
title: Knowledge Graph
---

**Initialization & Imports**
```python
from waii_sdk_py import WAII
from waii_sdk_py.kg import *

WAII.initialize(url="https://your-waii-instance/api/", api_key="your-api-key")
```

The `Knowledge Graph` module provides methods to generate and visualize knowledge graphs representing relationships between database objects and semantic statements.

**Important:** You need to activate the database connection first before using the methods in this module.
```python
WAII.Database.activate_connection("snowflake://...&warehouse=COMPUTE_WH")
```

## Overview

The Knowledge Graph module helps you understand:
- Relationships between tables through foreign keys and constraints
- Table-to-column mappings
- Schema-to-table hierarchies
- Semantic statements associated with database objects

## Methods

### Get Knowledge Graph

```python
WAII.knowledge_graph.get_knowledge_graph(params: GetKnowledgeGraphRequest) -> GetKnowledgeGraphResponse
```

This method generates a knowledge graph based on the provided query.

**Parameters:**
- `ask`: The question or query to generate a knowledge graph for (e.g., "Show me relationships between customer and order tables")

**Response:**
The `GetKnowledgeGraphResponse` contains:
- `graph`: A `KnowledgeGraph` object containing:
  - `nodes`: List of `KnowledgeGraphNode` objects
  - `edges`: List of `KnowledgeGraphEdge` objects

## Data Models

### KnowledgeGraphNode

Represents a node in the knowledge graph:
- `id`: Unique identifier for the node
- `display_name`: Human-readable name for display
- `entity_type`: Type of the entity (table, column, schema, or semantic_statement)
- `entity`: The actual entity object (TableDefinition, ColumnDefinition, SchemaDefinition, or SemanticStatement)
- `parent_entity`: Optional parent entity (for hierarchical relationships)

### KnowledgeGraphEdge

Represents an edge (relationship) in the knowledge graph:
- `edge_type`: Type of relationship (constraint, semantic_statement_reference, table_to_column, schema_to_table)
- `source_id`: ID of the source node
- `target_id`: ID of the target node
- `directed`: Whether the edge is directed (true) or undirected (false)
- `description`: Optional description of the relationship
- `edge_entity`: Optional entity associated with the edge (SemanticStatement or Constraint)

## Node Types

The module supports four types of nodes:

```python
class KnowlegeGraphNodeType(str, Enum):
    table = "table"
    column = "column"
    schema = "schema"
    semantic_statement = "semantic_statement"
```

## Edge Types

The module supports four types of edges:

```python
class KnowledgeGraphEdgeType(str, Enum):
    constraint = "constraint"  # Join between two tables
    semantic_statement_reference = "semantic_statement_reference"  # Reference to semantic context
    table_to_column = "table_to_column"  # Table to column relationship
    schema_to_table = "schema_to_table"  # Schema to table hierarchy
```

## Examples

### Basic Usage

Generate a knowledge graph for understanding table relationships:

```python
>>> from waii_sdk_py.kg import GetKnowledgeGraphRequest
>>> 
>>> request = GetKnowledgeGraphRequest(ask="Show me how customer data relates to orders")
>>> response = WAII.knowledge_graph.get_knowledge_graph(request)
>>> 
>>> # Access the graph
>>> graph = response.graph
>>> print(f"Found {len(graph.nodes)} nodes and {len(graph.edges)} edges")
```

### Analyzing Node Types

```python
>>> # Count nodes by type
>>> node_types = {}
>>> for node in graph.nodes:
...     node_type = node.entity_type
...     node_types[node_type] = node_types.get(node_type, 0) + 1
>>> 
>>> print("Node types found:")
>>> for node_type, count in node_types.items():
...     print(f"  {node_type}: {count}")
```

### Working with Specific Node Types

```python
>>> from waii_sdk_py.kg import KnowlegeGraphNodeType
>>> 
>>> # Find all table nodes
>>> table_nodes = [
...     node for node in graph.nodes 
...     if node.entity_type == KnowlegeGraphNodeType.table
... ]
>>> 
>>> # Print table names
>>> for node in table_nodes:
...     table = node.entity  # This is a TableDefinition
...     print(f"Table: {table.name.table_name}")
...     if table.description:
...         print(f"  Description: {table.description}")
```

### Exploring Relationships

```python
>>> from waii_sdk_py.kg import KnowledgeGraphEdgeType
>>> 
>>> # Find all foreign key constraints
>>> constraints = [
...     edge for edge in graph.edges 
...     if edge.edge_type == KnowledgeGraphEdgeType.constraint
... ]
>>> 
>>> # Print constraint relationships
>>> for edge in constraints:
...     source_node = next(n for n in graph.nodes if n.id == edge.source_id)
...     target_node = next(n for n in graph.nodes if n.id == edge.target_id)
...     print(f"{source_node.display_name} -> {target_node.display_name}")
...     if edge.description:
...         print(f"  Relationship: {edge.description}")
```

### Finding Semantic Statements

```python
>>> # Find nodes with semantic statements
>>> semantic_nodes = [
...     node for node in graph.nodes 
...     if node.entity_type == KnowlegeGraphNodeType.semantic_statement
... ]
>>> 
>>> # Print semantic statements
>>> for node in semantic_nodes:
...     statement = node.entity  # This is a SemanticStatement
...     print(f"Statement: {statement.statement}")
...     if statement.labels:
...         print(f"  Labels: {', '.join(statement.labels)}")
```

### Visualizing Table Hierarchies

```python
>>> # Find schema-to-table relationships
>>> schema_edges = [
...     edge for edge in graph.edges 
...     if edge.edge_type == KnowledgeGraphEdgeType.schema_to_table
... ]
>>> 
>>> # Build hierarchy
>>> for edge in schema_edges:
...     schema_node = next(n for n in graph.nodes if n.id == edge.source_id)
...     table_node = next(n for n in graph.nodes if n.id == edge.target_id)
...     print(f"Schema: {schema_node.display_name}")
...     print(f"  └─ Table: {table_node.display_name}")
```

### Complex Query Example

```python
>>> # Generate a comprehensive knowledge graph
>>> request = GetKnowledgeGraphRequest(
...     ask="Show me all relationships and constraints for the sales database including customer, order, and product tables"
... )
>>> response = WAII.knowledge_graph.get_knowledge_graph(request)
>>> 
>>> # Analyze the results
>>> graph = response.graph
>>> 
>>> # Group edges by type
>>> edges_by_type = {}
>>> for edge in graph.edges:
...     edge_type = edge.edge_type
...     edges_by_type[edge_type] = edges_by_type.get(edge_type, [])
...     edges_by_type[edge_type].append(edge)
>>> 
>>> # Print summary
>>> print("Knowledge Graph Summary:")
>>> print(f"Total nodes: {len(graph.nodes)}")
>>> print(f"Total edges: {len(graph.edges)}")
>>> print("\nEdges by type:")
>>> for edge_type, edges in edges_by_type.items():
...     print(f"  {edge_type}: {len(edges)}")
```

## Use Cases

1. **Database Documentation**: Generate visual representations of database schemas
2. **Impact Analysis**: Understand which tables and columns are affected by changes
3. **Query Optimization**: Identify join paths and relationships
4. **Data Lineage**: Track data flow through constraints and relationships
5. **Semantic Context**: Understand business rules associated with database objects

## Integration with Other Modules

The Knowledge Graph module works well with:
- **Database module**: For exploring catalog information
- **Semantic Context module**: For understanding business rules
- **Query module**: For generating queries based on relationships

```python
>>> # Example: Use knowledge graph to inform query generation
>>> kg_request = GetKnowledgeGraphRequest(ask="customer order relationships")
>>> kg_response = WAII.knowledge_graph.get_knowledge_graph(kg_request)
>>> 
>>> # Use the relationships found to generate a query
>>> from waii_sdk_py.query import QueryGenerationRequest
>>> query_request = QueryGenerationRequest(
...     ask="Show me customers with their recent orders"
... )
>>> query_response = WAII.query.generate(query_request)
```

## Best Practices

1. **Be Specific**: Provide specific table or schema names in your `ask` parameter for more focused results
2. **Check Entity Types**: Always verify the `entity_type` before accessing entity properties
3. **Handle Large Graphs**: For large databases, focus your queries on specific schemas or table groups
4. **Cache Results**: Knowledge graphs can be cached as they represent structural relationships that don't change frequently
5. **Combine with Filters**: Use in conjunction with database filters for more targeted results 