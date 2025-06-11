from fastapi import APIRouter, Form

from dotenv import load_dotenv

from redis_cache.redis_client import redis_client
from redis_cache.ai_tasks import ask_ai_task

load_dotenv()

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/ask-background")
async def ask_ai_bg(question: str = Form(...)):
    task = ask_ai_task.delay(question)
    return {"task_id": task.id}
