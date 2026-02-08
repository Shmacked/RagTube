from pydantic import BaseModel, ConfigDict
from datetime import datetime

class UserSessionBase(BaseModel):
    id: int
    user_id: int
    session_token: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)