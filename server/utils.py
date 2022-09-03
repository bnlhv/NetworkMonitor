""" Utilities module """
import sys

from fastapi.responses import JSONResponse
from loguru import logger

from config import settings


def rate_calculator_to_json_response(dl: float, ul: float,
                                     nic_name: str) -> JSONResponse:
    """
    Calc the nic rate and if passes the threshold indicate with
    json response.

    :param nic_name: The specific nic's name.
    :param dl: Download at the last minute.
    :param ul: Upload at the last minute.
    :return: JsonResponse of what happened to return to client
    """
    mapping = {
        # [Download threshold detected, Upload threshold detected]
        "[True, True]": JSONResponse(
            content={
                "valid_threshold_check": False,
                "message": f"Both download and upload are passing thresholds "
                           f"for nic {nic_name}.",
            }),
        "[True, False]": JSONResponse(
            content={
                "valid_threshold_check": False,
                "message": f"Download is passing threshold for nic {nic_name}",
            }),
        "[False, True]": JSONResponse(
            content={
                "valid_threshold_check": False,
                "message": f"Upload are passing threshold for nic {nic_name}",
            }),
        "[False, False]": JSONResponse(
            content={
                "valid_threshold_check": True,
                "message": f"NICs rate aren't passing the thresholds.",
            })
    }
    dl_condition = (
            dl > settings.DL_MAX_NIC_RATE_THRESHOLD or
            dl < settings.DL_MIN_NIC_RATE_THRESHOLD
    )
    up_condition = (
            ul > settings.UL_MAX_NIC_RATE_THRESHOLD or
            ul < settings.UL_MIN_NIC_RATE_THRESHOLD
    )

    return mapping[str([dl_condition, up_condition])]


def config_logger() -> None:
    """ Override default logger. """
    logger.remove()
    logger.add(
        sys.stdout,
        colorize=True,
        format="<green>{time:HH:mm:ss}</green> | {level} | "
               "<level>{message}</level>",
    )
    logger.info("Config logger done")
