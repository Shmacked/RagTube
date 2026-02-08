from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.services.dependencies import is_authenticated
from backend.database import get_db
from backend.services.vector_db import add_text_to_vector_db, search_vector_db
from backend.pydantic_models.vector_db import VectorDBInput
from backend.db_models.users import Users
from backend.db_models.sessions import UserSession

router = APIRouter(
    prefix="/vector_db",
    tags=["vector_db"],
)


@router.post("/")
async def add_text_to_vector_db(input: VectorDBInput, db: Session = Depends(get_db), user_session_id: str = Depends(is_authenticated)):
    User = db.query(Users).filter(Users.session_id == user_session_id).first()
    return add_text_to_vector_db(input.collection_name, input.user_id, input.input)

@router.post("/search")
async def search_vector_db(input: VectorDBInput, db: Session = Depends(get_db), user_session_id: str = Depends(is_authenticated)):
    User = db.query(UserSession).filter(UserSession.session_token == user_session_id).first()
    return search_vector_db(input.collection_name, input.user_id, input.input)
