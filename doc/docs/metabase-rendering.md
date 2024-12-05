---
id: metabase-rendering
title: Metabase chart
---

## Waii chat response -> Metabase chart iframe

getMetabasePlot takes chart specs as input and returns c Metabase chart URL that can be embedded as an iframe.

```
import json
import csv
import io
import os
import requests
import streamlit as st
import jwt
import time


class MetabaseChartRenderer:
    """
    Singleton class for rendering charts in Metabase by managing datasets and generating public/embedded links.
    Handles dataset creation, chart specifications, and link generation for visualizations.
    
    Environment Variables Required:
        METABASE_URL: Metabase host URL
        METABASE_API_KEY: API key for Metabase authentication
        METABASE_SECRET_KEY: Optional secret key for embedded visualizations
    """
    _instance = None

    def __new__(cls):
        """
        Creates or returns singleton instance of MetabaseChartRenderer.
        Initializes with environment variables.
        
        Raises:
            Exception: If required environment variables are not set
        """
        if cls._instance is None:
            cls._instance = super(MetabaseChartRenderer, cls).__new__(cls)
            if not os.getenv("METABASE_URL") or not os.getenv("METABASE_API_KEY"):
                raise Exception("METABASE_URL or METABASE_API_KEY env variables not set. Cannot plot metabase charts")
            cls._instance.url = os.getenv("METABASE_URL")
            cls._instance.api_key = os.getenv("METABASE_API_KEY")
            cls._instance.link_map = {}
            cls._instance.embedding_secret_key = os.getenv("METABASE_SECRET_KEY")
        return cls._instance

    def convert_to_csv(self, dataframe_rows):
        """
        Converts dataframe rows to CSV format.
        
        Args:
            dataframe_rows (list): List of dictionaries representing dataframe rows
            
        Returns:
            str: CSV formatted data
        """
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=dataframe_rows[0].keys())
        writer.writeheader()
        writer.writerows(dataframe_rows)
        csv_data = output.getvalue()
        output.close()
        return csv_data

    def upload_csv(self, csv_data):
        """
        Uploads CSV data to Metabase to create a new dataset.
        
        Args:
            csv_data (str): CSV formatted data
            
        Returns:
            str: Model ID of created dataset
        """
        url = f'{self.url}/api/card/from-csv'
        headers = {'x-api-key': self.api_key}
        files = {'file': ('waiichart.csv', csv_data, 'text/csv')}
        data = {'collection_id': 'root'}
        response = requests.post(url, headers=headers, files=files, data=data)
        return response.text

    def get_database_id(self, connection_string, table_names):
        """
        Identifies appropriate database ID based on connection string and table names.
        Supports Athena, MySQL, and Snowflake databases.
        
        Args:
            connection_string (str): Database connection string
            table_names (list): List of table names with schema information
            
        Returns:
            tuple: (database_id, database_engine) or (None, None) if no match found
        """
        headers = {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json'
        }
        url = f'{self.url}/api/database'

        response = requests.get(url, headers=headers)
        data = response.json()

        for db in data['data']:
            if db['engine'] == 'athena':
                access_key = db['details']['access_key']
                s3_staging_dir = db['details']['s3_staging_dir']
                region = db['details']['region']

                if access_key in connection_string and s3_staging_dir in connection_string and region in connection_string:
                    return db['id'], db['engine']

            elif db['engine'] == 'mysql':
                dbname = db['details']['dbname']
                host = db['details']['host']
                user = db['details']['user']

                db_names_for_query = [table.schema_name for table in table_names if table.schema_name is not None]

                if len(db_names_for_query) == 0 or len(db_names_for_query) > 1 or db_names_for_query[0] != dbname:
                    continue

                if user in connection_string and host in connection_string:
                    return db['id'], db['engine']

            elif db['engine'] == 'snowflake':
                db_name = db['details']['db']
                account = db['details']['account']
                user = db['details']['user']
                role = db['details']['role']
                warehouse = db['details']['warehouse']

                if db_name in connection_string and user in connection_string and account in connection_string and role in connection_string and warehouse in connection_string:
                    return db['id'], db['engine']

        return None, None

    def save_question(self, chart_info, query, df):
        """
        Creates a new visualization in Metabase.
        
        Args:
            chart_info (dict): Chart specifications including plot type, columns, and styling
            query (Query): Query object containing SQL and table information
            df (DataFrame): Data to be visualized
            
        Returns:
            str: Card ID of created visualization
        """
        url = f'{self.url}/api/card'
        database_id, db_type = self.get_database_id(st.session_state['db_activated_connection'], query.tables)
        if not database_id:
            model_id = self.upload_csv(self.convert_to_csv(df.to_dict(orient='records')))
            self.update_card(model_id, chart_info)
            return model_id

        data = {
            "display": chart_info["plot_type"],
            "dataset_query": {
                "database": database_id,
                "type": "native",
                "native": {
                    "template-tags": {},
                    "query": query.query
                }
            },
            "visualization_settings": {
                "graph.dimensions": [chart_info["dimension_column"].lower() if db_type == 'mysql' else chart_info["dimension_column"]],
                "graph.metrics": [chart_info["metric_column"].lower() if db_type == 'mysql' else chart_info["metric_column"]],
                "series_settings": {
                    chart_info["metric_column"].lower() if db_type == 'mysql' else chart_info["metric_column"]: {
                        "color": chart_info["chart_color_hex"]
                    }
                }
            },
            "name": chart_info["chart_name"],
            "enable_embedding": True,
            "type": "question"
        }

        headers = {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json'
        }

        if chart_info["plot_type"] == "pie":
            data["visualization_settings"] = {
                "pie.dimension": chart_info["dimension_column"].lower() if db_type == 'mysql' else chart_info["dimension_column"],
                "pie.metric": chart_info["metric_column"].lower() if db_type == 'mysql' else chart_info["dimension_column"]
            }

        response = requests.post(url, headers=headers, data=json.dumps(data))
        return response.json()["id"]

    def update_card(self, card_id, chart_info):
        """
        Updates visualization settings for an existing Metabase card.
        
        Args:
            card_id (str): ID of the card to update
            chart_info (dict): New chart specifications
        """
        url = f'{self.url}/api/card/{card_id}'
        data = {
            "display": chart_info["plot_type"],
            "visualization_settings": {
                "graph.dimensions": [chart_info["dimension_column"].lower()],
                "graph.metrics": [chart_info["metric_column"].lower()],
                "series_settings": {
                    chart_info["metric_column"].lower(): {
                        "color": chart_info["chart_color_hex"]
                    }
                }
            },
            "name": chart_info["chart_name"],
            "enable_embedding": True,
            "type": "question"
        }
        if chart_info["plot_type"] == "pie":
            data["visualization_settings"] = {
                "pie.dimension": chart_info["dimension_column"].lower(),
                "pie.metric": chart_info["metric_column"].lower()
            }
        headers = {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json'
        }
        response = requests.put(url, headers=headers, data=json.dumps(data))
        return response

    def enable_embedding(self, card_id):
        """
        Enables embedding for a specific Metabase card.
        
        Args:
            card_id (str): ID of the card to enable embedding for
        """
        full_url = f"{self.url}/api/card/{card_id}"
        headers = {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json'
        }
        payload = {"enable_embedding": True}
        requests.put(full_url, headers=headers, json=payload)

    def get_embedding_link(self, card_id):
        """
        Generates an embedded visualization link with JWT token.
        
        Args:
            card_id (str): ID of the card to generate link for
            
        Returns:
            str: Embedded visualization URL
        """
        payload = {
            "resource": {"question": int(card_id)},
            "params": {},
            "exp": round(time.time()) + (60 * 10)
        }
        self.enable_embedding(card_id)
        token = jwt.encode(payload, self.embedding_secret_key, algorithm="HS256")
        return self.url + "/embed/question/" + token + "#bordered=true&titled=true"

    def get_public_link(self, card_id):
        """
        Generates a public link for a Metabase visualization.
        
        Args:
            card_id (str): ID of the card to generate link for
            
        Returns:
            str: Public visualization URL
        """
        url = f'{self.url}/api/card/{card_id}/public_link'
        headers = {'x-api-key': self.api_key}
        response = requests.post(url, headers=headers)
        uuid = response.json()['uuid']
        return f'{self.url}/public/question/{uuid}'

    def get_metabase_plot(self, chart_info, df, query):
        """
        Main method to generate a Metabase visualization with caching.
        
        Args:
            chart_info (dict): Chart specifications
            df (DataFrame): Data to visualize
            query (Query): Query object with SQL and metadata
            
        Returns:
            str: URL for the generated visualization
        
        Note:
            Results are cached using query UUID and chart info as key
        """
        if (query.uuid,str(chart_info)) in self.link_map:
            return self.link_map[(query.uuid,str(chart_info))]

        card_id = self.save_question(chart_info, query, df)

        if self.embedding_secret_key:
            link = self.get_embedding_link(card_id)
        else:
            link = self.get_public_link(card_id)

        self.link_map[(query.uuid,str(chart_info))] = link

        return self.link_map[(query.uuid,str(chart_info))]
```