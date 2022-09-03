""" App configurations """

from pydantic import BaseSettings


class Settings(BaseSettings):
    """ Settings configuration. """
    # Mongo configs
    DB_HOST: str = "localhost"
    DB_PORT: str = "27017"
    NIC_DB_COLLECTION: str = "network_interface_card_collection"
    BW_DB_COLLECTION: str = "bandwidth_sample_collection"

    # Tasks configs
    NETWORK_SLEEP_TIME: int = 5
    INTERVAL_TASK_MONITOR_NICS: int = 5
    INTERVAL_TASK_BW_SAMPLE: int = 10

    # Represents Mbps
    DL_MIN_NIC_RATE_THRESHOLD: int = 0
    DL_MAX_NIC_RATE_THRESHOLD: int = 5
    UL_MIN_NIC_RATE_THRESHOLD: int = 0
    UL_MAX_NIC_RATE_THRESHOLD: int = 3


settings = Settings()
