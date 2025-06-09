from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.models import Books
from db.dependencies import get_db
from schemas.book_schemas import BookCreate, BookUpdate, BookOut

router = APIRouter(prefix="/books", tags=["Books"])


@router.post("/", response_model=BookOut)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    db_book = Books(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


@router.get("/", response_model=BookOut)
def read_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Books).filter(Books.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.put("/{book_id}", response_model=BookOut)
def update_book(book_id: int, book_data: BookUpdate, db: Session = Depends(get_db)):
    book = db.query(Books).filter(Books.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    for key, value in book_data.dict().items():
        setattr(book, key, value)
    db.commit()
    db.refresh(book)
    return book


@router.delete("/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Books).filter(Books.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(book)
    db.commit()
    return {"detail": "Book deleted successfully"}
