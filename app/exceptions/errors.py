from typing import ClassVar


class AppError(Exception):
    status_code: ClassVar[int] = 500
    code: ClassVar[str] = "internal_error"
    title: ClassVar[str] = "Internal Server Error"

    def __init__(self, detail: str | None = None):
        self.detail = detail if detail is not None else self.title
        super().__init__(self.detail)


class NotFoundError(AppError):
    status_code = 404
    code = "not_found"
    title = "Not Found"


class AuthenticationError(AppError):
    status_code = 401
    code = "unauthorized"
    title = "Unauthorized"


class AuthorizationError(AppError):
    status_code = 403
    code = "forbidden"
    title = "Forbidden"


class ConflictError(AppError):
    status_code = 409
    code = "conflict"
    title = "Conflict"


class AppValidationError(AppError):
    status_code = 422
    code = "validation_error"
    title = "Unprocessable Entity"


class BusinessError(AppError):
    status_code = 400
    code = "business_error"
    title = "Bad Request"
