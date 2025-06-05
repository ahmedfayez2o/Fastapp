from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import orders as crud_orders
from app.schemas.orders import (
    Order,
    OrderCreate,
    OrderUpdate,
    Transaction,
    TransactionCreate,
    TransactionUpdate,
    BorrowRequest,
    PurchaseRequest,
    OrderStats,
    TransactionStats
)
from app.models.orders import OrderStatus, TransactionStatus

router = APIRouter()

# Order endpoints
@router.post("/", response_model=Order)
def create_order(
    *,
    db: Session = Depends(deps.get_db),
    order_in: OrderCreate,
    current_user = Depends(deps.get_current_user)
) -> Order:
    """
    Create new order.
    """
    return crud_orders.create_order(db=db, user_id=current_user.id, order=order_in)

@router.get("/", response_model=List[Order])
def read_orders(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[OrderStatus] = None,
    current_user = Depends(deps.get_current_user)
) -> List[Order]:
    """
    Retrieve orders.
    """
    return crud_orders.get_user_orders(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        status=status
    )

@router.get("/{order_id}", response_model=Order)
def read_order(
    *,
    db: Session = Depends(deps.get_db),
    order_id: int,
    current_user = Depends(deps.get_current_user)
) -> Order:
    """
    Get order by ID.
    """
    order = crud_orders.get_order(db=db, order_id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return order

@router.put("/{order_id}", response_model=Order)
def update_order(
    *,
    db: Session = Depends(deps.get_db),
    order_id: int,
    order_in: OrderUpdate,
    current_user = Depends(deps.get_current_user)
) -> Order:
    """
    Update an order.
    """
    order = crud_orders.get_order(db=db, order_id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return crud_orders.update_order(db=db, order_id=order_id, order=order_in)

@router.post("/{order_id}/borrow", response_model=Order)
def borrow_book(
    *,
    db: Session = Depends(deps.get_db),
    order_id: int,
    borrow_request: BorrowRequest,
    current_user = Depends(deps.get_current_user)
) -> Order:
    """
    Borrow a book.
    """
    order = crud_orders.get_order(db=db, order_id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return crud_orders.borrow_book(db=db, order_id=order_id, borrow_request=borrow_request)

@router.post("/{order_id}/purchase", response_model=Order)
def purchase_book(
    *,
    db: Session = Depends(deps.get_db),
    order_id: int,
    purchase_request: PurchaseRequest,
    current_user = Depends(deps.get_current_user)
) -> Order:
    """
    Purchase a book.
    """
    order = crud_orders.get_order(db=db, order_id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return crud_orders.purchase_book(db=db, order_id=order_id, purchase_request=purchase_request)

@router.post("/{order_id}/return", response_model=Order)
def return_book(
    *,
    db: Session = Depends(deps.get_db),
    order_id: int,
    current_user = Depends(deps.get_current_user)
) -> Order:
    """
    Return a borrowed book.
    """
    order = crud_orders.get_order(db=db, order_id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return crud_orders.return_book(db=db, order_id=order_id)

@router.post("/{order_id}/cancel", response_model=Order)
def cancel_order(
    *,
    db: Session = Depends(deps.get_db),
    order_id: int,
    current_user = Depends(deps.get_current_user)
) -> Order:
    """
    Cancel an order.
    """
    order = crud_orders.get_order(db=db, order_id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return crud_orders.cancel_order(db=db, order_id=order_id)

# Transaction endpoints
@router.post("/transactions/", response_model=Transaction)
def create_transaction(
    *,
    db: Session = Depends(deps.get_db),
    transaction_in: TransactionCreate,
    current_user = Depends(deps.get_current_user)
) -> Transaction:
    """
    Create new transaction.
    """
    return crud_orders.create_transaction(db=db, user_id=current_user.id, transaction=transaction_in)

@router.get("/transactions/", response_model=List[Transaction])
def read_transactions(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[TransactionStatus] = None,
    current_user = Depends(deps.get_current_user)
) -> List[Transaction]:
    """
    Retrieve transactions.
    """
    return crud_orders.get_user_transactions(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        status=status
    )

@router.get("/transactions/{transaction_id}", response_model=Transaction)
def read_transaction(
    *,
    db: Session = Depends(deps.get_db),
    transaction_id: int,
    current_user = Depends(deps.get_current_user)
) -> Transaction:
    """
    Get transaction by ID.
    """
    transaction = crud_orders.get_transaction(db=db, transaction_id=transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    if transaction.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return transaction

@router.put("/transactions/{transaction_id}", response_model=Transaction)
def update_transaction(
    *,
    db: Session = Depends(deps.get_db),
    transaction_id: int,
    transaction_in: TransactionUpdate,
    current_user = Depends(deps.get_current_user)
) -> Transaction:
    """
    Update a transaction.
    """
    transaction = crud_orders.get_transaction(db=db, transaction_id=transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    if transaction.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return crud_orders.update_transaction(db=db, transaction_id=transaction_id, transaction=transaction_in)

# Statistics endpoints
@router.get("/stats/orders", response_model=OrderStats)
def get_order_statistics(
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user)
) -> OrderStats:
    """
    Get order statistics.
    """
    return crud_orders.get_order_stats(db=db, user_id=current_user.id)

@router.get("/stats/transactions", response_model=TransactionStats)
def get_transaction_statistics(
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user)
) -> TransactionStats:
    """
    Get transaction statistics.
    """
    return crud_orders.get_transaction_stats(db=db, user_id=current_user.id)

# Admin endpoints
@router.get("/admin/overdue", response_model=List[Order])
def get_overdue_orders(
    db: Session = Depends(deps.get_db),
    user_id: Optional[int] = None,
    current_user = Depends(deps.get_current_superuser)
) -> List[Order]:
    """
    Get overdue orders (admin only).
    """
    return crud_orders.get_overdue_orders(db=db, user_id=user_id)

@router.get("/admin/stats/orders", response_model=OrderStats)
def get_admin_order_statistics(
    db: Session = Depends(deps.get_db),
    user_id: Optional[int] = None,
    current_user = Depends(deps.get_current_superuser)
) -> OrderStats:
    """
    Get order statistics (admin only).
    """
    return crud_orders.get_order_stats(db=db, user_id=user_id)

@router.get("/admin/stats/transactions", response_model=TransactionStats)
def get_admin_transaction_statistics(
    db: Session = Depends(deps.get_db),
    user_id: Optional[int] = None,
    current_user = Depends(deps.get_current_superuser)
) -> TransactionStats:
    """
    Get transaction statistics (admin only).
    """
    return crud_orders.get_transaction_stats(db=db, user_id=user_id) 