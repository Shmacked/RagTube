from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.graph.state import StateGraph
from langgraph.checkpoint.memory import MemorySaver

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from backend.services.helpers import save_langgraph_graph

from pydantic import BaseModel
from typing import List, Annotated, Any
from dotenv import load_dotenv
import os


load_dotenv(dotenv_path="backend/.env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("MODEL")

llm = ChatOpenAI(model=MODEL, api_key=OPENAI_API_KEY)


class ChatState(BaseModel):
    input: str
    messages: Annotated[List[Any], add_messages]


def get_chat_graph() -> StateGraph:
    graph = StateGraph(ChatState)

    def chat_message(state: ChatState) -> ChatState:
        response = llm.invoke(state.messages + [HumanMessage(content=state.input)])
        return {"messages": state.messages + [response]}

    graph.add_node("chat_message", chat_message)

    graph.add_edge(START, "chat_message")
    graph.add_edge("chat_message", END)

    compiled = graph.compile(checkpointer=MemorySaver())
    save_langgraph_graph("backend/images/chat_graph.png", compiled)
    return compiled
