from starlette.requests import Request
from starlette.exceptions import HTTPException
from ..exceptions import BaseError, RateLimitException, InvalidRequestException, InvalidResponseException
import traceback

def configure_error_handlers():
    async def status_404_handler(request: Request, _: HTTPException):
        return InvalidRequestException(f"Invalid URL ({request.method} {request.url.path})", status=404).to_response()

    async def status_405_handler(request: Request, _: HTTPException):
        return InvalidRequestException(f"Invalid Method ({request.method} {request.url.path})", status=405).to_response()

    async def exception_handler(_: Request, exc: HTTPException):
        traceback.print_exc()
        return BaseError(f"An unexpected error has occurred: {exc}", status=500).to_response()

    return {
        404: status_404_handler,
        405: status_405_handler,
        Exception: exception_handler,
        BaseError: BaseError._handler,
        RateLimitException: RateLimitException._handler,
        InvalidRequestException: InvalidRequestException._handler,
        InvalidResponseException: InvalidResponseException._handler,
    }