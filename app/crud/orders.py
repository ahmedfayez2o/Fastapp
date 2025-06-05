from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_
from fastapi import HTTPException
from decimal import Decimal

from app.models.orders import Transaction, TransactionItem, Order, OrderStatus, TransactionStatus
from app.models.books import Book
from app.models.users import User
from app.schemas.orders import (
    TransactionCreate,
    TransactionUpdate,
    OrderCreate,
    OrderUpdate,
    BorrowRequest,
    PurchaseRequest
)

# Transaction CRUD operations
def get_transaction(db: Session, transaction_id: int) -> Optional[Transaction]:
    return db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()

def get_user_transactions(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    status: Optional[TransactionStatus] = None
) -> List[Transaction]:
    query = db.query(Transaction).filter(Transaction.user_id == user_id)
    if status:
        query = query.filter(Transaction.status == status)
    return query.order_by(desc(Transaction.created_at)).offset(skip).limit(limit).all()

def create_transaction(
    db: Session,
    user_id: int,
    transaction: TransactionCreate
) -> Transaction:
    # Calculate total amount
    total_amount = Decimal('0')
    for item in transaction.items:
        book = db.query(Book).filter(Book.book_id == item.book_id).first()
        if not book:
            raise HTTPException(status_code=404, detail=f"Book {item.book_id} not found")
        if book.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"Not enough stock for book {book.title}")
        total_amount += item.unit_price * item.quantity

    # Create transaction
    db_transaction = Transaction(
        user_id=user_id,
        transaction_type=transaction.transaction_type,
        status=TransactionStatus.PENDING,
        total_amount=total_amount,
        delivery_method=transaction.delivery_method,
        delivery_address=transaction.delivery_address,
        notes=transaction.notes
    )
    db.add(db_transaction)
    db.flush()

    # Create transaction items
    for item in transaction.items:
        db_item = TransactionItem(
            transaction_id=db_transaction.transaction_id,
            book_id=item.book_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
            borrow_duration_days=item.borrow_duration_days
        )
        db.add(db_item)
        
        # Update book stock
        book = db.query(Book).filter(Book.book_id == item.book_id).first()
        book.stock -= item.quantity

    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def update_transaction(
    db: Session,
    transaction_id: int,
    transaction: TransactionUpdate
) -> Optional[Transaction]:
    db_transaction = get_transaction(db, transaction_id)
    if not db_transaction:
        return None

    update_data = transaction.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_transaction, field, value)

    db.commit()
    db.refresh(db_transaction)
    return db_transaction

# Order CRUD operations
def get_order(db: Session, order_id: int) -> Optional[Order]:
    return db.query(Order).filter(Order.id == order_id).first()

def get_user_orders(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    status: Optional[OrderStatus] = None
) -> List[Order]:
    query = db.query(Order).filter(Order.user_id == user_id)
    if status:
        query = query.filter(Order.status == status)
    return query.order_by(desc(Order.date_ordered)).offset(skip).limit(limit).all()

