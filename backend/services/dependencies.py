import uuid
from sqlalchemy.orm import Session
from fastapi import Request, Response, HTTPException, Depends

from backend.database import get_db
from backend.db_models.sessions import UserSession
from backend.db_models.users import Users


def is_authenticated(request: Request, response: Response, db: Session = Depends(get_db)) -> UserSession:
    session_id = request.cookies.get("login_session_id")
    if not session_id:
        print("No session ID found")
        raise HTTPException(status_code=401, detail="Unauthorized")

    user_session = db.query(UserSession).filter(UserSession.session_token == session_id).first()
    if not user_session:
        print("No user session found")
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    return user_session

def set_login_session_id(request: Request, response: Response, user: Users, db: Session = Depends(get_db)) -> UserSession:
    user_session = db.query(UserSession).filter(UserSession.user_id == user.id).first()

    if user_session:
        user_session.session_token = str(uuid.uuid4())
        db.commit()
        response.set_cookie(key="login_session_id", value=user_session.session_token, httponly=True)
        return user_session

    user_session = UserSession(session_token=str(uuid.uuid4()), user_id=user.id)
    db.add(user_session)
    db.commit()
    response.set_cookie(key="login_session_id", value=user_session.session_token, httponly=True)
        
    return user_session
