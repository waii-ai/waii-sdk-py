from typing import Optional, List, Dict, Any

from ..my_pydantic import BaseModel


class CommonRequest(BaseModel):
    tags: Optional[List[str]]
    parameters: Optional[Dict[str, Any]]


class LLMBasedRequest(CommonRequest):
    model: Optional[str]
    # should we use cache?
    use_cache: Optional[bool] = True


class CommonResponse(BaseModel):
    pass
