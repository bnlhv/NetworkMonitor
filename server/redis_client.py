""" Redis service connection module """
import loguru
import redis
import rq
from fastapi_utils.tasks import repeat_every

from config import settings
from models import NIC
from task import keep_alive_nics, create_bandwidth_sample

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
)

bandwidth_queue = rq.Queue(name=settings.BANDWIDTH_QUEUE,
                           connection=redis_client)
nic_queue = rq.Queue(name=settings.NIC_QUEUE, connection=redis_client)


@repeat_every(seconds=settings.INTERVAL_TASK_MONITOR_NICS,
              logger=loguru.logger, wait_first=True)
async def monitor_nics() -> None:
    """ Function that startup all redis periodic tasks """
    nic_queue.enqueue_call(keep_alive_nics)


@repeat_every(seconds=settings.INTERVAL_TASK_BW_SAMPLE, logger=loguru.logger)
async def save_nic_bandwidth_sample() -> None:
    """ Function that startup all redis periodic tasks """
    async for nic in NIC.find_all():
        bandwidth_queue.enqueue_call(create_bandwidth_sample, args=(nic,),
                                     kwargs={})
