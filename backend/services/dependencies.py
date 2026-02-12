import uuid
from sqlalchemy.orm import Session
from fastapi import Request, Response, HTTPException, Depends

from backend.database import get_db
from backend.db_models.sessions import UserSession
from backend.db_models.users import Users


def is_authenticated(request: Request, response: Response, db: Session = Depends(get_db)) -> UserSession:
    session_id = request.cookies.get("login_session_id")

    if not session_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    user_session = db.query(UserSession).filter(UserSession.session_token == session_id).first()
    if not user_session:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    return user_session

def set_login_session_id(request: Request, response: Response, user: Users, db: Session = Depends(get_db)) -> UserSession:
    user_session = db.query(UserSession).filter(UserSession.user_id == user.id).first()
    token = str(uuid.uuid4())

    if not user_session:
        user_session = UserSession(session_token=token, user_id=user.id)
        db.add(user_session)
    
    user_session.session_token = token
    db.commit()
    response.set_cookie(
        key="login_session_id",
        value=token,
        httponly=True,
        max_age = 60 * 60,
        path="/",
        samesite=None,
        secure=False,    # MUST be False for HTTP
    )
    return user_session
