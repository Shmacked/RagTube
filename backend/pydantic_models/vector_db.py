from pydantic import BaseModel
from typing import Optional, Dict, Any


class VectorDBInputBase(BaseModel):
    input: str

class VectorDBSearchInput(VectorDBInputBase):
    collection_name: str
    k: int = 5
    _filter: Optional[Dict[str, Any]] = None