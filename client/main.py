import json
from datetime import datetime
from pathlib import Path

import fire
import pandas as pd
from httpx import AsyncClient
from loguru import logger

from config import settings

BASE_URL = f"{settings.HOST}:{settings.PORT}"


async def get_nics() -> json:
    """ Get all nics in the system. """
    url = f"{BASE_URL}/nics/"
    async with AsyncClient(timeout=None) as client:
        response = await client.get(url=url)
        return response.json()


async def check_nic_threshold(nic_name: str) -> None:
    """
    Check a given nic thresholds in the server.

    :param nic_name: The nic name (get from get_nics).
    """
    url = f"{BASE_URL}/nics/check_nic_rate_threshold/{nic_name}"
    async with AsyncClient(timeout=None) as client:
        response = await client.get(url=url)
        logger.info(response.json())


async def change_thresholds(params: dict) -> None:
    """ DRY function """
    url = f"{BASE_URL}/settings/update_thresholds/"
    async with AsyncClient(timeout=None) as client:
        response = await client.put(url=url, params=params)
        logger.info(response.json())


async def change_min_dl_threshold(new_threshold: int) -> None:
    """
    Change minimum download threshold settings in server.

    :param new_threshold: The new threshold you'll want to save to server.
    """
    await change_thresholds({"dl_min": new_threshold})


async def change_max_dl_threshold(new_threshold: int) -> None:
    """
    Change maximum download threshold settings in server

    :param new_threshold: The new threshold you'll want to save to server.
    """
    await change_thresholds({"dl_max": new_threshold})


async def change_min_ul_threshold(new_threshold: int) -> None:
    """
    Change minimum upload threshold settings in server

    :param new_threshold: The new threshold you'll want to save to server.
    """
    await change_thresholds({"ul_min": new_threshold})


async def change_max_ul_threshold(new_threshold: int) -> None:
    """
    Change maximum upload threshold settings in server

    :param new_threshold: The new threshold you'll want to save to server.
    """
    await change_thresholds({"ul_max": new_threshold})


async def get_snapshot(nic_name: str) -> None:
    """
    Get rates of nic for the last minute and save the snapshot.

    :param nic_name: The name of nic you'll want to get plot of.
    """
    url = f"{BASE_URL}/bandwidth/{nic_name}"
    async with AsyncClient(timeout=None) as client:
        response = await client.get(url=url)
        data = response.json()
        if data:
            timestamps = [v['timestamp'] for v in data]
            df = pd.DataFrame(data={
                "upload": [v["upload"] for v in data],
                "download": [v["download"] for v in data],
            }, index=timestamps)
            lines = df.plot.line()
            lines.figure.figsize = (18,18)
            lines.figure.savefig(Path.cwd() / Path("plots") / Path(f"{timestamps[-1]}.jpeg"))
        else:
            logger.debug("No data")


if __name__ == '__main__':
    fire.Fire()
