import random
import string
import openai
import traceback
from fastapi.responses import ORJSONResponse, StreamingResponse
from typing import Union

def gen_random_string(prefix: str, length: int = 29, charset: str = string.ascii_letters + string.digits) -> str:
    """Generates a random string with a given prefix and length"""
    return prefix + "".join(random.choices(charset, k=length))

def gen_completion_id() -> str:
    """Generates a chat completion ID"""
    return gen_random_string("chatcmpl-")

def gen_system_fingerprint() -> str:
    """Generates a system fingerprint"""
    return gen_random_string("fp_", length=10, charset=string.ascii_lowercase + string.digits)

def make_response(message: str, type: str, status: int) -> ORJSONResponse:
    """Sets up the response for an error"""
    return ORJSONResponse(
        {"error": {"message": message, "type": type, "param": None, "code": None}},
        status_code=status
    )

def handle_errors(func):
    async def wrapper(*args, **kwargs) -> Union[ORJSONResponse, StreamingResponse]:
        try:
            return await func(*args, **kwargs)
        except openai.APIStatusError:
            traceback.print_exc()
            return make_response(
                message="We were unable to generate a response. Please try again later.",
                type="invalid_response_error",
                status_code=500
            )
    return wrapper