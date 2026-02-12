from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from backend.database import get_db
from backend.db_models.users import Users
from backend.pydantic_models.users import UserBase, User, UserLogin
from backend.db_models.sessions import UserSession
from backend.services.dependencies import set_login_session_id, is_authenticated
from backend.services.helpers import delete_urls


router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post("/login")
async def login(user: UserLogin, request: Request, response: Response, db: Session = Depends(get_db)):
    user = db.query(Users).filter(
        and_(
            or_(
                Users.username == user.username_or_email,
                Users.email == user.username_or_email
            ),
            Users.password == user.password
        )
    ).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    user_session = set_login_session_id(request, response, user, db=db)
    return User.model_validate(user)

@router.post("/")
async def create_user(user: UserBase, request: Request, response: Response, db: Session = Depends(get_db)):
    existing_user = db.query(Users).filter(or_(Users.username == user.username, Users.email == user.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    new_user = Users(username=user.username, password=user.password, email=user.email)
    db.add(new_user)
    db.commit()
    user_session = set_login_session_id(request, response, new_user, db=db)
    return User.model_validate(new_user)

# this also acts as a check for the authentication
@router.get("/", response_model=User)
async def get_user(user_session: UserSession = Depends(is_authenticated)):
    user = user_session.user
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete("/")
async def delete_user(request: Request, response: Response, db: Session = Depends(get_db), user_session: UserSession = Depends(is_authenticated)):
    user = user_session.user
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    success = delete_urls(user, db=db)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete user")
    db.delete(user)
    db.delete(user_session)
    db.commit()
    response.delete_cookie(key="login_session_id")
    return {"message": "User deleted successfully"}

@router.post("/logout")
async def logout(request: Request, response: Response, user_session: UserSession = Depends(is_authenticated)):
    response.delete_cookie(key="login_session_id")
    return {"message": "Logged out successfully"}

@router.get("/get_sessions")
async def get_sessions(db: Session = Depends(get_db), user_session: UserSession = Depends(is_authenticated)):
    sessions = db.query(UserSession).all()
    return sessions


