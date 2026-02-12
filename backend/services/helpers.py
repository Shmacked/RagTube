from langgraph.graph.state import CompiledStateGraph
from IPython.display import Image
import PIL.Image
from io import BytesIO

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from fastapi import Depends, HTTPException

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

def create_url(url: str, user: Users, db: Session = Depends(get_db), task_id: str = None, task_memory: dict = None, tasks_results: dict = None) -> Urls:
    if task_id and task_memory is None:
        raise HTTPException(status_code=400, detail="Task memory is required")
    if task_id and tasks_results is None:
        raise HTTPException(status_code=400, detail="Tasks results is required")
    if db.query(Urls).filter(Urls.url == url, Urls.user_id == user.id).first():
        task_memory[task_id]["status"] = "failed"
        task_memory[task_id]["message"] = "Link already exists"
        raise HTTPException(status_code=400, detail="Link already exists")

    transcript = transcribe(url, task_id=task_id, task_memory=task_memory, tasks_results=tasks_results)
    segment_count = len([e for e in transcript])
    for i, segment in enumerate(transcript):
        task_memory[task_id]["progress"] = (int(((i + 1) / segment_count) * 100) / 2) + 50
        task_memory[task_id]["message"] = f"Adding segment {i + 1} of {segment_count} to vector database"
        add_text_to_vector_db("youtube_transcripts", segment.text, metadata={"user_id": user.id, "url": url, "start_time": segment.start, "end_time": segment.end})
    url_model = Urls(url=url, user_id=user.id)
    db.add(url_model)
    db.commit()
    db.refresh(url_model)
    task_memory[task_id]["status"] = "completed"
    task_memory[task_id]["message"] = "Link created successfully"
    task_memory[task_id]["progress"] = 100
    tasks_results[task_id] = url_model.to_dict()
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

