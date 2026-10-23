from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

from app.timeutils import to_naive_utc


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    role: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ResourceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str = Field("", max_length=500)
    capacity: int = Field(ge=1)


class ResourceUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    capacity: int | None = Field(None, ge=1)
    is_active: bool | None = None


class ResourceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    capacity: int
    is_active: bool


class BookingCreate(BaseModel):
    resource_id: int
    start_time: datetime
    end_time: datetime

    @field_validator("start_time", "end_time")
    @classmethod
    def _to_utc(cls, value: datetime) -> datetime:
        return to_naive_utc(value)

    @model_validator(mode="after")
    def _check_order(self) -> "BookingCreate":
        if self.start_time >= self.end_time:
            raise ValueError("Начало брони должно быть раньше конца")
        return self


class BookingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    resource_id: int
    user_id: int
    start_time: datetime
    end_time: datetime
    status: str
    created_at: datetime


class BookingStats(BaseModel):
    total: int
    active: int
    cancelled: int


class AdminBookingsOut(BaseModel):
    stats: BookingStats
    bookings: list[BookingOut]
