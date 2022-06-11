__title__ = 'tmdbsdk'
__version__ = '0.1.0'
__author__ = 'Josh Odell'
__license__ = 'GPLv3'

from .exceptions import TmdbApiException
from .tmdb_api import TmdbApi

__all__ = ['TmdbApiException', 'TmdbApi']
