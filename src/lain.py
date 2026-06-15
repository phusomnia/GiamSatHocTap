from uuid import uuid4
from fastapi import FastAPI, APIRouter
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from scalar_fastapi import get_scalar_api_reference
from typing import Optional
import granian
from src.SharedKernel.base.Decorators import register_controllers
from src.SharedKernel.base.Container import Container
from src.SharedKernel.base import Logger
from src.Infrastructure.Config import Config

config = Config()
config.load_env_yaml()

app = FastAPI(
    title=config.app.title,
    port=config.app.port
)

container = Container()
register_controllers(app, container)

@app.get("/docs")
async def redirect():
    return RedirectResponse(url="/scalar")

@app.get("/scalar", include_in_schema=False)
async def scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=config.app.title
    )