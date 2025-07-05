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

try:
    from pydantic.v1 import (
        BaseModel,
        ValidationError,
        PrivateAttr,
        Field,
        # Add other necessary imports here
    )

    class WaiiBaseModel(BaseModel, extra='allow'):
        def check_extra_fields(self):
            extra_fields = {k: v for k, v in self.__dict__.items() if k not in self.__class__.__fields__}
            if extra_fields != {}:
                raise ValueError(f'Cannot set unknown fields: {list(extra_fields.keys())}')
            for field_name, field in self.__fields__.items():
                field_value = getattr(self, field_name)
                if field_value is None:
                    continue
                if isinstance(field_value, list):
                    for item in field_value:
                        if isinstance(item, WaiiBaseModel):
                            item.check_extra_fields()
                elif isinstance(field_value, dict):
                    for k, v in field_value.items():
                        if isinstance(v, WaiiBaseModel):
                            v.check_extra_fields()
                elif isinstance(field_value, WaiiBaseModel):
                    field_value.check_extra_fields()
        
except ImportError:
    try:
        from pydantic import (
            BaseModel,
            ValidationError,
            PrivateAttr,
            Field,
            # Add other necessary imports here
        )

        class WaiiBaseModel(BaseModel, extra='allow'):
            def check_extra_fields(self):
                if self.model_extra != {}:
                    raise ValueError(f'Cannot set unknown fields: {list(self.model_extra.keys())}')
                
                for field_name, field in self.model_fields.items():
                    field_value = getattr(self, field_name)
                    if field_value is None:
                        continue
                    if isinstance(field_value, list):
                        for item in field_value:
                            if isinstance(item, WaiiBaseModel):
                                item.check_extra_fields()
                    elif isinstance(field_value, dict):
                        for k, v in field_value.items():
                            if isinstance(v, WaiiBaseModel):
                                v.check_extra_fields()
                    elif isinstance(field_value, WaiiBaseModel):
                        field_value.check_extra_fields()

                    
    except ImportError:
        raise ImportError("Cannot find pydantic module. Please install pydantic. You can use >= 1.10.x or >= 2.7.x")

__all__ = [
    "BaseModel",
    "WaiiBaseModel",
    "ValidationError",
    "PrivateAttr",
    "Field"
]