def create_order(
    db: Session,
    user_id: int,
    order: OrderCreate
) -> Order:
    # Check book availability
    book = db.query(Book).filter(Book.book_id == order.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if book.stock <= 0:
        raise HTTPException(status_code=400, detail="Book is out of stock")

    db_order = Order(
        user_id=user_id,
        book_id=order.book_id,
        status=OrderStatus.PENDING
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

def update_order(
    db: Session,
    order_id: int,
    order: OrderUpdate
) -> Optional[Order]:
    db_order = get_order(db, order_id)
    if not db_order:
        return None

    update_data = order.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_order, field, value)

    db.commit()
    db.refresh(db_order)
    return db_order

def borrow_book(
    db: Session,
    order_id: int,
    borrow_request: BorrowRequest
) -> Order:
    order = get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status != OrderStatus.PENDING:
        raise HTTPException(status_code=400, detail=f"Cannot borrow book in {order.status} status")

    book = db.query(Book).filter(Book.book_id == order.book_id).first()
    if book.stock <= 0:
        raise HTTPException(status_code=400, detail="Book is out of stock")

    # Update book stock
    book.stock -= 1

    # Update order
    order.status = OrderStatus.BORROWED
    order.is_borrowed = True
    order.borrow_date = datetime.utcnow()
    order.return_due_date = datetime.utcnow() + timedelta(days=borrow_request.borrow_duration_days)

    db.commit()
    db.refresh(order)
    return order

def purchase_book(
    db: Session,
    order_id: int,
    purchase_request: PurchaseRequest
) -> Order:
    order = get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status not in [OrderStatus.PENDING, OrderStatus.BORROWED]:
        raise HTTPException(status_code=400, detail=f"Cannot purchase book in {order.status} status")

    if order.status == OrderStatus.PENDING:
        book = db.query(Book).filter(Book.book_id == order.book_id).first()
        if book.stock <= 0:
            raise HTTPException(status_code=400, detail="Book is out of stock")
        book.stock -= 1

    # Create transaction
    transaction = create_transaction(
        db=db,
        user_id=order.user_id,
        transaction=TransactionCreate(
            transaction_type="buy",
            delivery_method=purchase_request.delivery_method,
            delivery_address=purchase_request.delivery_address,
            notes=purchase_request.notes,
            items=[{
                "book_id": order.book_id,
                "quantity": 1,
                "unit_price": book.price
            }]
        )
    )

    # Update order
    order.status = OrderStatus.PURCHASED
    order.is_purchased = True
    order.purchase_date = datetime.utcnow()

    db.commit()
    db.refresh(order)
    return order

def return_book(db: Session, order_id: int) -> Order:
    order = get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if not order.is_borrowed or order.status != OrderStatus.BORROWED:
        raise HTTPException(status_code=400, detail="This book is not borrowed")

    # Update book stock
    book = db.query(Book).filter(Book.book_id == order.book_id).first()
    book.stock += 1

    # Update order
    order.status = OrderStatus.RETURNED
    order.is_borrowed = False
    order.return_date = datetime.utcnow()

    db.commit()
    db.refresh(order)
    return order

def cancel_order(db: Session, order_id: int) -> Order:
    order = get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status != OrderStatus.PENDING:
        raise HTTPException(status_code=400, detail=f"Cannot cancel order in {order.status} status")

    order.status = OrderStatus.CANCELLED
    db.commit()
    db.refresh(order)
    return order

def get_overdue_orders(db: Session, user_id: Optional[int] = None) -> List[Order]:
    query = db.query(Order).filter(
        and_(
            Order.status == OrderStatus.BORROWED,
            Order.return_due_date < datetime.utcnow()
        )
    )
    if user_id:
        query = query.filter(Order.user_id == user_id)
    return query.all()

def get_order_stats(db: Session, user_id: Optional[int] = None) -> Dict[str, Any]:
    query = db.query(Order)
    if user_id:
        query = query.filter(Order.user_id == user_id)

    total_orders = query.count()
    active_borrows = query.filter(Order.status == OrderStatus.BORROWED).count()
    completed_purchases = query.filter(Order.status == OrderStatus.PURCHASED).count()
    overdue_books = get_overdue_orders(db, user_id).count()

    # Calculate total revenue from transactions
    revenue_query = db.query(func.sum(Transaction.total_amount)).filter(
        Transaction.status == TransactionStatus.DELIVERED
    )
    if user_id:
        revenue_query = revenue_query.filter(Transaction.user_id == user_id)
    total_revenue = revenue_query.scalar() or Decimal('0')

    return {
        "total_orders": total_orders,
        "active_borrows": active_borrows,
        "completed_purchases": completed_purchases,
        "overdue_books": overdue_books,
        "total_revenue": total_revenue
    }

def get_transaction_stats(db: Session, user_id: Optional[int] = None) -> Dict[str, Any]:
    query = db.query(Transaction)
    if user_id:
        query = query.filter(Transaction.user_id == user_id)

    total_transactions = query.count()
    total_revenue = query.filter(
        Transaction.status == TransactionStatus.DELIVERED
    ).with_entities(func.sum(Transaction.total_amount)).scalar() or Decimal('0')

    # Calculate average order value
    avg_order_value = total_revenue / total_transactions if total_transactions > 0 else Decimal('0')

    # Get most popular books
    popular_books = db.query(
        TransactionItem.book_id,
        func.sum(TransactionItem.quantity).label('total_quantity')
    ).join(Transaction).filter(
        Transaction.status == TransactionStatus.DELIVERED
    ).group_by(
        TransactionItem.book_id
    ).order_by(
        desc('total_quantity')
    ).limit(5).all()

    # Get recent transactions
    recent_transactions = query.order_by(
        desc(Transaction.created_at)
    ).limit(5).all()

    return {
        "total_transactions": total_transactions,
        "total_revenue": total_revenue,
        "average_order_value": avg_order_value,
        "most_popular_books": [
            {
                "book_id": book_id,
                "total_quantity": quantity
            }
            for book_id, quantity in popular_books
        ],
        "recent_transactions": recent_transactions
    } 