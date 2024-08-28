import typing
import traceback
from litestar.response import Stream
from ..responses import JSONResponse

def handle_errors(func: typing.Coroutine) -> typing.Coroutine:
    """Decorator to handle errors for a provider."""
    
    async def wrapper(*args, **kwargs) -> typing.Union[JSONResponse, Stream]:
        try:
            return await func(*args, **kwargs)
        except (IndexError, RuntimeError, TypeError, ValueError):
            traceback.print_exc()
            return JSONResponse(
                content={
                    "error": {
                        "message": "We're sorry, something went wrong. Please try again later.",
                        "type": "unexpected_error",
                        "param": None,
                        "code": None
                    }
                },
                status_code=500
            )
    
    return wrapper