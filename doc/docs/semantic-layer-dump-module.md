---
id: semantic-layer-dump-module
title: Semantic Layer Import & Export Configuration
---

The `SemanticLayerDump` module provides methods for exporting and importing Waii semantic layer configurations between environments.

**Initialization & Imports**
```python
from waii_sdk_py import WAII
from waii_sdk_py.semantic_layer_dump import *
from waii_sdk_py.database import SearchContext

WAII.initialize(url="https://your-waii-instance/api/", api_key="your-api-key")
```

**Operation Status Enum**
```python
class OperationStatus(str, Enum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    IN_PROGRESS = "in_progress"
    NOT_EXISTS = "not_exists"
```

Here are its methods:

### Export Semantic Layer Dump

```python
SemanticLayerDump.export_dump(params: ExportSemanticLayerDumpRequest) -> ExportSemanticLayerDumpResponse
```

Exports the semantic layer configuration from a specified database connection.

Parameters of `ExportSemanticLayerDumpRequest`:
- `db_conn_key`: (str) **Required**. The database connection key to export from.
- `search_context`: (List[SearchContext]) Optional. List of search contexts to filter what gets exported. Default is a single empty SearchContext.

Example:
```python
response = WAII.SemanticLayerDump.export_dump(ExportSemanticLayerDumpRequest(
    db_conn_key="my_snowflake_connection"
))

# The operation ID can be used to check export status
op_id = response.op_id
```

### Import Semantic Layer Dump

```python
SemanticLayerDump.import_dump(params: ImportSemanticLayerDumpRequest) -> ImportSemanticLayerDumpResponse
```

Imports a semantic layer configuration into a specified database connection.

Parameters of `ImportSemanticLayerDumpRequest`:
- `db_conn_key`: (str) **Required**. The database connection key to import into.
- `configuration`: (Dict[str, Any]) **Required**. The semantic layer configuration to import.
- `search_context`: (List[SearchContext]) Optional. List of search contexts. Default is a single empty SearchContext.

Example:
```python
import yaml

# Load configuration from a YAML file
with open("semantic_layer_export.yaml", "r") as file:
    config = yaml.safe_load(file)

response = WAII.SemanticLayerDump.import_dump(ImportSemanticLayerDumpRequest(
    db_conn_key="target_connection",
    configuration=config
))

# The operation ID can be used to check import status
op_id = response.op_id
```

### Check Export Status

```python
SemanticLayerDump.export_dump_status(params: CheckOperationStatusRequest) -> CheckOperationStatusResponse
```

Checks the status of an export operation.

Parameters of `CheckOperationStatusRequest`:
- `op_id`: (str) **Required**. The operation ID returned by the export_dump method.

The `CheckOperationStatusResponse` contains:
- `op_id`: (str) The operation ID.
- `status`: (OperationStatus) The status of the operation.
- `info`: When status is `SUCCEEDED`, this field contains the exported configuration as a dictionary. Otherwise, it contains an error message or progress information.

Example:
```python
import yaml

status = WAII.SemanticLayerDump.export_dump_status(CheckOperationStatusRequest(
    op_id=op_id
))

if status.status == OperationStatus.SUCCEEDED:
    print("Export completed successfully")
    
    # Access the exported configuration data
    exported_config = status.info
    
    # The exported_config structure contains:
    # - version: The version of the export format
    # - metadata: Export metadata including source dialect and database
    # - database: Database-level configurations
    # - tables: Table definitions including columns and constraints
    # - schemas: Schema definitions and descriptions
    # - liked_queries: Saved/liked queries
    
    # Example: print the number of exported tables
    print(f"Exported {len(exported_config['tables'])} tables")
    
    # Save the configuration to a YAML file
    with open("semantic_layer_export.yaml", "w") as file:
        yaml.dump(exported_config, file, default_flow_style=False, sort_keys=False)
    print("Saved export configuration to semantic_layer_export.yaml")
    
elif status.status == OperationStatus.FAILED:
    print(f"Export failed: {status.info}")
elif status.status == OperationStatus.IN_PROGRESS:
    print("Export is still in progress")
```

### Check Import Status

```python
SemanticLayerDump.import_dump_status(params: CheckOperationStatusRequest) -> CheckOperationStatusResponse
```

Checks the status of an import operation.

Parameters of `CheckOperationStatusRequest`:
- `op_id`: (str) **Required**. The operation ID returned by the import_dump method.

The `CheckOperationStatusResponse` contains:
- `op_id`: (str) The operation ID.
- `status`: (OperationStatus) The status of the operation.
- `info`: When status is `SUCCEEDED`, this field contains import statistics as a dictionary. Otherwise, it contains an error message or progress information.

Example:
```python
status = WAII.SemanticLayerDump.import_dump_status(CheckOperationStatusRequest(
    op_id=op_id
))

if status.status == OperationStatus.SUCCEEDED:
    print(f"Import completed successfully")
    
    # Access the import statistics
    import_stats = status.info
    
    # The import_stats contains details about what was imported and what was ignored
    if 'stats' in import_stats:
        stats = import_stats['stats']
        print(f"Imported {len(stats['tables']['imported'])} tables")
        print(f"Imported {len(stats['semantic_contexts']['imported'])} semantic contexts")
        print(f"Imported {len(stats['schema_definitions']['imported'])} schemas")
        
        # Tables that were ignored during import
        if len(stats['tables']['ignored']) > 0:
            print(f"Ignored {len(stats['tables']['ignored'])} tables")
            
        # More stats are available for columns, content_filters, liked_queries, etc.
    
elif status.status == OperationStatus.FAILED:
    print(f"Import failed: {status.info}")
elif status.status == OperationStatus.IN_PROGRESS:
    print("Import is still in progress")
```

