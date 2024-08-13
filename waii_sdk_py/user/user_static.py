from waii_sdk_py.user import UserImpl
from waii_sdk_py.waii_http_client import WaiiHttpClient

User = UserImpl(WaiiHttpClient.get_instance())
