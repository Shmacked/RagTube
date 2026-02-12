from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.services.dependencies import is_authenticated
from backend.pydantic_models.user_sessions import UserSessionBase
from backend.pydantic_models.chat import ChatInput
from backend.services.langgraph import get_chat_graph
from langchain_core.messages import HumanMessage

import time

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)

chat_graph = get_chat_graph()

@router.post("/")
async def chat(chat_input: ChatInput, db: Session = Depends(get_db), user_session: UserSessionBase = Depends(is_authenticated)):
    response = chat_graph.invoke({
            "messages": [HumanMessage(content=chat_input.input, id=f"msg_{time.time()}")],
            "user_id": user_session.user.id
        },
        config={"configurable": {
            "thread_id": user_session.session_token
        }
    })
    return {"output": response["messages"][-1]}

@router.get("/")
async def get_chat(db: Session = Depends(get_db), user_session: UserSessionBase = Depends(is_authenticated)):
    config = {"configurable": {"thread_id": user_session.session_token}}
    state = chat_graph.get_state(config=config).values
    return {"messages": state.get("messages", []), "summary": state.get("summary", "")}
