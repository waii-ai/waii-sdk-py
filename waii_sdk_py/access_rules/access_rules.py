from enum import Enum
from typing import Optional, List

from ..my_pydantic import WaiiBaseModel

from waii_sdk_py.common import CommonRequest, CommonResponse
from waii_sdk_py.database import TableName
from waii_sdk_py.waii_http_client import WaiiHttpClient
from ..user import User
from waii_sdk_py.utils import wrap_methods_with_async
UPDATE_TABLE_ACCESS_RULES_ENDPOINT = "update-table-access-rules"
REMOVE_TABLE_ACCESS_RULES_ENDPOINT = "remove-table-access-rules"
LIST_TABLE_ACCESS_RULES_ENDPOINT = "list-table-access-rules"


class TableAccessRuleType(str, Enum):
    filter = "filter"  # protect all access with a filter
    block = "block"  # stop all access from the identified users


class TableAccessRule(WaiiBaseModel):
    id: Optional[str]
    name: str
    table: TableName
    org_id: str = '*'
    tenant_id: str = '*'
    user_id: str = '*'
    type: TableAccessRuleType
    expression: Optional[str]


class UpdateTableAccessRuleRequest(CommonRequest):
    rules: List[TableAccessRule]


class RemoveTableAccessRuleRequest(CommonRequest):
    rules: List[str]


class ListTableAccessRuleRequest(CommonRequest):
    table: Optional[TableName]
    ids: Optional[List[str]]
    lookup_user: Optional[User]


class ListTableAccessRuleResponse(CommonResponse):
    rules: Optional[List[TableAccessRule]]


class AccessRuleImpl:

    def __init__(self, http_client: WaiiHttpClient):
        self.http_client = http_client

    def update_table_access_rules(
            self, params: UpdateTableAccessRuleRequest
    ) -> CommonResponse:
        return self.http_client.common_fetch(
            UPDATE_TABLE_ACCESS_RULES_ENDPOINT, params, CommonResponse
        )

    def remove_table_access_rules(
            self, params: RemoveTableAccessRuleRequest
    ) -> CommonResponse:
        return self.http_client.common_fetch(
            REMOVE_TABLE_ACCESS_RULES_ENDPOINT, params, CommonResponse
        )

    def list_table_access_rules(
            self, params: ListTableAccessRuleRequest
    ) -> ListTableAccessRuleResponse:
        return self.http_client.common_fetch(
            LIST_TABLE_ACCESS_RULES_ENDPOINT, params, ListTableAccessRuleResponse
        )


class AsyncAccessRuleImpl:
    def __init__(self, http_client: WaiiHttpClient):
        self._access_rule_impl = AccessRuleImpl(http_client)
        wrap_methods_with_async(self._access_rule_impl, self)

AccessRules = AccessRuleImpl(WaiiHttpClient.get_instance())
