from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.graph.state import StateGraph
from langgraph.checkpoint.memory import MemorySaver

from langchain_core.messages import RemoveMessage

from langchain_openai import ChatOpenAI

from backend.services.helpers import save_langgraph_graph, load_chat_prompt
from backend.services.vector_db import search_vector_db
from langchain_core.documents import Document

from typing import List, Annotated, Any, TypedDict
from dotenv import load_dotenv
from pathlib import Path
import os



load_dotenv(dotenv_path="backend/.env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("MODEL")

llm = ChatOpenAI(model=MODEL, api_key=OPENAI_API_KEY)


class ChatState(TypedDict):
    messages: Annotated[List[Any], add_messages]
    context: List[Document]
    summary: str
    user_id: int


def get_chat_graph() -> StateGraph:
    graph = StateGraph(ChatState)

    def get_context(state: ChatState) -> str:
        user_id = state.get("user_id", None)
        _input = state.get("messages")[-1].content

        if user_id is None:
            raise ValueError("User ID is required")

        _filter = {
            "user_id": {
                "$eq": user_id
            }
        }

        search_results = search_vector_db("youtube_transcripts", _input, k=10, _filter=_filter)
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

        # Summarize the chat if it's longer than 10 messages
        if len(messages) == 10:
            prompt = load_chat_prompt("summarize")
            chain = prompt | llm
            summary = chain.invoke({"messages": messages})
            return {"summary": summary.content, "messages": [RemoveMessage(e) for e in messages[:-10]]}
        
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
