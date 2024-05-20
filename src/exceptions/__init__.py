from typing import Optional, Union
from starlette.exceptions import HTTPException
from ..responses import PrettyJSONResponse

def get_exception_type(etype: Union[Exception, str]):
    if isinstance(etype, str): return etype
    class_name = etype.__class__.__name__.replace('Exception', 'Error')
    return ''.join(['_' + i.lower() if i.isupper() else i for i in class_name]).lstrip('_')

class BaseError(Exception):
    def __init__(self, message: str, param: Optional[str] = None, code: Optional[Union[int, str]] = None, status: int = None):
        self.message = message
        self.type = get_exception_type(self)
        self.param = param
        self.code = code
        self.status = status

    def to_dict(self):
        return {"error": {"message": self.message, "type": self.type, "param": self.param, "code": self.code}}

    async def _handler(self, **_):
        return PrettyJSONResponse(content=self.to_dict(), status_code=self.status)

    def to_response(self):
        return PrettyJSONResponse(content=self.to_dict(), status_code=self.status)

class InvalidRequestException(BaseError):
    pass

class InvalidResponseException(BaseError):
    pass