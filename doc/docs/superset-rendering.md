---
id: superset-rendering
title: Superset chart
---

## Waii chat response -> Superset chart iframe

the method render_chart takes chat_response as input 


```
{
 "response": ...,
 "response_data": {
        "data": ...,
        "query": ...,
        "chart": ...
        }
    }
}
```

and returns permalink which can be embedded as iframe

E.g, http://51.8.188.37:8088/superset/explore/p/aqYmx10WDKd/?standalone=True


```
from supersetapiclient.client import SupersetClient
import os
import uuid
import json
import re

# Allow insecure transport for development
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

class SupersetChartRenderer:
    """
    Singleton class for rendering charts in Superset by managing datasets and permalinks.
    Handles dataset creation, chart specifications, and permalink generation.
    
    Environment Variables Required:
        SUPERSET_USERNAME: Superset login username
        SUPERSET_PASSWORD: Superset login password
        SUPERSET_HOST: Superset host URL
        SUPERSET_DATABASE_ID: Target database ID in Superset
        SUPERSET_HOST_HTTPS: Optional HTTPS host URL for permalink generation
    """
    _instance = None

    def __new__(cls):
        """
        Creates or returns the singleton instance of SupersetChartRenderer.
        Initializes SupersetClient with credentials from environment variables.
        """
        if cls._instance is None:
            cls._instance = super(SupersetChartRenderer, cls).__new__(cls)
            cls._instance.client = SupersetClient(username=os.getenv("SUPERSET_USERNAME"),
                                                  password=os.getenv("SUPERSET_PASSWORD"),
                                                  host=os.getenv("SUPERSET_HOST"))
            cls._instance.superset_database_id = os.getenv("SUPERSET_DATABASE_ID")
            cls._instance.link_map = {}
            cls._instance.query_id_to_dataset_id = {}
            cls._instance.current_dataset_id = None
        return cls._instance

    def create_dataset(self, database_id, sql_query):
        """
        Creates a new dataset in Superset from SQL query.
        
        Args:
            database_id (str): ID of target Superset database
            sql_query (str): SQL query to create dataset
            
        Returns:
            str: ID of created dataset
        """
        dataset_name = f"waii-dataset-{str(uuid.uuid4())}"
        dataset = self.client.post(f"{self.client.host}/api/v1/dataset/", json={
            "database": database_id,
            "sql": sql_query,
            "table_name": dataset_name,
            "normalize_columns": True
        })

        return dataset.json()["id"]

    def create_permalink(self, dataset_id, superset_specs):
        """
        Creates a permalink for chart visualization in Superset.
        
        Args:
            dataset_id (str): ID of dataset to visualize
            superset_specs (dict): Chart specifications for Superset
            
        Returns:
            str: Permalink URL for chart visualization
        """
        superset_specs["datasource"] = f"{dataset_id}__table"
        permlink_payload = {
            "formData": superset_specs
        }

        permlink = self.client.post(f"{self.client.host}/api/v1/explore/permalink", json=permlink_payload)

        if os.environ['SUPERSET_HOST_HTTPS']:
            return f"{os.environ['SUPERSET_HOST_HTTPS']}/superset/explore/p/{permlink.json()['key']}/?standalone=True"
        else:
            return f"{os.environ['SUPERSET_HOST']}/superset/explore/p/{permlink.json()['key']}/?standalone=True"

    def render_chart(self, chat_response):
        """
        Renders a chart based on chat response data.
        Creates dataset if query exists and generates visualization permalink.
        
        Args:
            chat_response: Object containing query and chart specifications
            
        Returns:
            str: Permalink URL for rendered chart
            
        Raises:
            Exception: If no query exists and no current dataset ID is set
        """
        if not chat_response.response_data.query and not self.current_dataset_id:
            raise Exception("Cannot plot")

        if chat_response.response_data.query:
            dataset_id = self.create_dataset(self.superset_database_id, chat_response.response_data.query.query)
            self.current_dataset_id = dataset_id
        link = self.create_permalink(self.current_dataset_id, chat_response.response_data.chart.chart_spec.superset_specs)

        return link
```
