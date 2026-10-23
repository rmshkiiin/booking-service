class AppError(Exception):
    """Базовая ошибка бизнес-логики. В main.py превращается в JSON-ответ."""

    status_code = 400

    def __init__(self, detail: str) -> None:
        super().__init__(detail)
        self.detail = detail


class NotFoundError(AppError):
    status_code = 404


class ConflictError(AppError):
    status_code = 409


class InvalidInputError(AppError):
    status_code = 422