### Polling for Operation Completion

Polling example for long running operation:

```python
from waii_sdk_py.common import OperationStatus
from waii_sdk_py.semantic_layer_dump import *

import time
import yaml

# Export the semantic layer configuration
response = WAII.SemanticLayerDump.export_dump(ExportSemanticLayerDumpRequest(
    db_conn_key="my_connection"
))
export_op_id = response.op_id

# Poll until the operation completes
timeout_seconds = 300  # 5 minutes
start_time = time.time()
while time.time() - start_time < timeout_seconds:
    status = WAII.SemanticLayerDump.export_dump_status(CheckOperationStatusRequest(
        op_id=export_op_id
    ))
    
    if status.status == OperationStatus.SUCCEEDED:
        print("Export completed successfully")
        exported_config = status.info
        
        # Save the configuration to a YAML file
        output_file = f"semantic_layer_export_{time.strftime('%Y%m%d_%H%M%S')}.yaml"
        with open(output_file, "w") as file:
            yaml.dump(exported_config, file, default_flow_style=False, sort_keys=False)
        print(f"Saved export configuration to {output_file}")
        break
        
    elif status.status == OperationStatus.FAILED:
        print(f"Export failed: {status.info}")
        break
    elif status.status == OperationStatus.NOT_EXISTS:
        print("Operation does not exist")
        break
    elif status.status == OperationStatus.IN_PROGRESS:
        print("Export is still in progress, waiting...")
        time.sleep(2)  # Wait for 2 seconds before checking again
else:
    print(f"Operation timed out after {timeout_seconds} seconds")
```

The same polling pattern can be used for import operations by replacing `export_dump` and `export_dump_status` with `import_dump` and `import_dump_status` respectively.

### Understanding the Semantic Layer Configuration

The exported semantic layer dump provides a comprehensive representation of your Waii semantic layer. Here's a detailed overview of its structure:

```python
{
    "version": "1.0",                 # Format version
    "metadata": {                     # Export metadata
        "exported_at": "2025-03-31T01:17:32.501001",
        "source_dialect": "snowflake",
        "source_database": "sales_analytics"
    },
    "database": {                     # Database-level configurations
        "content_filters": []         # Content filters applied at database level
    },
    "tables": [                       # Table definitions
        {
            "name": "order_transactions",          # Table name
            "schema_name": "sales",               # Schema name
            "description": "This table stores transaction data for all customer orders", # Table description
            "constraints": [                      # Constraints (PK, FK, etc.)
                # table constraints
            ],
            "columns": [                          # Column definitions
                {
                    "name": "order_id",
                    "type": "INT64",
                    "description": "Unique identifier for each customer order",
                    "description_update_source": "generated"
                }
                # More columns...
            ]
        }
        # More tables...
    ],
    "schemas": [                     # Schema definitions
        {
            "name": "sales",
            "description": {
                "summary": "This schema contains all sales-related tables and views for analyzing customer transactions and orders",
                "common_tables": [
                    {
                        "name": "customer_dimension",
                        "description": "This table stores customer profile information including demographics and contact details"
                    }
                    # More tables...
                ]
            }
        }
        # More schemas...
    ],
    "liked_queries": []              # Saved/liked queries
    # Other configuration elements...
}
```

This configuration can be used for:
- Migrating configurations between environments (dev to prod)
- Backing up and restoring semantic layer definitions
- Version controlling your semantic layer configurations
- Sharing configurations across teams

### Import Status Response Structure

When an import operation succeeds, the `info` field of the `CheckOperationStatusResponse` contains detailed statistics about what was imported. Here's the structure:

```python
{
    "message": "Semantic layer dump applied successfully",  # Success message
    "stats": {                                             # Import statistics
        "semantic_contexts": {                             # Semantic context statements
            "imported": [
                "The measure 'Revenue_YTD' in 'Sales_Summary' is calculated as: Sum of transaction amounts for the current year to date",
                "Calculate 'Profit_Margin_Pct' for 'Performance_Dashboard' using the ratio of net profit to revenue"
            ],
            "ignored": []                                  # Statements that weren't imported
        },
        "schema_definitions": {                            # Schema definitions
            "imported": [
                "sales_analytics.marketing",
                "sales_analytics.finance"
            ],
            "ignored": []                                  # Schemas that weren't imported
        },
        "tables": {                                        # Table definitions
            "imported": [
                "sales_analytics.finance.Calendar",
                "sales_analytics.marketing.CustomerSegments"
            ],
            "ignored": [                                   # Tables that weren't imported
                "sales_analytics.marketing.DeprecatedCampaigns",
                "sales_analytics.marketing.TestSegmentation"
            ]
        },
        "columns": {                                       # Column definitions
            "imported": [
                "sales_analytics.marketing.CustomerSegments.CustomerId",
                "sales_analytics.marketing.CustomerSegments.SegmentName",
                "sales_analytics.marketing.CustomerSegments.LoyaltyScore"
            ],
            "ignored": [                                   # Columns that weren't imported
                "sales_analytics.marketing.TestSegmentation.TestColumn1",
                "sales_analytics.marketing.TestSegmentation.TestColumn2"
            ]
        },
        "content_filters": {                               # Content filters
            "imported": [],
            "ignored": []
        },
        "liked_queries": {                                 # Saved/liked queries
            "imported": [],
            "ignored": []
        },
        "similarity_search_indices": {                     # Similarity search indices
            "imported": [],
            "ignored": []
        }
    }
}
```

This structure provides a comprehensive report of what was successfully imported and what was ignored during the import process.
