from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import Booking, User
from app.schemas import BookingCreate, BookingOut
from app.services import bookings as booking_service

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post("", response_model=BookingOut, status_code=status.HTTP_201_CREATED)
def create_booking(
    data: BookingCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return booking_service.create_booking(db, user, data.resource_id, data.start_time, data.end_time)


@router.get("", response_model=list[BookingOut])
def my_bookings(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    stmt = select(Booking).where(Booking.user_id == user.id).order_by(Booking.start_time)
    return db.scalars(stmt).all()


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    booking_service.cancel_booking(db, user, booking_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
