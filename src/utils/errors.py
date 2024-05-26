import traceback
from typing import Union
from litestar import Request, Response
from litestar.types import ExceptionHandlersMap
from litestar.exceptions import HTTPException, ValidationException
from ..exceptions import BaseError, InvalidRequestException, InvalidResponseException
from . import make_response

def configure_error_handlers() -> ExceptionHandlersMap:
    """Sets up all error handlers"""

    def status_404_handler(request: Request, _: Exception) -> Response:
        """Not found page error handler"""
        return make_response(f"Invalid URL ({request.method} {request.url.path})", "invalid_request_error", 404)

    def status_405_handler(request: Request, _: Exception) -> Response:
        """Method not allowed error handler"""
        return make_response(f"Invalid Method ({request.method} {request.url.path})", "invalid_request_error", 405)

    def exception_handler(_: Request, exc: Exception) -> Response:
        """Generic error handler"""
        traceback.print_exc()
        return make_response(f"An unexpected error has occurred: {exc}", "base_error", 500)
    
    def validation_error_handler(_: Request, exc: ValidationException) -> Response:
        """Validation error handler"""
        message = exc.extra[0]["message"].replace("Value error, ", "")
        return make_response(message, "invalid_request_error", 400 if "Invalid model" not in message else 404)
    
    def http_exception_handler(_: Request, exc: Union[InvalidRequestException, InvalidResponseException]) -> Response:
        """HTTP exception handler"""
        return make_response(exc.message, exc.type, exc.status)

    return {
        404: status_404_handler,
        405: status_405_handler,
        Exception: exception_handler,
        BaseError: exception_handler,
        InvalidRequestException: http_exception_handler,
        InvalidResponseException: http_exception_handler,
        HTTPException: http_exception_handler,
        ValueError: validation_error_handler,
        ValidationException: validation_error_handler
    }