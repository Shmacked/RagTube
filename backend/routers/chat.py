from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.services.dependencies import is_authenticated
from backend.pydantic_models.user_sessions import UserSessionBase
from backend.pydantic_models.chat import ChatInput
from backend.services.langgraph import get_chat_graph

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)

chat_graph = get_chat_graph()

@router.post("/")
async def chat(chat_input: ChatInput, db: Session = Depends(get_db), user_session: UserSessionBase = Depends(is_authenticated)):
    response = chat_graph.invoke({
            "messages": [("user", chat_input.input)],
            "user_id": user_session.user.id
        },
        config={"configurable": {
            "thread_id": user_session.session_token
        }
    })
    return {"output": response["messages"][-1].content}
