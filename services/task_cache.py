from redis_cache.redis_client import redis_client
from db.models import Tasks
from typing import List, Optional
import json


class TaskCacheService:
    @staticmethod
    def _get_user_tasks_cache_key(user_id: int) -> str:
        return f"user_tasks:{user_id}"

    @staticmethod
    def _get_task_cache_key(task_id: int) -> str:
        return f"task:{task_id}"

    @staticmethod
    async def get_user_tasks_from_cache(user_id: int) -> Optional[List[dict]]:
        """Get user's tasks from cache"""
        cache_key = TaskCacheService._get_user_tasks_cache_key(user_id)
        cached_tasks = await redis_client.get(cache_key)
        if cached_tasks:
            print(f"Cache HIT for user {user_id} tasks")
            return cached_tasks
        print(f"Cache MISS for user {user_id} tasks")
        return None

    @staticmethod
    async def cache_user_tasks(user_id: int, tasks: List[Tasks], expire: int = 300):
        """Cache user's tasks"""
        cache_key = TaskCacheService._get_user_tasks_cache_key(user_id)
        tasks_dict = [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "user_id": task.user_id,
            }
            for task in tasks
        ]
        await redis_client.set(cache_key, tasks_dict, expire=expire)
        print(f"Cached {len(tasks)} tasks for user {user_id}")

    @staticmethod
    async def get_task_from_cache(task_id: int, user_id: int) -> Optional[dict]:
        """Get single task from cache"""
        cache_key = TaskCacheService._get_task_cache_key(task_id)
        cached_task = await redis_client.get(cache_key)

        if cached_task and cached_task.get("user_id") == user_id:
            print(f"Cache HIT for task {task_id}")
            return cached_task
        print(f"Cache MISS for task {task_id}")
        return None

    @staticmethod
    async def cache_task(task: Tasks, expire: int = 300):
        """Cache single task"""
        cache_key = TaskCacheService._get_task_cache_key(task.id)
        task_dict = {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "user_id": task.user_id,
        }
        await redis_client.set(cache_key, task_dict, expire=expire)
        print(f"Cached task {task.id}")

    @staticmethod
    async def invalidate_user_cache(user_id: int):
        """Invalidate user's tasks cache"""
        cache_key = TaskCacheService._get_user_tasks_cache_key(user_id)
        await redis_client.delete(cache_key)
        print(f"Invalidated cache for user {user_id}")

    @staticmethod
    async def invalidate_task_cache(task_id: int):
        """Invalidate single task cache"""
        cache_key = TaskCacheService._get_task_cache_key(task_id)
        await redis_client.delete(cache_key)
        print(f"Invalidated cache for task {task_id}")

    @staticmethod
    async def invalidate_all_user_caches(user_id: int):
        """Invalidate all caches related to a user"""
        await TaskCacheService.invalidate_user_cache(user_id)
        # Also invalidate individual task caches for this user's tasks
        pattern = f"task:*"
        await redis_client.delete_pattern(pattern)
        print(f"Invalidated all caches for user {user_id}")
