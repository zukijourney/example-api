from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .handlers import routes
from .utils import configure_error_handlers

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

for route in routes:
    app.include_router(route)

for exception, handler in configure_error_handlers().items():
    app.add_exception_handler(exception, handler)