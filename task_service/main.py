from fastapi import FastAPI, HTTPException
from models import Task, TaskCreate
import httpx
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("task_service")

app = FastAPI(title="Task Service", version="1.0.0")

tasks_db: list[Task] = []

NOTIFICATION_WEBHOOK_URL = "http://localhost:8001/api/webhooks/task_created"


@app.post("/api/tasks", response_model=Task, status_code=201)
async def create_task(task_data: TaskCreate):
    task = Task(**task_data.model_dump())
    tasks_db.append(task)
    logger.info(f"Task created: {task.id}")
    
    # Асинхронная отправка вебхука (не блокирует ответ клиенту)
    asyncio.create_task(send_webhook(task))
    
    return task


@app.get("/api/tasks", response_model=list[Task])
async def get_tasks():
    return tasks_db


async def send_webhook(task: Task, max_retries: int = 3):
    """Отправка вебхука с повторными попытками."""
    for attempt in range(1, max_retries + 1):
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    NOTIFICATION_WEBHOOK_URL,
                    json=task.model_dump()
                )
                if response.status_code == 200:
                    logger.info(f"Webhook sent successfully for task {task.id}")
                    return
                else:
                    logger.warning(f"Webhook attempt {attempt} failed: {response.status_code}")
        except httpx.RequestError as e:
            logger.warning(f"Webhook attempt {attempt} error: {e}")
        
        if attempt < max_retries:
            await asyncio.sleep(1)
    
    logger.error(f"❌ Failed to send webhook for task {task.id} after {max_retries} attempts")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)