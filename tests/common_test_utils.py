import time

from waii_sdk_py import WAII
from waii_sdk_py.database import ModifyDBConnectionRequest, DBConnection


def connect_db(db_conn_to_add: DBConnection):
    WAII.initialize(url="http://localhost:9859/api/")

    # add the database connection
    try:
        WAII.Database.modify_connections(
            ModifyDBConnectionRequest(updated=[db_conn_to_add])
        ).connectors
    except Exception as e:
        print(e)
        print("""In order to run the test, you need to run Waii locally, and setup the following
        sudo -u $USER psql postgres
        CREATE ROLE waii WITH LOGIN CREATEDB PASSWORD 'password';
        CREATE DATABASE waii_sdk_test;
        GRANT ALL PRIVILEGES ON DATABASE waii_sdk_test TO waii;
        """)

    max_wait_time = 60

    # wait till the index is finished
    while True:
        try:
            catalogs = WAII.Database.get_catalogs()
            if catalogs.catalogs and len(catalogs.catalogs) > 0:
                break
        except Exception as e:
            print(e)
        max_wait_time -= 1
        if max_wait_time == 0:
            raise Exception("Cannot get the catalog")
        time.sleep(1)

    WAII.Database.activate_connection(db_conn_to_add.key)


def load_db_conn1():
    db_connection = DBConnection(
        key="postgresql://waii@localhost:5432/waii_sdk_test",  # will be generated by the system
        db_type="postgresql",
        host="localhost",
        port=5432,
        database="waii_sdk_test",
        username="waii",
        password="password"
    )
    return db_connection


def load_db_conn2():
    db_connection = DBConnection(
        key="postgresql://waii@localhost:5432/waii_sdk_test2",  # will be generated by the system
        db_type="postgresql",
        host="localhost",
        port=5432,
        database="waii_sdk_test2",
        username="waii",
        password="password"
    )
    return db_connection