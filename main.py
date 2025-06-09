from fastapi import FastAPI
from api.books import books

app = FastAPI()
app.include_router(books.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
