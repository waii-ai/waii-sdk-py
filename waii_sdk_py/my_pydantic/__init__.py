try:
    from pydantic.v1 import (
        BaseModel,
        ValidationError,
        PrivateAttr,
        Field,
        # Add other necessary imports here
    )
except ImportError:
    try:
        from pydantic import (
            BaseModel,
            ValidationError,
            PrivateAttr,
            Field,
            # Add other necessary imports here
        )
    except ImportError:
        raise ImportError("Cannot find pydantic module. Please install pydantic. You can use >= 1.10.x or >= 2.7.x")

__all__ = [
    "BaseModel",
    "ValidationError",
    "PrivateAttr",
    "Field"
]