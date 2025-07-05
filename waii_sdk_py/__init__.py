"""
Copyright 2023–2025 Waii, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from .waii_sdk_py import WAII

# Add these two imports to avoid you have to from waii_sdk_py.waii_sdk_py import AsyncWaii
# (which is ugly).
from .waii_sdk_py import AsyncWaii
from .waii_sdk_py import Waii