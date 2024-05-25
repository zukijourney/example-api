from typing import Union

def get_exception_type(etype: Union[Exception, str]) -> str:
    """Returns a string representation of the exception class name"""
    class_name = etype.__class__.__name__.replace("Exception", "Error")
    return "".join(["_" + i.lower() if i.isupper() else i for i in class_name]).lstrip("_")

class BaseError(Exception):
    """
    Base class for all response exceptions in this project
    """

    def __init__(self, message: str, status: int = None) -> None:
        self.message = message
        self.type = get_exception_type(self)
        self.status = status

class InvalidRequestException(BaseError):
    """Exception for invalid requests"""
    pass

class InvalidResponseException(BaseError):
    """Exception for invalid responses"""
    pass