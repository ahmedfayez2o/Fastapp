from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from app.models.orders import (
    TransactionType,
    TransactionStatus,
    DeliveryMethod,
    OrderStatus
)

# Transaction Schemas
class TransactionItemBase(BaseModel):
    book_id: int
    quantity: int = Field(..., gt=0)
    unit_price: Decimal = Field(..., ge=0)
    borrow_duration_days: Optional[int] = Field(None, gt=0)

class TransactionItemCreate(TransactionItemBase):
    pass

class TransactionItem(TransactionItemBase):
    item_id: int
    transaction_id: int
    return_date: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class TransactionBase(BaseModel):
    transaction_type: TransactionType
    delivery_method: DeliveryMethod
    delivery_address: str
    notes: Optional[str] = None
    items: List[TransactionItemCreate]

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    status: Optional[TransactionStatus] = None
    estimated_delivery_time: Optional[datetime] = None
    actual_delivery_time: Optional[datetime] = None
    delivery_method: Optional[DeliveryMethod] = None
    delivery_address: Optional[str] = None
    notes: Optional[str] = None

class Transaction(TransactionBase):
    transaction_id: int
    user_id: int
    status: TransactionStatus
    total_amount: Decimal
    created_at: datetime
    updated_at: datetime
    estimated_delivery_time: Optional[datetime] = None
    actual_delivery_time: Optional[datetime] = None
    items: List[TransactionItem]

    class Config:
        from_attributes = True

# Order Schemas
class OrderBase(BaseModel):
    book_id: int

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    is_borrowed: Optional[bool] = None
    is_purchased: Optional[bool] = None
    return_date: Optional[datetime] = None

class Order(OrderBase):
    id: int
    user_id: int
    date_ordered: datetime
    status: OrderStatus
    is_borrowed: bool
    is_purchased: bool
    borrow_date: Optional[datetime] = None
    return_due_date: Optional[datetime] = None
    return_date: Optional[datetime] = None
    purchase_date: Optional[datetime] = None

    class Config:
        from_attributes = True

# Response Schemas
class OrderResponse(Order):
    book_details: Dict[str, Any]
    user_details: Dict[str, Any]

class TransactionResponse(Transaction):
    user_details: Dict[str, Any]
    book_details: List[Dict[str, Any]]

# Request Schemas
class BorrowRequest(BaseModel):
    borrow_duration_days: int = Field(14, gt=0, le=30)  # Default 2 weeks, max 30 days

class PurchaseRequest(BaseModel):
    delivery_method: DeliveryMethod
    delivery_address: str
    notes: Optional[str] = None

# Statistics Schemas
class OrderStats(BaseModel):
    total_orders: int
    active_borrows: int
    completed_purchases: int
    overdue_books: int
    total_revenue: Decimal

class TransactionStats(BaseModel):
    total_transactions: int
    total_revenue: Decimal
    average_order_value: Decimal
    most_popular_books: List[Dict[str, Any]]
    recent_transactions: List[Transaction] 