from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings): 
    Failed_Extraction: str = 'data/failed/'
    Success_Extractiom: str = 'data/success/'

    class Config:
        env_file = '.env'


@lru_cache
def get_settings():
    return Settings()