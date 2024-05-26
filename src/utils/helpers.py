import random
import string
import ujson
from litestar import Response

def gen_random_string(prefix: str, length: int = 29, charset: str = string.ascii_letters + string.digits) -> str:
   """Generates a random string with a given prefix and length"""
   return prefix + "".join(random.choices(charset, k=length))

def gen_completion_id() -> str:
   """Generates a chat completion ID"""
   return gen_random_string("chatcmpl-")

def gen_system_fingerprint() -> str:
   """Generates a system fingerprint"""
   return gen_random_string("fp_", length=10, charset=string.ascii_lowercase + string.digits)

def make_response(message: str, type: str, status_code: int) -> Response:
   """Sets up the response for an error"""
   return Response(
      ujson.dumps({"error": {"message": message, "type": type, "param": None, "code": None}}, indent=4, escape_forward_slashes=False),
      status_code=status_code
   )