from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.middleware import SlowAPIMiddleware
from contextlib import asynccontextmanager
from .tasks import CreditsService
from .providers import BaseProvider
from .api import main_router
from .errors import ExceptionHandler
from .utils import request_processor

credits_service = CreditsService()
base_provider = BaseProvider()

@asynccontextmanager
async def lifespan(_: FastAPI):
    await credits_service.start()
    await base_provider.import_modules()
    await base_provider.sync_to_db()
    yield
    await credits_service.stop()
 
app = FastAPI(lifespan=lifespan)

app.state.limiter = Limiter(
    key_func=request_processor.get_api_key,
    default_limits=[
        '2/second',
        '30/minute'
    ]
)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*']
)

ExceptionHandler().setup(app)

app.include_router(main_router)