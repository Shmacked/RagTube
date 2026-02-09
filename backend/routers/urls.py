from fastapi import APIRouter, Depends, HTTPException

from backend.services.dependencies import is_authenticated
from backend.db_models.sessions import UserSession
from backend.services.helpers import create_url, get_urls, delete_url
from backend.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/urls",
    tags=["urls"],
)

@router.post("/")
async def create_url_endpoint(url: str, db: Session = Depends(get_db), user_session: UserSession = Depends(is_authenticated)):
    user = user_session.user
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return create_url(url, user, db=db)

@router.get("/")
async def get_urls_endpoint(db: Session = Depends(get_db), user_session: UserSession = Depends(is_authenticated)):
    user = user_session.user
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return get_urls(user, db=db)

@router.delete("/")
async def delete_url_endpoint(url: str, db: Session = Depends(get_db), user_session: UserSession = Depends(is_authenticated)):
    user = user_session.user
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return delete_url(url, user, db=db)
