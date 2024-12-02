from dataclasses import dataclass
from typing import Dict, Any, Callable, Awaitable, Type, Union, Optional
from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import ValidationException
from slowapi.errors import RateLimitExceeded
from .api import ValidationError, AccessError, AuthenticationError
from .responses import JSONResponse

@dataclass
class ErrorResponse:
    message: str
    error_type: str
    code: int
    status_code: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            'error': {
                'message': self.message,
                'type': self.error_type,
                'code': self.code
            }
        }

class ExceptionHandler:
    def __init__(self):
        self.handlers: Dict[
            Type[Exception],
            Callable[[Request, Exception], Awaitable[JSONResponse]]
        ] = {}
        self._register_default_handlers()

    def _register_default_handlers(self) -> None:
        self.handlers.update({
            Exception: self._handle_generic_exception,
            AccessError: self._handle_http_exception,
            AuthenticationError: self._handle_http_exception,
            HTTPException: self._handle_http_exception,
            ValidationError: self._handle_validation_exception,
            ValidationException: self._handle_validation_exception,
            RateLimitExceeded: self._handle_rate_limit_exceeded
        })

    @staticmethod
    def _create_error_response(
        message: str,
        error_type: str = 'invalid_request_error',
        code: int = 400,
        status_code: Optional[int] = None
    ) -> ErrorResponse:
        return ErrorResponse(
            message=message,
            error_type=error_type,
            code=code,
            status_code=status_code or code
        )

    @staticmethod
    def _create_json_response(error_response: ErrorResponse) -> JSONResponse:
        return JSONResponse(
            status_code=error_response.status_code,
            content=error_response.to_dict()
        )

    async def _handle_generic_exception(
        self,
        _: Request,
        __: Exception
    ) -> JSONResponse:
        error_response = self._create_error_response(
            message='An internal server error occurred while processing your request. Try again later.',
            error_type='internal_server_error',
            code=500,
            status_code=500
        )
        return self._create_json_response(error_response)

    async def _handle_validation_exception(
        self,
        _: Request,
        exc: Union[ValidationException, ValidationError, ValueError]
    ) -> JSONResponse:
        if isinstance(exc, ValidationException):
            error_response = self._create_error_response(
                message=exc.errors()[0]['msg'],
                error_type='invalid_request_error',
                code=400,
                status_code=400
            )
        else:
            error_response = self._create_error_response(
                message=exc.message if hasattr(exc, 'message') else str(exc),
                error_type='invalid_request_error',
                code=400,
                status_code=400
            )

        return self._create_json_response(error_response)

    async def _handle_http_exception(
        self,
        _: Request,
        exc: Union[HTTPException, AccessError, AuthenticationError]
    ) -> JSONResponse:
        error_response = self._create_error_response(
            message=exc.detail if hasattr(exc, 'detail') else exc.message,
            error_type='invalid_request_error',
            code=exc.status_code,
            status_code=exc.status_code
        )
        return self._create_json_response(error_response)

    async def _handle_rate_limit_exceeded(
        self,
        _: Request,
        exc: RateLimitExceeded
    ) -> JSONResponse:
        error_response = self._create_error_response(
            message=f'Rate limit exceeded: {exc.detail}',
            error_type='invalid_request_error',
            code=400,
            status_code=exc.status_code
        )
        return self._create_json_response(error_response)

    def register_handler(
        self,
        exception_class: Type[Exception],
        handler: Callable[[Request, Exception], Awaitable[JSONResponse]]
    ) -> None:
        self.handlers[exception_class] = handler

    def setup(self, app: FastAPI) -> None:
        for exception_class, handler in self.handlers.items():
            app.add_exception_handler(exception_class, handler)