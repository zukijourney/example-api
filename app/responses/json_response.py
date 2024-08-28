import litestar
import orjson
import typing

class JSONResponse(litestar.Response):
    """
    A class for returning a JSON response.
    """

    media_type = litestar.MediaType.JSON

    def render(self, content: typing.Union[dict, list], *_) -> bytes:
        """Renders the response to a JSON bytes object."""
        return orjson.dumps(content)