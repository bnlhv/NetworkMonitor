from pydantic import BaseSettings


class Settings(BaseSettings):
    """ Base settings of the client app. """
    HOST: str = "http://localhost"
    PORT: str = "8000"
    PATH_TO_SAVE_PLOTS: str = "/plots"


settings = Settings()
