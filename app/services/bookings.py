import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.errors import ConflictError, InvalidInputError, NotFoundError
from app.models import Booking, Resource, User
from app.timeutils import utcnow

logger = logging.getLogger(__name__)


def create_booking(db: Session, user: User, resource_id: int, start, end) -> Booking:
    """Создаёт бронь, если ресурс свободен на весь интервал [start, end)."""
    if start < utcnow():
        raise InvalidInputError("Нельзя бронировать в прошлом")

    # Блокируем строку ресурса до конца транзакции. Если два пользователя бронируют
    # один ресурс одновременно, второй запрос подождёт, пока первый закончит.
    # (SQLite этот запрос игнорирует, в PostgreSQL блокировка работает.)
    resource = db.scalar(
        select(Resource)
        .where(Resource.id == resource_id, Resource.is_active.is_(True))
        .with_for_update()
    )
    if resource is None:
        raise NotFoundError("Ресурс не найден")

    # Два интервала пересекаются, если начало одного раньше конца другого и наоборот.
    # Бронь «10:00-11:00» и бронь «11:00-12:00» не пересекаются.
    conflict = db.scalar(
        select(Booking.id)
        .where(
            Booking.resource_id == resource_id,
            Booking.status == "active",
            Booking.start_time < end,
            Booking.end_time > start,
        )
        .limit(1)
    )
    if conflict is not None:
        logger.info("Конфликт брони: resource=%s user=%s", resource_id, user.id)
        raise ConflictError("Время уже занято")

    booking = Booking(resource_id=resource_id, user_id=user.id, start_time=start, end_time=end)
    db.add(booking)
    db.commit()
    db.refresh(booking)
    logger.info("Бронь создана: id=%s resource=%s user=%s", booking.id, resource_id, user.id)
    return booking


def cancel_booking(db: Session, user: User, booking_id: int) -> None:
    """Отменяет бронь. Чужая бронь для пользователя выглядит как несуществующая."""
    booking = db.scalar(select(Booking).where(Booking.id == booking_id, Booking.user_id == user.id))
    if booking is None:
        raise NotFoundError("Бронь не найдена")
    if booking.status != "cancelled":
        booking.status = "cancelled"
        db.commit()
        logger.info("Бронь отменена: id=%s user=%s", booking_id, user.id)
