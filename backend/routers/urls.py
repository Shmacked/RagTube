from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.background import BackgroundTasks
from backend.services.dependencies import is_authenticated
from backend.db_models.sessions import UserSession
from backend.services.helpers import create_url, get_urls, delete_url
from backend.database import get_db
from backend.db_models.urls import Urls
from sqlalchemy.orm import Session
from sse_starlette.sse import EventSourceResponse
import asyncio
import uuid
import json

router = APIRouter(
    prefix="/urls",
    tags=["urls"],
)

# In-memory store (Use Redis for production/multiple workers)
tasks_progress = {}
tasks_results = {}

@router.get("/progress/{task_id}")
async def get_progress(task_id: str, request: Request):
    async def event_generator():
        while True:
            if await request.is_disconnected():
                break

            task = tasks_progress.get(task_id, 0)
            
            # Check if there is a result yet
            result = tasks_results.get(task_id)

            if result:
                # Send the final result as a special event
                yield {
                    "event": "result",
                    "data": json.dumps(
                        {
                            "progress": 100,
                            "status": "completed",
                            "message": task.get("message", ""),
                            "url": task.get("url", ""),
                            "object": result
                        }
                    ) # Must be a string
                }
                break

            yield {
                "event": "update",
                "data": json.dumps(
                    {
                        "progress": task.get("progress", 0),
                        "status": task.get("status", "pending"),
                        "message": task.get("message", ""),
                        "url": task.get("url", ""),
                        "object": task.get("object", None)
                    }
                )
            }
            await asyncio.sleep(1)

    return EventSourceResponse(event_generator(), media_type="text/event-stream")

@router.post("/")
async def create_url_endpoint(background_tasks: BackgroundTasks, url: str, db: Session = Depends(get_db), user_session: UserSession = Depends(is_authenticated)):
    user = user_session.user
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    _uuid = str(uuid.uuid4())
    tasks_progress[_uuid] = {
        "progress": 0,
        "status": "pending",
        "url": url,
        "message": "Creating link...",
    }
    background_tasks.add_task(create_url, url, user, db=db, task_id=_uuid, task_memory=tasks_progress, tasks_results=tasks_results)
    return {"task_id": _uuid}

@router.get("/")
async def get_urls_endpoint(db: Session = Depends(get_db), user_session: UserSession = Depends(is_authenticated)):
    user = user_session.user
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return get_urls(user, db=db)

@router.delete("/")
async def delete_url_endpoint(linkId: int, db: Session = Depends(get_db), user_session: UserSession = Depends(is_authenticated)):
    user = user_session.user
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    link = db.query(Urls).filter(Urls.id == linkId, Urls.user_id == user.id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    return delete_url(link.url, user, db=db)
