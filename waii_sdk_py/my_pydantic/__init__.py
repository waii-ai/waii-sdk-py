try:
    from pydantic.v1 import (
        BaseModel,
        ValidationError,
        PrivateAttr,
        Field,
        # Add other necessary imports here
    )

    class StrictBaseModel(BaseModel, extra='forbid'):
        pass
    # class WaiiBaseModel(BaseModel):
    #     pass
except ImportError:
    try:
        from pydantic import (
            BaseModel,
            ValidationError,
            PrivateAttr,
            Field,
            # Add other necessary imports here
        )

        class StrictBaseModel(BaseModel, extra='forbid'):
            pass
        # class WaiiBaseModel(BaseModel):
        #     pass
    except ImportError:
        raise ImportError("Cannot find pydantic module. Please install pydantic. You can use >= 1.10.x or >= 2.7.x")

__all__ = [
    "BaseModel",
    "StrictBaseModel",
    "ValidationError",
    "PrivateAttr",
    "Field"
]