from .waii_sdk_py import WAII

# Add these two imports to avoid you have to from waii_sdk_py.waii_sdk_py import AsyncWaii
# (which is ugly).
from .waii_sdk_py import AsyncWaii
from .waii_sdk_py import Waii