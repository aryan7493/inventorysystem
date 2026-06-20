from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas, services
from app.database import get_db

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("", response_model=list[schemas.CustomerRead])
def list_customers(db: Session = Depends(get_db)) -> list[models.Customer]:
    return list(db.scalars(select(models.Customer).order_by(models.Customer.name)))


@router.post("", response_model=schemas.CustomerRead, status_code=status.HTTP_201_CREATED)
def create_customer(payload: schemas.CustomerCreate, db: Session = Depends(get_db)) -> models.Customer:
    return services.create_customer(db, payload)


@router.get("/{customer_id}", response_model=schemas.CustomerRead)
def get_customer(customer_id: int, db: Session = Depends(get_db)) -> models.Customer:
    customer = db.get(models.Customer, customer_id)
    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found.")
    return customer


@router.patch("/{customer_id}", response_model=schemas.CustomerRead)
def update_customer(
    customer_id: int, payload: schemas.CustomerUpdate, db: Session = Depends(get_db)
) -> models.Customer:
    customer = db.get(models.Customer, customer_id)
    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found.")
    return services.update_customer(db, customer, payload)


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(customer_id: int, db: Session = Depends(get_db)) -> Response:
    customer = db.get(models.Customer, customer_id)
    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found.")
    db.delete(customer)
    services.commit_or_409(db, "Customer cannot be deleted because they have orders.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

