from pydantic import BaseModel


class BookBase(BaseModel):
    title: str
    description: str


class BookCreate(BookBase):
    pass


class BookUpdate(BookBase):
    pass


class BookOut(BookBase):
    id: int

    class Config:
        orm_mode = True
