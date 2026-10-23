import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app import models  # noqa: F401  (нужно, чтобы таблицы попали в Base.metadata)
from app.database import Base, engine
from app.errors import AppError
from app.routers import admin, auth, bookings, resources

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Для простого старта таблицы создаются автоматически.
    # В реальном проекте вместо этого используются миграции Alembic (см. README).
    Base.metadata.create_all(engine)
    yield


app = FastAPI(title="Сервис бронирования", version="0.1.0", lifespan=lifespan)

app.include_router(auth.router)
app.include_router(resources.router)
app.include_router(bookings.router)
app.include_router(admin.router)


@app.exception_handler(AppError)
async def app_error_handler(_request: Request, exc: AppError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.get("/health", tags=["service"])
def health():
    return {"status": "ok"}
