""" Asynchronous tasks module """
import asyncio
import functools
import time
from typing import cast, Dict, Tuple, List

import loguru
import psutil
from beanie import Document
from fastapi_utils.tasks import repeat_every
from loguru import logger

from config import settings
from database import Database
from exceptions import NicDownException
from models import NIC, BandwidthSample


def worker_first_db_init(documents: List[Document]):
    """ Decorator to check if worker needs db initialization. """

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            logger.info("Checking if db needs to be restarted")
            logger.info(f"going to init? {settings.WORKER_INITIALIZED}")
            if not settings.WORKER_INITIALIZED:
                logger.info("Restart DB!")
                Database()
                settings.WORKER_INITIALIZED = True
                logger.info(f"Changed to {settings.WORKER_INITIALIZED}!")
            return func(*args, **kwargs)

        return wrapper

    return decorator


async def populate_nics() -> None:
    """ Populate NICs to db. """
    relevant_interfaces = [k for k, v in psutil.net_if_stats().items() if
                           v.isup]
    interfaces = dict(
        (k, v) for k, v in
        dict(psutil.net_io_counters(pernic=True, nowrap=True)).items()
        if k in relevant_interfaces
    )
    for inf in interfaces.keys():
        result = await NIC.find_one(NIC.name == inf)
        if not result:
            result = await NIC(name=inf).create()
            logger.debug(f"Populated {result.id} NIC id doc")
        else:
            logger.debug(f"{result.id} already populated")
    logger.debug(f"Populated all NICs")


@repeat_every(seconds=settings.INTERVAL_TASK_BW_SAMPLE, logger=loguru.logger)
async def create_bandwidth_sample() -> None:
    """ Redis task creates bandwidth sample per NIC. """

    def get_net_info(interface: str) -> Tuple[float, int, int]:
        """ :returns: The network info of specific interface. """
        inf = cast(Dict, psutil.net_io_counters(pernic=True,
                                                nowrap=True))
        return (
            time.time(), inf[interface].bytes_sent, inf[interface].bytes_recv,
        )

    async for nic in NIC.find_all():
        t1, bytes_sent_1, bytes_recv_1 = get_net_info(interface=nic.name)
        await asyncio.sleep(settings.NETWORK_SLEEP_TIME)
        t2, bytes_sent_2, bytes_recv_2 = get_net_info(interface=nic.name)

        net_sent = (bytes_sent_2 - bytes_sent_1) / (t2 - t1)
        net_recv = (bytes_recv_2 - bytes_recv_1) / (t2 - t1)

        net_sent = round(net_sent / 1024 / 1024, 3)
        net_recv = round(net_recv / 1024 / 1024, 3)

        logger.debug(f"Upload sample for nic: {nic.name} is {net_sent}Mbps")
        logger.debug(f"Download sample for nic: {nic.name} is {net_recv}Mbps")

        await BandwidthSample(
            nic_name=nic.name, upload=net_sent, download=net_recv).insert()


@repeat_every(seconds=settings.INTERVAL_TASK_MONITOR_NICS,
              logger=loguru.logger)
async def keep_alive_nics() -> None:
    """ Task for checking that all nics are up. """
    current_live_nics = [k for k, v in psutil.net_if_stats().items() if v.isup]
    async for nic in NIC.find_all():
        if nic.name not in current_live_nics:
            logger.warning(f"Detected exception for nic: {nic}")
            raise NicDownException(f"NIC {nic} is down")
