import traceback
from typing import Dict, Union
from litestar import Request
from litestar.exceptions import HTTPException
from ..responses import PrettyJSONResponse
from ..exceptions import BaseError, InvalidRequestException, InvalidResponseException

def configure_error_handlers() -> Dict[Union[int, Exception], PrettyJSONResponse]:
    """Sets up all error handlers"""

    def status_404_handler(request: Request, _: Exception) -> PrettyJSONResponse:
        """Not found page error handler"""
        return InvalidRequestException(f"Invalid URL ({request.method} {request.url.path})", status=404).to_response()

    def status_405_handler(request: Request, _: Exception) -> PrettyJSONResponse:
        """Method not allowed error handler"""
        return InvalidRequestException(f"Invalid Method ({request.method} {request.url.path})", status=405).to_response()

    def exception_handler(_: Request, exc: Exception) -> PrettyJSONResponse:
        """Generic error handler"""
        traceback.print_exc()
        return BaseError(f"An unexpected error has occurred: {exc}", status=500).to_response()
    
    def value_error_handler(_: Request, exc: Exception) -> PrettyJSONResponse:
        """Validation error handler"""
        return InvalidRequestException(f"Invalid value: {exc}", status=400).to_response()
    
    def http_exception_handler(_: Request, exc: HTTPException) -> PrettyJSONResponse:
        """HTTP exception handler"""
        return InvalidRequestException(exc.detail, status=exc.status_code).to_response()

    return {
        404: status_404_handler,
        405: status_405_handler,
        Exception: exception_handler,
        BaseError: BaseError.to_response,
        InvalidRequestException: InvalidRequestException.to_response,
        InvalidResponseException: InvalidResponseException.to_response,
        HTTPException: http_exception_handler,
        ValueError: value_error_handler
    }