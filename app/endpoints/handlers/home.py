import litestar
import typing

@litestar.get("/", status_code=200)
async def home() -> typing.Dict[str, str]:
    """The home endpoint for the API."""
    return {
        "message": "Welcome to the homepage of an instance of the Zukijourney example API!",
        "github": "https://github.com/zukijourney/example-api"
    }