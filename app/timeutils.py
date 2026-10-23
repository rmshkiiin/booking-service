from datetime import datetime, timezone


def utcnow() -> datetime:
    """Текущее время в UTC без tzinfo. Все даты в базе хранятся как UTC."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def to_naive_utc(value: datetime) -> datetime:
    """Приводит время к UTC. Время без часового пояса считается UTC."""
    if value.tzinfo is not None:
        value = value.astimezone(timezone.utc).replace(tzinfo=None)
    return value
