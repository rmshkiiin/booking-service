from datetime import datetime

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user, require_admin
from app.errors import InvalidInputError, NotFoundError
from app.models import Booking, Resource, User
from app.schemas import ResourceCreate, ResourceOut, ResourceUpdate
from app.timeutils import to_naive_utc

router = APIRouter(prefix="/resources", tags=["resources"])


@router.get("", response_model=list[ResourceOut])
def list_resources(
    min_capacity: int | None = Query(None, ge=1),
    free_from: datetime | None = None,
    free_to: datetime | None = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """Список активных ресурсов. Фильтры: вместимость и свободность в интервале."""
    stmt = select(Resource).where(Resource.is_active.is_(True))
    if min_capacity is not None:
        stmt = stmt.where(Resource.capacity >= min_capacity)

    if (free_from is None) != (free_to is None):
        raise InvalidInputError("Укажите free_from и free_to вместе")
    if free_from is not None and free_to is not None:
        start, end = to_naive_utc(free_from), to_naive_utc(free_to)
        if start >= end:
            raise InvalidInputError("free_from должно быть раньше free_to")
        busy = select(Booking.resource_id).where(
            Booking.status == "active",
            Booking.start_time < end,
            Booking.end_time > start,
        )
        stmt = stmt.where(Resource.id.not_in(busy))

    stmt = stmt.order_by(Resource.id).limit(limit).offset(offset)
    return db.scalars(stmt).all()


@router.post("", response_model=ResourceOut, status_code=status.HTTP_201_CREATED)
def create_resource(
    data: ResourceCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    resource = Resource(**data.model_dump())
    db.add(resource)
    db.commit()
    db.refresh(resource)
    return resource


@router.patch("/{resource_id}", response_model=ResourceOut)
def update_resource(
    resource_id: int,
    data: ResourceUpdate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    resource = db.get(Resource, resource_id)
    if resource is None:
        raise NotFoundError("Ресурс не найден")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(resource, field, value)
    db.commit()
    db.refresh(resource)
    return resource


@router.delete("/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resource(
    resource_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    """«Мягкое» удаление: ресурс скрывается, а история броней остаётся."""
    resource = db.get(Resource, resource_id)
    if resource is None:
        raise NotFoundError("Ресурс не найден")
    resource.is_active = False
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
