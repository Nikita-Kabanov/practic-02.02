from fastapi import FastAPI
from models import Task
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("notification_service")

app = FastAPI(title="Notification Service", version="1.0.0")

LOG_FILE = "notifications.log"


@app.post("/api/webhooks/task_created", status_code=200)
async def receive_task_webhook(task: Task):
    log_message = (
        f"[{datetime.utcnow().isoformat()}] "
        f"📧 Notification sent for task '{task.title}' (id: {task.id}, status: {task.status})\n"
    )
    
    # Запись в консоль
    logger.info(log_message.strip())
    
    # Запись в лог-файл
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_message)
    
    return {"status": "logged", "task_id": task.id}


@app.get("/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)     