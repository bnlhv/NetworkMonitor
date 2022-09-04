""" Controllers module for api contract with other apps """
from datetime import datetime, timedelta
from typing import List, Optional, Union

from fastapi import APIRouter, status, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.responses import Response

from config import settings
from models import NIC, BandwidthSample
from utils import rate_calculator_to_json_response

nics_router = APIRouter(prefix="/nics", tags=["nics"])
bandwidth_router = APIRouter(prefix="/bandwidth", tags=["bandwidths"])
settings_router = APIRouter(prefix="/settings", tags=["settings"])


@nics_router.get("/")
async def get_nics() -> List[NIC]:
    """ Get all NICs that exists in database """
    return await NIC.find_all().to_list()


@bandwidth_router.get("/{nic_name}")
async def get_nic_bandwidth_samples(
        nic_name: str,
        last_minutes: int = 1,
) -> Union[Response, JSONResponse]:
    """
    Get all bandwidth samples of specific nic.

    :param nic_name: The unique nic name.
    :param last_minutes: The timedelta in minutes of last minutes samples.
    :return: HTTP status code representing what happened.
    :raises: HTTPException: if the db doesn't contain this nic_id.
    """
    wanted_timestamp = datetime.now() - timedelta(minutes=last_minutes)
    bw_samples = await BandwidthSample.find(
        BandwidthSample.nic_name == nic_name,
    ).find(
        BandwidthSample.timestamp > wanted_timestamp,
    ).sort("timestamp").to_list()

    if not bw_samples:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    return JSONResponse(content=jsonable_encoder(bw_samples),
                        status_code=status.HTTP_200_OK)


@nics_router.get("/check_nic_rate_threshold/{nic_name}")
async def check_nic_rate_threshold(
        nic_name: str,
) -> JSONResponse:
    """
    Check specific NIC rate threshold.

    :param nic_name: The unique nic name.
    :return: response message indicating the nic threshold test.
    """
    last_minute_timestamp = datetime.now() - timedelta(minutes=1)
    bw_samples = await BandwidthSample.find(
        BandwidthSample.nic_name == nic_name,
    ).find(
        BandwidthSample.timestamp > last_minute_timestamp,
    ).sort("timestamp").to_list()

    first_sample = bw_samples[0] if bw_samples else None
    last_sample = bw_samples[-1] if bw_samples else None

    if first_sample and first_sample is not last_sample:
        last_minute_download = last_sample.download - first_sample.download
        last_minute_upload = last_sample.upload - first_sample.upload

        return rate_calculator_to_json_response(
            dl=last_minute_download,
            ul=last_minute_upload,
            nic_name=nic_name,
        )

    return JSONResponse(content="Not valid data yet or name given.",
                        status_code=status.HTTP_404_NOT_FOUND)


@settings_router.put("/update_thresholds")
async def update_thresholds(
        dl_min: Optional[int] = None,
        dl_max: Optional[int] = None,
        ul_min: Optional[int] = None,
        ul_max: Optional[int] = None,
) -> JSONResponse:
    """
    Update settings threshold.

    :param dl_min: Download minimum threshold.
    :param dl_max: Download maximum threshold.
    :param ul_min: Upload minimum threshold.
    :param ul_max: Upload maximum threshold.
    :return: JSON response
    """
    if dl_min:
        if (dl_max and dl_min >= dl_max) or (
                dl_min >= settings.DL_MAX_NIC_RATE_THRESHOLD):
            raise HTTPException(detail="Min threshold can't be greater than "
                                       "or equal to Max threshold.",
                                status_code=status.HTTP_400_BAD_REQUEST)
        settings.DL_MIN_NIC_RATE_THRESHOLD = dl_min
    if dl_max:
        if dl_max <= settings.DL_MIN_NIC_RATE_THRESHOLD:
            raise HTTPException(detail="Max threshold can't be less than "
                                       "or equal to Min threshold.",
                                status_code=status.HTTP_400_BAD_REQUEST)
        settings.DL_MAX_NIC_RATE_THRESHOLD = dl_max
    if ul_min:
        if (ul_max and ul_min >= ul_max) or (
                ul_min >= settings.UL_MAX_NIC_RATE_THRESHOLD):
            raise HTTPException(detail="Min threshold can't be greater than "
                                       "or equal to Max threshold.",
                                status_code=status.HTTP_400_BAD_REQUEST)
        settings.UL_MIN_NIC_RATE_THRESHOLD = ul_min
    if ul_max:
        if ul_max <= settings.UL_MIN_NIC_RATE_THRESHOLD:
            raise HTTPException(detail="Max threshold can't be less than "
                                       "or equal to Min threshold.",
                                status_code=status.HTTP_400_BAD_REQUEST)
        settings.UL_MAX_NIC_RATE_THRESHOLD = ul_max

    logger.debug(f"{settings.DL_MIN_NIC_RATE_THRESHOLD},"
                 f"{settings.DL_MAX_NIC_RATE_THRESHOLD},"
                 f"{settings.UL_MIN_NIC_RATE_THRESHOLD},"
                 f"{settings.UL_MAX_NIC_RATE_THRESHOLD}")

    return JSONResponse(content="Updated", status_code=status.HTTP_200_OK)
