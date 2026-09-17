from pydantic import BaseModel
from typing import Optional
from enum import Enum


class TaskStatus(str, Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class Task(BaseModel):
    id: str
    title: str
    description: Optional[str] = ""
    status: TaskStatus
    created_at: str