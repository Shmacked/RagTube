from pydantic import BaseModel
from typing import List, Any

class ChatInput(BaseModel):
    input: str

