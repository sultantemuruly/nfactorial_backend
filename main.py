from fastapi import FastAPI
from api.users import users
from api.books import books

app = FastAPI()
app.include_router(books.router)
app.include_router(users.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
