from litestar import Response
import ujson

class PrettyJSONResponse(Response):
    """
    Class for easily creating pretty JSON responses.
    """

    media_type = "application/json"
    status_code = 200

    def render(self, content: dict | list, *_):
        """Renders the given dict or list as an indented bytes object"""
        return ujson.dumps(
            obj=content,
            ensure_ascii=False,
            allow_nan=False,
            indent=4,
            separators=(", ", ": "),
            escape_forward_slashes=False
        ).encode("utf-8")