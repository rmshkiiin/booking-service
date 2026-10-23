from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_admin
from app.models import Booking, User
from app.schemas import AdminBookingsOut, BookingStats

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/bookings", response_model=AdminBookingsOut)
def all_bookings(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    """Все брони со статистикой. Только для администратора."""
    rows = db.execute(select(Booking.status, func.count()).group_by(Booking.status)).all()
    counts = {status_name: count for status_name, count in rows}
    stats = BookingStats(
        total=sum(counts.values()),
        active=counts.get("active", 0),
        cancelled=counts.get("cancelled", 0),
    )
    bookings = db.scalars(
        select(Booking).order_by(Booking.start_time).limit(limit).offset(offset)
    ).all()
    return AdminBookingsOut(stats=stats, bookings=bookings)
