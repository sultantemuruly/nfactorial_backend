from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.models import Tasks
from db.dependencies import get_db
from schemas.task_schemas import TaskCreate, TaskUpdate, TaskOut
from api.users.users import get_current_user
from db.models import Users
from typing import List

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/", response_model=TaskOut)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    db_task = Tasks(**task.dict(), user_id=current_user.id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@router.get("/{task_id}", response_model=TaskOut)
def read_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    task = (
        db.query(Tasks)
        .filter(Tasks.id == task_id, Tasks.user_id == current_user.id)
        .first()
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskOut)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    task = (
        db.query(Tasks)
        .filter(Tasks.id == task_id, Tasks.user_id == current_user.id)
        .first()
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    for key, value in task_data.dict().items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    task = (
        db.query(Tasks)
        .filter(Tasks.id == task_id, Tasks.user_id == current_user.id)
        .first()
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
    return {"detail": "Task deleted successfully"}


@router.get("/", response_model=List[TaskOut])
def list_user_tasks(
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    return db.query(Tasks).filter(Tasks.user_id == current_user.id).all()
