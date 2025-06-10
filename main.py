from fastapi import FastAPI
from api.users import users
from api.tasks import tasks
from redis_cache.redis_client import redis_client

app = FastAPI()
app.include_router(tasks.router)
app.include_router(users.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.on_event("startup")
async def startup_event():
    """Test Redis connection on startup"""
    try:
        await redis_client.set("health_check", "ok", expire=10)
        test_value = await redis_client.get("health_check")
        if test_value == "ok":
            print("✅ Redis connection successful")
        else:
            print("❌ Redis connection failed")
    except Exception as e:
        print(f"❌ Redis connection error: {e}")


@app.get("/health/redis")
async def redis_health():
    """Check Redis connection health"""
    try:
        await redis_client.set("health_test", "working", expire=5)
        result = await redis_client.get("health_test")
        return {"redis_status": "healthy" if result == "working" else "unhealthy"}
    except Exception as e:
        return {"redis_status": "unhealthy", "error": str(e)}
