import litestar
import typing
import ujson

class PrettyJSONResponse(litestar.Response):
    """
    A class for returning a pretty JSON response.
    """

    media_type = litestar.MediaType.JSON

    def render(self, content: typing.Union[dict, list], *_) -> bytes:
        """Renders the response to a pretty JSON bytes object."""
        return ujson.dumps(
            obj=content,
            indent=4,
            ensure_ascii=False,
            escape_forward_slashes=False,
            separators=(",", ": ")
        )