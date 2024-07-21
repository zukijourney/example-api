import litestar
import logging
from litestar.exceptions import ValidationException
from ..responses import PrettyJSONResponse

def get_exception_handlers() -> dict:
    """Returns a dictionary of exception handlers."""

    def not_found(request: litestar.Request, _: Exception) -> PrettyJSONResponse:
        """Handles an error for when an endpoint is not found."""
        return PrettyJSONResponse(
            content={
                "error": {
                    "message": f"Invalid URL ({request.method} {request.url.path})",
                    "type": "invalid_request_error",
                    "param": None,
                    "code": None
                }
            },
            status_code=404
        )
    
    def method_not_allowed(request: litestar.Request, _: Exception) -> PrettyJSONResponse:
        """Handles an error for when an endpoint is not found."""
        return PrettyJSONResponse(
            content={
                "error": {
                    "message": f"Not allowed to {request.method} on {request.url.path}.",
                    "type": "invalid_request_error",
                    "param": None,
                    "code": None
                }
            },
            status_code=405
        )

    def internal_server_error(_: litestar.Request, exc: Exception) -> PrettyJSONResponse:
        """Handles an unexpected internal server error."""
        logging.error(f"Internal server error: {exc}")
        return PrettyJSONResponse(
            content={
                "error": {
                    "message": "Internal server error",
                    "type": "unexpected_error",
                    "param": None,
                    "code": None
                }
            },
            status_code=500
        )

    def validation_error(_: litestar.Request, exc: ValidationException) -> PrettyJSONResponse:
        """Handles a validation error."""
        logging.error(f"Validation error: {exc}")
        return PrettyJSONResponse(
            content={
                "error": {
                    "message": "Your request payload is invalid.",
                    "type": "invalid_request_error",
                    "param": ", ".join(set(error for field in exc.extra for error in field["loc"])),
                    "code": None
                }
            },
            status_code=422
        )
        
    return {
        404: not_found,
        500: internal_server_error,
        422: validation_error,
        400: validation_error,
        405: method_not_allowed
    }