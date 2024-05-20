import traceback
from litestar import Request
from litestar.exceptions import HTTPException
from ..responses import PrettyJSONResponse
from ..exceptions import BaseError, InvalidRequestException, InvalidResponseException

def configure_error_handlers():
    """Sets up error handlers to return error messages on certain cases"""

    def status_404_handler(request: Request, _: Exception) -> PrettyJSONResponse:
        return InvalidRequestException(f"Invalid URL ({request.method} {request.url.path})", status=404).to_response()

    def status_405_handler(request: Request, _: Exception) -> PrettyJSONResponse:
        return InvalidRequestException(f"Invalid Method ({request.method} {request.url.path})", status=405).to_response()

    def exception_handler(_: Request, exc: Exception) -> PrettyJSONResponse:
        traceback.print_exc()
        return BaseError(f"An unexpected error has occurred: {exc}", status=500).to_response()
    
    def value_error_handler(_: Request, exc: Exception) -> PrettyJSONResponse:
        return InvalidRequestException(f"Invalid value: {exc}", status=400).to_response()
    
    def http_exception_handler(_: Request, exc: HTTPException) -> PrettyJSONResponse:
        return InvalidRequestException(exc.detail, status=exc.status_code).to_response()

    return {
        404: status_404_handler,
        405: status_405_handler,
        Exception: exception_handler,
        BaseError: BaseError._handler,
        InvalidRequestException: InvalidRequestException._handler,
        InvalidResponseException: InvalidResponseException._handler,
        HTTPException: http_exception_handler,
        ValueError: value_error_handler
    }