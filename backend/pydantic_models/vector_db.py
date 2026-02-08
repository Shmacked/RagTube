from pydantic import BaseModel


class VectorDBInput(BaseModel):
    collection_name: str
    user_id: int
    input: str
