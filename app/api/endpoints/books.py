from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.crud import books as crud
from app.schemas.books import Book, BookCreate, BookUpdate, Category, CategoryCreate

router = APIRouter()

@router.get("/books/", response_model=List[Book])
def read_books(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    category_id: Optional[int] = None
):
    """
    Retrieve books with optional filtering by search term and category.
    """
    return crud.get_books(db, skip=skip, limit=limit, search=search, category_id=category_id)

@router.post("/books/", response_model=Book)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    """
    Create a new book.
    """
    return crud.create_book(db=db, book=book)

@router.get("/books/{book_id}", response_model=Book)
def read_book(book_id: int, db: Session = Depends(get_db)):
    """
    Get a specific book by ID.
    """
    db_book = crud.get_book(db, book_id=book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book

@router.put("/books/{book_id}", response_model=Book)
def update_book(book_id: int, book: BookUpdate, db: Session = Depends(get_db)):
    """
    Update a book.
    """
    db_book = crud.update_book(db, book_id=book_id, book=book)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book

@router.delete("/books/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    """
    Delete a book.
    """
    success = crud.delete_book(db, book_id=book_id)
    if not success:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"message": "Book deleted successfully"}

# Category endpoints
@router.get("/categories/", response_model=List[Category])
def read_categories(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    parent_id: Optional[int] = None
):
    """
    Retrieve categories with optional filtering by parent category.
    """
    return crud.get_categories(db, skip=skip, limit=limit, parent_id=parent_id)

@router.post("/categories/", response_model=Category)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """
    Create a new category.
    """
    return crud.create_category(db=db, category=category)

@router.get("/categories/{category_id}", response_model=Category)
def read_category(category_id: int, db: Session = Depends(get_db)):
    """
    Get a specific category by ID.
    """
    db_category = crud.get_category(db, category_id=category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category

@router.get("/categories/{category_id}/books", response_model=List[Book])
def read_category_books(category_id: int, db: Session = Depends(get_db)):
    """
    Get all books in a specific category.
    """
    db_category = crud.get_category(db, category_id=category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return crud.get_category_books(db, category_id=category_id) 