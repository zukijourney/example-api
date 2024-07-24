import litestar

@litestar.get("/")
async def home() -> dict[str, str]:
    """The home endpoint for the API."""
    return {
        "message": "Welcome to the homepage of an instance of the Zukijourney example API!",
        "github": "https://github.com/zukijourney/example-api"
    }
