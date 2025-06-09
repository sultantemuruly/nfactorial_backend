from sqlalchemy import Column, Integer, String
from .database import Base


class Books(Base):
    __tablename__ = "Books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, index=True)
    description = Column(String)
