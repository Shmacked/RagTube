from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import StateGraph
from langgraph.checkpoint.memory import MemorySaver

from langchain_core.messages import RemoveMessage

from langchain_openai import ChatOpenAI

from backend.services.helpers import save_langgraph_graph, load_chat_prompt
from backend.services.vector_db import search_vector_db
from langchain_core.documents import Document

from typing import List, Annotated, Any, TypedDict
from dotenv import load_dotenv
import os



load_dotenv(dotenv_path="backend/.env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("MODEL")

llm = ChatOpenAI(model=MODEL, api_key=OPENAI_API_KEY)


from langchain_core.messages import RemoveMessage

def basic_reducer(left: list | tuple | None, right: list | dict) -> list:
    # 1. Force 'left' to be a list. LangGraph often sends () on init.
    if left is None or isinstance(left, tuple):
        left = []
    
    # 2. Force 'right' to be a list of updates
    if not isinstance(right, list):
        updates = [right]
    else:
        updates = right

    new_state = list(left)

    # print(f"Left: {left}")
    # print(f"Right: {right}")

    for message in updates:
        if isinstance(message, RemoveMessage):
            # Filtering out the ID
            new_state = [m for m in new_state if m.id != message.id]
        else:
            new_state.append(message)

    return new_state


class ChatState(TypedDict):
    messages: Annotated[List[Any], basic_reducer]
    context: List[Document]
    summary: str
    user_id: int


def get_chat_graph() -> StateGraph:
    graph = StateGraph(ChatState)

    def get_context(state: ChatState) -> str:
        user_id = state.get("user_id", None)
        messages = state.get("messages", [])
            
        if not messages:
            return {}

        last_msg = messages[-1]
        
        # Check if it's a LangChain message object (BaseMessage)
        if hasattr(last_msg, "content"):
            _input = last_msg.content
        # Check if it's a plain dictionary
        elif isinstance(last_msg, dict):
            _input = last_msg.get("content", "")
        else:
            _input = str(last_msg)

        if user_id is None:
            raise ValueError("User ID is required")

        _filter = {
            "user_id": {
                "$eq": user_id
            }
        }

        search_results = search_vector_db("youtube_transcripts", _input, k=20, _filter=_filter)
        return {"context": search_results}

    def chat_message(state: ChatState) -> ChatState:
        context = state.get("context", "")
        messages = state.get("messages", [])
        summary = state.get("summary", "")

        prompt = load_chat_prompt("chat")

        chain = prompt | llm

        response = chain.invoke({
            "context": context,
            "messages": messages,
            "summary": summary,
        })

        return {"messages": [response]}

    def summarize_chat(state: ChatState) -> ChatState:
        messages = state.get("messages", [])
        MESSAGES_TO_REMOVE = 10

        # Summarize the chat if it's longer than 10 messages
        if len(messages) >= MESSAGES_TO_REMOVE:
            prompt = load_chat_prompt("summarize")
            chain = prompt | llm
            summary = chain.invoke({"messages": messages})
            return {"summary": summary.content, "messages": [RemoveMessage(id=e.id) for e in messages[:MESSAGES_TO_REMOVE - 1]]}
        
        return {}

    graph.add_node("get_context", get_context)
    graph.add_node("chat_message", chat_message)
    graph.add_node("summarize_chat", summarize_chat)

    graph.add_edge(START, "get_context")
    graph.add_edge("get_context", "chat_message")
    graph.add_edge("chat_message", "summarize_chat")
    graph.add_edge("summarize_chat", END)

    compiled = graph.compile(checkpointer=MemorySaver())
    save_langgraph_graph("backend/images/chat_graph.png", compiled)
    return compiled
