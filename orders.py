from collections import defaultdict
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app import models, schemas


def commit_or_409(db: Session, duplicate_message: str) -> None:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=duplicate_message) from exc


def create_product(db: Session, payload: schemas.ProductCreate) -> models.Product:
    product = models.Product(**payload.model_dump())
    db.add(product)
    commit_or_409(db, "Product SKU already exists.")
    db.refresh(product)
    return product


def update_product(db: Session, product: models.Product, payload: schemas.ProductUpdate) -> models.Product:
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(product, key, value)
    commit_or_409(db, "Product SKU already exists.")
    db.refresh(product)
    return product


def create_customer(db: Session, payload: schemas.CustomerCreate) -> models.Customer:
    customer = models.Customer(**payload.model_dump())
    db.add(customer)
    commit_or_409(db, "Customer email already exists.")
    db.refresh(customer)
    return customer


def update_customer(db: Session, customer: models.Customer, payload: schemas.CustomerUpdate) -> models.Customer:
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(customer, key, value)
    commit_or_409(db, "Customer email already exists.")
    db.refresh(customer)
    return customer


def create_order(db: Session, payload: schemas.OrderCreate) -> models.Order:
    customer = db.get(models.Customer, payload.customer_id)
    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found.")

    requested_quantities: dict[int, int] = defaultdict(int)
    for item in payload.items:
        requested_quantities[item.product_id] += item.quantity

    product_ids = list(requested_quantities)
    product_rows = db.scalars(
        select(models.Product).where(models.Product.id.in_(product_ids)).with_for_update()
    ).all()
    products = {product.id: product for product in product_rows}

    missing_ids = [product_id for product_id in product_ids if product_id not in products]
    if missing_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Products not found: {', '.join(map(str, missing_ids))}.",
        )

    for product_id, requested_quantity in requested_quantities.items():
        product = products[product_id]
        if product.stock_quantity < requested_quantity:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Insufficient stock for SKU {product.sku}: "
                    f"requested {requested_quantity}, available {product.stock_quantity}."
                ),
            )

    order = models.Order(customer_id=customer.id, status="placed", total_amount=Decimal("0.00"))
    db.add(order)
    db.flush()

    total = Decimal("0.00")
    for product_id, requested_quantity in requested_quantities.items():
        product = products[product_id]
        line_total = product.price * requested_quantity
        product.stock_quantity -= requested_quantity
        db.add(
            models.OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=requested_quantity,
                unit_price=product.price,
                line_total=line_total,
            )
        )
        total += line_total

    order.total_amount = total
    db.commit()

    return get_order_or_404(db, order.id)


def get_order_or_404(db: Session, order_id: int) -> models.Order:
    order = db.scalar(
        select(models.Order)
        .where(models.Order.id == order_id)
        .options(
            selectinload(models.Order.customer),
            selectinload(models.Order.items).selectinload(models.OrderItem.product),
        )
    )
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")
    return order

