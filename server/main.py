""" Main server module """
import asyncio
from typing import Dict

import uvicorn
from beanie import init_beanie
from fastapi import FastAPI, APIRouter
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient

from api import nics_router, bandwidth_router, settings_router
from config import settings
from models import NIC, BandwidthSample
from task import populate_nics, create_bandwidth_sample, keep_alive_nics
from utils import config_logger

app = FastAPI()
root_router = APIRouter()


@root_router.on_event("startup")
async def on_startup_actions() -> None:
    """ Make on startup actions """
    config_logger()

    client = AsyncIOMotorClient(
        f"mongodb://{settings.DB_HOST}:{settings.DB_PORT}"
    )
    await init_beanie(database=client.db_name,
                      document_models=[NIC, BandwidthSample])
    await NIC.delete_all()
    await BandwidthSample.delete_all()

    await asyncio.gather(
        asyncio.create_task(populate_nics()),
        asyncio.create_task(create_bandwidth_sample()),
        asyncio.create_task(keep_alive_nics()),
    )


@root_router.get("/", response_model=Dict)
async def root() -> Dict:
    return {"message": "Hey! It's Ben and that's the root path."}


# Routers configuration
app.include_router(root_router)
app.include_router(nics_router)
app.include_router(bandwidth_router)
app.include_router(settings_router)


async def main() -> None:
    """ Main program function. """
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


if __name__ == '__main__':
    """ Run this function if this module ran explicitly """
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        # Graceful shutdown async tasks
        logger.warning("Gracefully shutdown all tasks.")
        loop.stop()
