""" Database setup """

from asyncinit import asyncinit
from beanie import init_beanie
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient
from singleton_decorator import singleton

from config import settings
from models import BandwidthSample, NIC


@singleton
@asyncinit
class Database:
    async def __init__(self):
        """ Extract for async call"""
        client = AsyncIOMotorClient(
            f"mongodb://{settings.DB_HOST}:{settings.DB_PORT}"
        )
        await init_beanie(database=client.db_name,
                          document_models=[NIC, BandwidthSample])
        logger.info("Database initialized")
