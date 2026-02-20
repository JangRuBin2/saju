from fastapi import Request
from fastapi.responses import JSONResponse


class SajuError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class InvalidBirthDateError(SajuError):
    def __init__(self, message: str = "Invalid birth date"):
        super().__init__(message, status_code=422)


class LunarConversionError(SajuError):
    def __init__(self, message: str = "Failed to convert lunar date"):
        super().__init__(message, status_code=422)


class LeapMonthError(SajuError):
    def __init__(self, message: str = "Invalid leap month for the given date"):
        super().__init__(message, status_code=422)


class LLMError(SajuError):
    def __init__(self, message: str = "LLM interpretation failed"):
        super().__init__(message, status_code=502)


async def saju_error_handler(_request: Request, exc: SajuError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": type(exc).__name__, "message": exc.message},
    )


async def generic_error_handler(_request: Request, _exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"error": "InternalServerError", "message": "An unexpected error occurred"},
    )
