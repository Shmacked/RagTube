from langgraph.graph.state import CompiledStateGraph
from IPython.display import Image
import PIL.Image
from io import BytesIO

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from fastapi import Depends

from backend.services.vector_db import add_text_to_vector_db, delete_vector_db_data
from backend.services.audio_helpers import transcribe
from backend.db_models.urls import Urls
from backend.db_models.users import Users
from backend.database import get_db
from sqlalchemy.orm import Session
from typing import List

from pathlib import Path
import yaml



_PROMPT_CACHE: dict[str, ChatPromptTemplate] = {}



def delete_url(url: str, user: Users, db: Session = Depends(get_db)) -> bool:
    try:
        delete_vector_db_data("youtube_transcripts", metadata_filter={
            "$and": [
                {"user_id": {
                    "$eq": user.id
                    }
                },
                {"url": {
                    "$eq": url
                    }
                }
            ]
        })
        db.query(Urls).filter(Urls.url == url, Urls.user_id == user.id).delete()
        db.commit()
    except Exception as e:
        return False
    return True

def delete_urls(user: Users, db: Session = Depends(get_db)) -> bool:
    try:
        delete_vector_db_data("youtube_transcripts", metadata_filter={"user_id": {
               "$eq": user.id
            }
        })
        db.query(Urls).filter(Urls.user_id == user.id).delete()
        db.commit()
    except Exception as e:
        return False
    return True

def get_urls(user: Users, db: Session = Depends(get_db)) -> List[Urls]:
    return db.query(Urls).filter(Urls.user_id == user.id).all()

def create_url(url: str, user: Users, db: Session = Depends(get_db)) -> Urls:
    transcript = transcribe(url)
    for segment in transcript:
        add_text_to_vector_db("youtube_transcripts", segment.text, metadata={"user_id": user.id, "url": url, "start_time": segment.start, "end_time": segment.end})
    url_model = Urls(url=url, user_id=user.id)
    db.add(url_model)
    db.commit()
    db.refresh(url_model)
    return url_model

def save_langgraph_graph(path: str, graph: CompiledStateGraph) -> None:
    mermaid = graph.get_graph().draw_mermaid_png()
    buffer = BytesIO(Image(mermaid).data)
    img = PIL.Image.open(buffer)
    print(f"Saving graph to '{path}'.")
    img.save(path)
    return None

def load_chat_prompt(name: str) -> ChatPromptTemplate:
    if name in _PROMPT_CACHE:
        return _PROMPT_CACHE[name]

    path = Path("backend/prompts/chat_state.yaml")
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    if name not in cfg:
        raise KeyError(f"Prompt '{name}' not found in {path}")

    prompt_cfg = cfg[name]

    prompt = ChatPromptTemplate.from_messages([
        ("system", prompt_cfg["system"]),
        MessagesPlaceholder("messages"),
    ])

    _PROMPT_CACHE[name] = prompt
    return prompt

