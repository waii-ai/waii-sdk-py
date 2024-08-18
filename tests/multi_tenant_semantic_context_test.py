import unittest

from tests.common_test_utils import load_db_conn1, load_db_conn2, connect_db, org_exists, tenant_exists, user_exists
from waii_sdk_py.query import QueryGenerationRequest
from waii_sdk_py.semantic_context import ModifySemanticContextRequest, SemanticStatement
from waii_sdk_py.user import Organization, CreateOrganizationRequest, Tenant, CreateTenantRequest, User, \
    CreateUserRequest, WaiiRoles, ListUsersRequest, DeleteUserRequest, DeleteTenantRequest
from waii_sdk_py.waii_sdk_py import Waii, WAII


class MultiTenantSemanticContextTest(unittest.TestCase):
    def setUp(self):
        self.movie_conn = load_db_conn1()
        self.album_conn = load_db_conn2()

        waii_client = Waii()
        waii_client.initialize(url="http://localhost:9859/api/")
        self.waii_client = waii_client
        self.waii_client.database.activate_connection(self.movie_conn.key)

        self.setup_users()

        # add the database connections to users
        for impersonate_user in ['multi-tenant-semantic-context-test-user1', 'multi-tenant-semantic-context-test-user2',
                                 '']:
            connect_db(self.movie_conn, impersonate_user=impersonate_user)
            connect_db(self.album_conn, impersonate_user=impersonate_user)

        # setup semantic context
        self.create_global_semantic_statements()

        # before we start, delete all the semantic rules
        self.delete_all_semantic_rules("multi-tenant-semantic-context-test-user1")
        self.delete_all_semantic_rules("multi-tenant-semantic-context-test-user2")

        self.create_semantic_rules_for_user1()
        self.create_semantic_rules_for_user2()

    def delete_all_semantic_rules(self, user_id):
        with self.waii_client.impersonate_user(user_id):
            response = self.waii_client.semantic_context.get_semantic_context().semantic_context
            for semantic in response:
                if semantic.user_id == user_id:
                    self.waii_client.semantic_context.modify_semantic_context(
                        ModifySemanticContextRequest(deleted=[semantic.id]))
            self.waii_client.clear_impersonation()

    def setup_users(self):
        client = self.waii_client

        # first list users under the new org
        response = client.user.list_users(ListUsersRequest(lookup_org_id="multi-tenant-semantic-context-test"))
        for user in response.users:
            client.user.delete_user(DeleteUserRequest(id=user.id))

        # delete the tenant
        response = client.user.list_tenants(ListUsersRequest(lookup_org_id="multi-tenant-semantic-context-test"))
        for tenant in response.tenants:
            client.user.delete_tenant(DeleteTenantRequest(id=tenant.id))

        # Create organization
        org_id = "multi-tenant-semantic-context-test"
        if not org_exists(client, org_id):
            org = Organization(id=org_id, name="Multi-tenant Semantic Context Test Org")
            client.user.create_org(CreateOrganizationRequest(organization=org))

        # Create tenant
        tenant_id = "test-tenant"
        if not tenant_exists(client, org_id, tenant_id):
            tenant = Tenant(id=tenant_id, name="Test Tenant", org_id=org_id)
            client.user.create_tenant(CreateTenantRequest(tenant=tenant))

        # Create users
        users = [
            {"id": "multi-tenant-semantic-context-test-user1", "name": "User 1"},
            {"id": "multi-tenant-semantic-context-test-user2", "name": "User 2"}
        ]

        for user_info in users:
            if not user_exists(client, org_id, user_info["id"]):
                # create user with WAII_USER role
                user = User(id=user_info["id"], name=user_info["name"], tenant_id=tenant_id, org_id=org_id,
                            roles=[WaiiRoles.WAII_USER])
                client.user.create_user(CreateUserRequest(user=user))
        print("Hierarchy creation completed.")

    def create_global_semantic_statements(self):
        request = ModifySemanticContextRequest(updated=[SemanticStatement(
            id="global-semantic-statement-1",
            statement="All the returned query must project column 'WAII_TEST' for output, which return a constant value of 'WAII'")])
        self.waii_client.semantic_context.modify_semantic_context(request)

    def create_semantic_rules_for_user1(self):
        with self.waii_client.impersonate_user("multi-tenant-semantic-context-test-user1"):
            request = ModifySemanticContextRequest(updated=[SemanticStatement(
                id="user1-semantic-statement-1",
                statement="All the returned query must project column 'FROM_USER' for output, which return a constant value of 'USER1'",
                user_id="multi-tenant-semantic-context-test-user1",
                tenant_id="test-tenant",
                org_id="multi-tenant-semantic-context-test")
            ])
            self.waii_client.semantic_context.modify_semantic_context(request)

    def create_semantic_rules_for_user2(self):
        with self.waii_client.impersonate_user("multi-tenant-semantic-context-test-user2"):
            request = ModifySemanticContextRequest(updated=[SemanticStatement(
                id="user2-semantic-statement",
                statement="All the returned query must project column 'FROM_USER' for output, which return a constant value of 'USER2'",
                user_id="multi-tenant-semantic-context-test-user2",
                tenant_id="test-tenant",
                org_id="multi-tenant-semantic-context-test")
            ])
            self.waii_client.semantic_context.modify_semantic_context(request)

    @staticmethod
    def _semantic_id_in_list(semantic_id, semantic_list):
        for semantic in semantic_list:
            if semantic.id == semantic_id:
                return True
        return False

    def test_list_semantic_statements(self):
        response = self.waii_client.semantic_context.get_semantic_context().semantic_context
        assert self._semantic_id_in_list("global-semantic-statement-1", response)

        with self.waii_client.impersonate_user("multi-tenant-semantic-context-test-user1"):
            response = self.waii_client.semantic_context.get_semantic_context().semantic_context
            assert self._semantic_id_in_list("user1-semantic-statement-1", response) and not self._semantic_id_in_list(
                "user2-semantic-statement", response)

        with self.waii_client.impersonate_user("multi-tenant-semantic-context-test-user2"):
            response = self.waii_client.semantic_context.get_semantic_context().semantic_context
            assert self._semantic_id_in_list("user2-semantic-statement", response) and not self._semantic_id_in_list(
                "user1-semantic-statement-1", response)

    def test_gen_query_uses_semantic_context(self):
        # generate query as main user
        response = self.waii_client.query.generate(QueryGenerationRequest(
            ask="how many movies are there"
        )).run()
        assert response.rows[0]['WAII_TEST'] == 'WAII'

        # generate query as user1
        with self.waii_client.impersonate_user("multi-tenant-semantic-context-test-user1"):
            response = self.waii_client.query.generate(QueryGenerationRequest(
                ask="how many movies are there"
            )).run()
            assert response.rows[0]['FROM_USER'] == 'USER1'
            assert response.rows[0]['WAII_TEST'] == 'WAII'

        # generate query as user2
        with self.waii_client.impersonate_user("multi-tenant-semantic-context-test-user2"):
            response = self.waii_client.query.generate(QueryGenerationRequest(
                ask="how many movies are there"
            )).run()
            assert response.rows[0]['FROM_USER'] == 'USER2'
            assert response.rows[0]['WAII_TEST'] == 'WAII'
