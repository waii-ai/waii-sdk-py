import time

from waii_sdk_py import WAII
from waii_sdk_py.database import ModifyDBConnectionRequest, DBConnection
from waii_sdk_py.user import ListOrganizationsRequest, ListTenantsRequest, ListUsersRequest
from waii_sdk_py.waii_sdk_py import Waii


def connect_db(db_conn_to_add: DBConnection, impersonate_user=None):
    WAII.initialize(url="http://localhost:9859/api/", verbose=True)

    if impersonate_user:
        WAII.set_impersonate_user(impersonate_user)
    else:
        WAII.clear_impersonation()

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
            WAII.Database.activate_connection(db_conn_to_add.key)
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
    WAII.clear_impersonation()


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


def check_table_existence(waii: Waii, table_name, should_exist, max_wait_time=30, check_interval=1):
    """
    Check if a table exists or not in the database.

    :param table_name: Name of the table to check
    :param should_exist: Boolean, True if table should exist, False if it should not exist
    :param max_wait_time: Maximum time to wait in seconds (default 30)
    :param check_interval: Time to wait between checks in seconds (default 1)
    :return: Boolean, True if the condition is met, False if timeout occurs
    """
    end_time = time.time() + max_wait_time

    while time.time() < end_time:
        # Refresh the database connection
        waii.database.refresh_db_connection()

        # Check for table existence
        result = waii.database.get_catalogs()
        table_exists = any(
            table.name.table_name.lower() == table_name.lower()
            for catalog in result.catalogs
            for schema in catalog.schemas
            for table in schema.tables
        )

        # If the condition is met, return True
        if table_exists == should_exist:
            return True

        # Wait before next check
        time.sleep(check_interval)

    # If we've reached this point, we've timed out
    return False


def org_exists(waii: Waii, org_id: str) -> bool:
    orgs = waii.user.list_orgs(ListOrganizationsRequest()).organizations
    for org in orgs:
        if org.id == org_id:
            return True
    return False


def tenant_exists(waii: Waii, org_id: str, tenant_id: str) -> bool:
    tenants = waii.user.list_tenants(ListTenantsRequest(lookup_org_id=org_id)).tenants
    for tenant in tenants:
        if tenant.id == tenant_id:
            return True
    return False


def user_exists(waii: Waii, org_id: str, user_id: str) -> bool:
    users = waii.user.list_users(ListUsersRequest(lookup_org_id=org_id)).users
    for user in users:
        if user.id == user_id:
            return True
    return False