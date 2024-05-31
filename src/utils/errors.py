import traceback
from typing import Union, Callable
from fastapi import Request
from fastapi.responses import ORJSONResponse
from fastapi.exceptions import HTTPException, ValidationException
from ..exceptions import BaseError, InvalidRequestException, InvalidResponseException
from . import make_response

def configure_error_handlers() -> dict[Union[type, Exception, int], Callable]:
    """Returns a dict of error handlers"""

    def status_404_handler(request: Request, _: Exception) -> ORJSONResponse:
        """Not found page error handler"""
        return make_response(f"Invalid URL ({request.method} {request.url.path})", "invalid_request_error", 404)

    def status_405_handler(request: Request, _: Exception) -> ORJSONResponse:
        """Method not allowed error handler"""
        return make_response(f"Invalid Method ({request.method} {request.url.path})", "invalid_request_error", 405)

    def exception_handler(_: Request, exc: Exception) -> ORJSONResponse:
        """Generic error handler"""
        traceback.print_exc()
        return make_response(f"An unexpected error has occurred: {exc}", "base_error", 500)
    
    def validation_error_handler(_: Request, exc: ValidationException) -> ORJSONResponse:
        """Validation error handler"""
        message = exc.extra[0]["message"].replace("Value error, ", "")
        return make_response(message, "invalid_request_error", 400 if "Invalid model" not in message else 404)
    
    def http_exception_handler(_: Request, exc: Union[InvalidRequestException, InvalidResponseException]) -> ORJSONResponse:
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