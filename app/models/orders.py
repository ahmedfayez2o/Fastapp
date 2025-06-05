from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Numeric, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class TransactionType(str, enum.Enum):
    BORROW = "borrow"
    BUY = "buy"

class TransactionStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    RETURNED = "returned"
    CANCELLED = "cancelled"

class DeliveryMethod(str, enum.Enum):
    STANDARD_SHIPPING = "standard_shipping"
    EXPRESS_SHIPPING = "express_shipping"
    PICKUP = "pickup"
    LOCAL_DELIVERY = "local_delivery"

class OrderStatus(str, enum.Enum):
    PENDING = "PENDING"
    BORROWED = "BORROWED"
    PURCHASED = "PURCHASED"
    RETURNED = "RETURNED"
    CANCELLED = "CANCELLED"

class Transaction(Base):
    """Represents a transaction (borrow or purchase) of books."""
    __tablename__ = "transactions"

    transaction_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    transaction_type = Column(Enum(TransactionType))
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING)
    total_amount = Column(Numeric(10, 2))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    estimated_delivery_time = Column(DateTime(timezone=True), nullable=True)
    actual_delivery_time = Column(DateTime(timezone=True), nullable=True)
    delivery_method = Column(Enum(DeliveryMethod))
    delivery_address = Column(Text)
    notes = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="transactions")
    items = relationship("TransactionItem", back_populates="transaction", cascade="all, delete-orphan")

class TransactionItem(Base):
    """Represents an item in a transaction."""
    __tablename__ = "transaction_items"

    item_id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.transaction_id", ondelete="CASCADE"))
    book_id = Column(Integer, ForeignKey("books.book_id", ondelete="CASCADE"))
    quantity = Column(Integer)
    unit_price = Column(Numeric(10, 2))
    borrow_duration_days = Column(Integer, nullable=True)
    return_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    transaction = relationship("Transaction", back_populates="items")
    book = relationship("Book", back_populates="transaction_items")

class Order(Base):
    """Represents a book order (borrow or purchase)."""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    book_id = Column(Integer, ForeignKey("books.book_id", ondelete="CASCADE"))
    date_ordered = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    is_borrowed = Column(Boolean, default=False)
    is_purchased = Column(Boolean, default=False)
    borrow_date = Column(DateTime(timezone=True), nullable=True)
    return_due_date = Column(DateTime(timezone=True), nullable=True)
    return_date = Column(DateTime(timezone=True), nullable=True)
    purchase_date = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="orders")
    book = relationship("Book", back_populates="orders")

    __table_args__ = (
        # Add any table constraints here
        {'sqlite_autoincrement': True},
    ) 