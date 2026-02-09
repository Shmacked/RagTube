from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.services.dependencies import is_authenticated
from backend.database import get_db
from backend.services.vector_db import add_text_to_vector_db, search_vector_db, delete_vector_db
from backend.pydantic_models.vector_db import VectorDBInputBase, VectorDBSearchInput
from backend.db_models.sessions import UserSession


router = APIRouter(
    prefix="/vector_db",
    tags=["vector_db"],
)


@router.post("/")
async def add_text_to_vector_db_endpoint(input: VectorDBInputBase, user_session: UserSession = Depends(is_authenticated)):
    user = user_session.user
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return add_text_to_vector_db("test_collection", input.input, metadata={"user_id": user.id})

@router.post("/search")
async def search_vector_db_endpoint(input: VectorDBSearchInput, user_session: UserSession = Depends(is_authenticated)):
    user = user_session.user
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if input._filter is None:
        input._filter = {}
    input._filter["user_id"] = {"$eq": user.id}
    return search_vector_db(input.collection_name, input.input, _filter=input._filter)

@router.delete("/")
async def delete_vector_db_endpoint(collection_name: str, user_session: UserSession = Depends(is_authenticated)):
    user = user_session.user
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return delete_vector_db(collection_name)
