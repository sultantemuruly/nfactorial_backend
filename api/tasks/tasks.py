from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.models import Tasks
from db.dependencies import get_db
from schemas.task_schemas import TaskCreate, TaskUpdate, TaskOut
from api.users.users import get_current_user
from db.models import Users
from typing import List
from services.task_cache import TaskCacheService

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/", response_model=TaskOut)
async def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    # Create task in database
    db_task = Tasks(**task.dict(), user_id=current_user.id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    # Cache the new task and invalidate user's tasks list cache
    await TaskCacheService.cache_task(db_task)
    await TaskCacheService.invalidate_user_cache(current_user.id)

    return db_task


@router.get("/{task_id}", response_model=TaskOut)
async def read_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    # Try cache first
    cached_task = await TaskCacheService.get_task_from_cache(task_id, current_user.id)
    if cached_task:
        return TaskOut(**cached_task)

    # If not in cache, get from database
    task = (
        db.query(Tasks)
        .filter(Tasks.id == task_id, Tasks.user_id == current_user.id)
        .first()
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Cache the task for future requests
    await TaskCacheService.cache_task(task)

    return task


@router.put("/{task_id}", response_model=TaskOut)
async def update_task(
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

    # Update task in database
    for key, value in task_data.dict(exclude_unset=True).items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)

    # Update cache
    await TaskCacheService.cache_task(task)
    await TaskCacheService.invalidate_user_cache(current_user.id)

    return task


@router.delete("/{task_id}")
async def delete_task(
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

    # Delete from database
    db.delete(task)
    db.commit()

    # Invalidate caches
    await TaskCacheService.invalidate_task_cache(task_id)
    await TaskCacheService.invalidate_user_cache(current_user.id)

    return {"detail": "Task deleted successfully"}


@router.get("/", response_model=List[TaskOut])
async def list_user_tasks(
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    # Try cache first
    cached_tasks = await TaskCacheService.get_user_tasks_from_cache(current_user.id)
    if cached_tasks:
        return [TaskOut(**task) for task in cached_tasks]

    # If not in cache, get from database
    tasks = db.query(Tasks).filter(Tasks.user_id == current_user.id).all()

    # Cache the results
    await TaskCacheService.cache_user_tasks(current_user.id, tasks)

    return tasks


# Cache management endpoints for debugging
@router.delete("/cache/clear")
async def clear_user_task_cache(
    current_user: Users = Depends(get_current_user),
):
    """Clear all cached data for the current user"""
    await TaskCacheService.invalidate_all_user_caches(current_user.id)
    return {"message": f"Cache cleared for user {current_user.id}"}


@router.delete("/cache/task/{task_id}")
async def clear_task_cache(
    task_id: int,
    current_user: Users = Depends(get_current_user),
):
    """Clear cache for a specific task"""
    await TaskCacheService.invalidate_task_cache(task_id)
    return {"message": f"Cache cleared for task {task_id}"}
