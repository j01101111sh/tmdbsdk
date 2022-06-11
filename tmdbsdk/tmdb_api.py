import logging

from .tools import RestAdapter


class TmdbApi:
    def __init__(self, api_key: str, api_ver: int = 3, safe_logging: bool = True):
        supported_api_versions = {3}
        if api_ver not in supported_api_versions:
            logging.warning(f'Untested API version - API:{api_ver}')
        self._rest_adapter = RestAdapter(
            api_key=api_key, api_ver=api_ver, safe_logging=safe_logging)
