from litestar import Response
from typing import Union
import ujson

class PrettyJSONResponse(Response):
    """
    Class for easily creating pretty JSON responses
    """

    media_type = "application/json"
    status_code = 200

    def render(self, content: Union[dict, list], *_) -> bytes:
        """Renders the given dict or list as an indented bytes object"""
        return ujson.dumps(
            obj=content,
            ensure_ascii=False,
            allow_nan=False,
            indent=4,
            separators=(", ", ": "),
            escape_forward_slashes=False
        ).encode("utf-8")