from typing import Optional, List

from ..my_pydantic import BaseModel


class CommonRequest(BaseModel):
    tags: Optional[List[str]]

class LLMBasedRequest(CommonRequest):
    model: Optional[str]
    # should we use cache?
    use_cache: Optional[bool] = True