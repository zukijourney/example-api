import random
import string
from ..responses import PrettyJSONResponse

def gen_random_string(prefix: str, length: int = 29, charset: str = string.ascii_letters + string.digits) -> str:
   """Generates a random string with a given prefix and length"""
   return prefix + "".join(random.choices(charset, k=length))

def gen_completion_id() -> str:
   """Generates a chat completion ID"""
   return gen_random_string("chatcmpl-")

def gen_system_fingerprint() -> str:
   """Generates a system fingerprint"""
   return gen_random_string("fp_", length=10, charset=string.ascii_lowercase + string.digits)

def make_response(message: str, error_type: str, status_code: int) -> PrettyJSONResponse:
   """Sets up the response for an error"""
   return PrettyJSONResponse(
      {"error": {"message": message, "type": error_type, "param": None, "code": None}},
      status_code=status_code
   )