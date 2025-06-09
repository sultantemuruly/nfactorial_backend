from fastapi import FastAPI
from api.users import users
from api.tasks import tasks

app = FastAPI()
app.include_router(tasks.router)
app.include_router(users.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
