from typing import Optional, Union
from ..responses import PrettyJSONResponse

def get_exception_type(etype: Union[Exception, str]) -> str:
    class_name = etype.__class__.__name__.replace("Exception", "Error")
    return "".join(["_" + i.lower() if i.isupper() else i for i in class_name]).lstrip("_")

class BaseError(Exception):
    def __init__(self, message: str, param: Optional[str] = None, code: Optional[Union[int, str]] = None, status: int = None) -> None:
        self.message = message
        self.type = get_exception_type(self) if not isinstance(self.type, str) else self.type
        self.param = param
        self.code = code
        self.status = status

    def to_dict(self) -> dict[str, str]:
        return {"error": {"message": self.message, "type": self.type, "param": self.param, "code": self.code}}

    def to_response(self) -> PrettyJSONResponse:
        return PrettyJSONResponse(content=self.to_dict(), status_code=self.status)

class InvalidRequestException(BaseError):
    pass

class InvalidResponseException(BaseError):
    pass