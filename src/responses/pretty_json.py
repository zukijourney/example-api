from starlette.responses import Response
import ujson

class PrettyJSONResponse(Response):
    media_type = "application/json"

    def render(self, content: dict | list):
        return ujson.dumps(
            obj=content,
            ensure_ascii=False,
            allow_nan=False,
            indent=4,
            separators=(", ", ": "),
            escape_forward_slashes=False
        ).encode("utf-8")