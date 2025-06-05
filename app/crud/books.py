from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from app.models.books import Book, Category
from app.schemas.books import BookCreate, BookUpdate, CategoryCreate

def get_book(db: Session, book_id: int) -> Optional[Book]:
    return db.query(Book).filter(Book.book_id == book_id).first()

def get_books(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    category_id: Optional[int] = None
) -> List[Book]:
    query = db.query(Book)
    
    if search:
        search_filter = or_(
            Book.title.ilike(f"%{search}%"),
            Book.author.ilike(f"%{search}%"),
            Book.isbn.ilike(f"%{search}%"),
            Book.publisher.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    if category_id:
        query = query.filter(Book.categories.any(Category.id == category_id))
    
    return query.offset(skip).limit(limit).all()

def create_book(db: Session, book: BookCreate) -> Book:
    db_book = Book(
        isbn=book.isbn,
        title=book.title,
        author=book.author,
        publisher=book.publisher,
        publication_year=book.publication_year,
        price=book.price,
        stock_quantity=book.stock_quantity,
        available_for_borrow=book.available_for_borrow,
        description=book.description
    )
    
    if book.category_ids:
        categories = db.query(Category).filter(Category.id.in_(book.category_ids)).all()
        db_book.categories = categories
    
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

def update_book(db: Session, book_id: int, book: BookUpdate) -> Optional[Book]:
    db_book = get_book(db, book_id)
    if not db_book:
        return None
    
    update_data = book.model_dump(exclude_unset=True)
    category_ids = update_data.pop('category_ids', None)
    
    for field, value in update_data.items():
        setattr(db_book, field, value)
    
    if category_ids is not None:
        categories = db.query(Category).filter(Category.id.in_(category_ids)).all()
        db_book.categories = categories
    
    db.commit()
    db.refresh(db_book)
    return db_book

def delete_book(db: Session, book_id: int) -> bool:
    db_book = get_book(db, book_id)
    if not db_book:
        return False
    
    db.delete(db_book)
    db.commit()
    return True

# Category CRUD operations
def get_category(db: Session, category_id: int) -> Optional[Category]:
    return db.query(Category).filter(Category.id == category_id).first()

def get_categories(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    parent_id: Optional[int] = None
) -> List[Category]:
    query = db.query(Category)
    if parent_id is not None:
        query = query.filter(Category.parent_id == parent_id)
    return query.offset(skip).limit(limit).all()

def create_category(db: Session, category: CategoryCreate) -> Category:
    db_category = Category(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def get_category_books(db: Session, category_id: int) -> List[Book]:
    category = get_category(db, category_id)
    if not category:
        return []
    return category.books 