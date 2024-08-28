import litestar
import traceback
import typing
from litestar.exceptions import ValidationException, HTTPException
from .responses import JSONResponse

T = typing.TypeVar("T", str, typing.List[str])

def get_exception_handlers() -> dict:
    """Returns a dictionary of exception handlers."""

    def not_found(*_) -> JSONResponse:
        """Handles a not found error."""
        return JSONResponse(
            content={"detail": "Not Found"},
            status_code=404
        )
    
    def method_not_allowed(*_) -> JSONResponse:
        """Handles a method not allowed error."""
        return JSONResponse(
            content={"detail": "Method Not Allowed"},
            status_code=405
        )

    def internal_server_error(_: litestar.Request, exc: Exception) -> JSONResponse:
        """Handles an unexpected internal server error."""
        traceback.print_exception(type(exc), exc, exc.__traceback__)
        return JSONResponse(
            content={
                "error": {
                    "message": f"Unexpected error: {exc}",
                    "type": "unexpected_error",
                    "param": None,
                    "code": None
                }
            },
            status_code=500
        )

    def validation_error(_: litestar.Request, exc: ValidationException) -> JSONResponse:
        """Handles a validation error."""
        
        def get_message(exc: ValidationException) -> str:
            if len(exc.extra) == 1 and "message" in exc.extra[0]:
                return exc.extra[0]["message"].replace("Value error, ", "")
            elif len(exc.extra) == 1:
                return exc.detail
            else:
                return "Your payload did not pass the validation checks. Review your request and try again."
        
        def get_params(exc: ValidationException) -> str:
            if len(exc.extra) > 1:
                return [field["key"] for field in exc.extra if "key" in field]
            else:
                return exc.extra[0]["key"]
        
        def get_error_details(param: T) -> typing.Tuple[typing.Optional[str], int]:
            if isinstance(param, str):
                if "model" in param:
                    return "model_not_found", 404
                elif "voice" in param:
                    return "voice_not_found", 404
                else:
                    return None, 422
            else:
                return None, 422
        
        message = get_message(exc)
        params = get_params(exc)
        code, status_code = get_error_details(params)
        
        return JSONResponse(
            content={
                "error": {
                    "message": message,
                    "type": "invalid_request_error",
                    "param": params if not any(value in message.lower() for value in ["model", "voice"]) else None,
                    "code": code
                }
            },
            status_code=status_code
        )

    def http_exception(_: litestar.Request, exc: HTTPException) -> JSONResponse:
        """Handles an HTTP exception."""
        return JSONResponse(
            content={
                "error": {
                    "message": exc.detail,
                    "type": "invalid_request_error",
                    "param": None,
                    "code": exc.extra.get("code") if exc.extra else None
                }
            },
            status_code=exc.status_code
        )
        
    return {
        404: not_found,
        405: method_not_allowed,
        Exception: internal_server_error,
        HTTPException: http_exception,
        ValidationException: validation_error
    }