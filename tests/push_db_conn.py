import requests

base_url = "http://localhost:9859"

# API endpoint URL
modify_db_conn_endpoint = f"{base_url}/api/update-db-connect-info"

update_table_endpoint = f"{base_url}/api/update-table-definitions"
generate_query_endpoint = f"{base_url}/api/generate-query"


def add_db_conn():
    # Data payload
    add_conn_data = {
        "updated": [
            {
                "account_name": "",
                "warehouse": "",
                "database": "push_test",
                "host": "test_host",
                "db_type": "postgresql",
                "push": True,
            }
        ],
        "validate_before_save": True,
    }
    # Adding Connection
    add_conn_response = requests.post(modify_db_conn_endpoint, json=add_conn_data)

    print("Adding db conn response")
    return add_conn_response


def remove_conn():
    # Removing connection
    remove_conn_data = {"removed": ["postgresql://push/test_host/push_test"]}
    print("remove connection")
    remove_conn_response = requests.post(modify_db_conn_endpoint, json=remove_conn_data)
    return remove_conn_response


def add_table():
    # Updating tables
    table_update_data = {
        "updated_tables": [
            {
                "name": {
                    "table_name": "Album",
                    "schema_name": "PUBLIC",
                    "database_name": "push_test",
                },
                "columns": [
                    {
                        "name": "AlbumId",
                        "type": "integer",
                        "comment": None,
                        "sample_values": None,
                        "description": "Unique identifier for the album.",
                        "description_update_source": "generated",
                    },
                    {
                        "name": "Title",
                        "type": "character varying",
                        "comment": None,
                        "sample_values": None,
                        "description": "Title of the album.",
                        "description_update_source": "generated",
                    },
                    {
                        "name": "ArtistId",
                        "type": "integer",
                        "comment": None,
                        "sample_values": None,
                        "description": "Identifier for the artist of the album.",
                        "description_update_source": "generated",
                    },
                ],
                "comment": None,
                "last_altered_time": 0,
                "refs": None,
                "constraints": [
                    {
                        "source": "database",
                        "table": {
                            "table_name": "Artist",
                            "schema_name": "PUBLIC",
                            "database_name": "push_test",
                        },
                        "cols": ["ArtistId"],
                        "constraint_type": None,
                        "src_table": {
                            "table_name": "Album",
                            "schema_name": "PUBLIC",
                            "database_name": "push_test",
                        },
                        "src_cols": ["ArtistId"],
                        "comment": None,
                    }
                ],
                "inferred_refs": [],
                "inferred_constraints": [],
                "description": 'The "Album" table contains information about music albums, including the album ID, artist ID, and title. Users can use this table to track and organize albums by various artists, making it easier to manage and access music collections.',
            }
        ],
        "scope": "postgresql://push/test_host/push_test",
    }
    updating_table_response = requests.post(
        update_table_endpoint, json=table_update_data
    )
    # add table definition response
    print("Updating table def Response")
    return updating_table_response


def gen_query():
    gen_query_data = {
        "ask": "give me 5 albums name",
        "search_context": [],
        "tweak_history": [],
        "parent_uuid": None,
        "model": "Automatic",
        "scope": "postgresql://push/test_host/push_test",
        "org_id": "",
        "user_id": "",
    }

    gen_query_response = requests.post(generate_query_endpoint, json=gen_query_data)

    print("Generating query response")
    return gen_query_response


def main():
    add_db_resp = add_db_conn()
    print(add_db_resp.status_code)

    remove_db_resp = remove_conn()
    print(remove_db_resp.status_code)
    add_db_resp = add_db_conn()
    print(add_db_resp.status_code)
    update_table_resp = add_table()
    print(update_table_resp.status_code)
    gen_query_resp = gen_query()
    print(gen_query_resp.status_code)
    print(gen_query_resp.json())


if __name__ == "__main__":
    main()
