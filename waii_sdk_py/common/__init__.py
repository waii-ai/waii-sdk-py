from typing import Optional, List

from pydantic import BaseModel


class CommonRequest(BaseModel):
    tags: Optional[List[str]]

class LLMBasedRequest(CommonRequest):
    model: Optional[str]