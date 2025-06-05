from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Numeric, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

# Association table for many-to-many relationship between books and categories
book_category = Table(
    'book_category',
    Base.metadata,
    Column('book_id', Integer, ForeignKey('books.book_id')),
    Column('category_id', Integer, ForeignKey('categories.id'))
)

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)
    description = Column(Text, nullable=True)
    parent_id = Column(Integer, ForeignKey('categories.id'), nullable=True)

    # Relationships
    parent = relationship("Category", remote_side=[id], backref="subcategories")
    books = relationship("Book", secondary=book_category, back_populates="categories")

class Book(Base):
    __tablename__ = "books"

    book_id = Column(Integer, primary_key=True, index=True)
    isbn = Column(String(13), unique=True, nullable=True)
    title = Column(String(255), index=True)
    author = Column(String(100))
    publisher = Column(String(100), nullable=True)
    publication_year = Column(Integer, nullable=True)
    price = Column(Numeric(10, 2))
    stock_quantity = Column(Integer, default=0)
    available_for_borrow = Column(Boolean, default=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    categories = relationship("Category", secondary=book_category, back_populates="books") 