import datetime
import logging
from json import JSONDecodeError

import requests

from ..exceptions import TmdbApiException
from ..models import Result


class RestAdapter:
    def __init__(self, api_key: str, api_ver: int = 3, safe_logging: bool = True):
        self.api_url = f'https://api.themoviedb.org/{api_ver}/'
        self._api_key = api_key
        self.safe_logging = safe_logging
        self._session = requests.Session()
        self._authenticate()

    def _authenticate(self):
        """Private method for authenticating a session with the API
        """
        self.auth_url = f'https://api.themoviedb.org/3/authentication/token/new?api_key={self._api_key}'
        if self.safe_logging:
            logging.debug(f'{self.auth_url=}')
        else:
            logging.debug(f'{self.auth_url=}, {self._api_key=})')

        try:
            post_request = requests.post(self.auth_url, json=self._api_key)
        except requests.exceptions.RequestException as e:
            logging.critical(str(e))
            raise TmdbApiException('Request failed') from e

        try:
            self._token = post_request.json()['access_token']
            self._token_expiration = datetime.datetime.now(
            ) + datetime.timedelta(seconds=post_request.json()['expires_in'])
            self._headers = {'accept': 'application/json',
                             'Authorization': f'Bearer {self._token}'}
            self._session.headers.update(self._headers)
        except KeyError:
            logging.critical(post_request.json()['details'])
            raise TmdbApiException(post_request.json()['details'])

    def _check_and_reauth(self) -> datetime.datetime:
        if datetime.datetime.now() + datetime.timedelta(minutes=2) >= self._token_expiration:
            self._authenticate()
        return self._token_expiration

    def _make_request(self, method: str, url: str, params: dict = {}, json: dict = {}) -> requests.Response:
        """Log HTTP params and perform an HTTP request, catching and re-raising any exceptions

        Args:
            method (str): GET or POST
            url (str): URL endpoint
            params (dict): Endpoint parameters
            json (dict): Data payload

        Returns:
            request result
        """
        log_line_pre = f'{method=}, {url=}, {params=}'
        try:
            self._check_and_reauth()
            logging.debug(log_line_pre)
            return self._session.request(method=method, url=url, params=params, json=json)
        except requests.exceptions.RequestException as e:
            logging.critical(str(e))
            raise TmdbApiException('Request failed') from e

    def _do(self, http_method: str, endpoint: str, ep_params: dict = {}, data: dict = {}) -> Result:
        """Private method for get and post methods

        Args:
            http_method (str): GET or POST
            endpoint (str): URL endpoint
            ep_params (Dict, optional): Endpoint parameters. Defaults to None.
            data (Dict, optional): Data payload. Defaults to None.

        Returns:
            Result: a Result object
        """
        ep_params.setdefault('top', 10000)
        full_api_url = self.api_url + endpoint

        log_line_post = ('success={}, status_code={}, message={}')
        response = self._make_request(method=http_method,
                                      url=full_api_url, params=ep_params, json=data)
        # Deserialize JSON output to Python object, or return failed Result on exception
        try:
            data_out = response.json()
        except (ValueError, JSONDecodeError) as e:
            logging.critical(log_line_post.format(False, None, e))
            raise TmdbApiException('Bad JSON in response') from e

        # If status_code in 200-299 range, return success Result with data, otherwise raise exception
        is_success = 299 >= response.status_code >= 200
        log_line = log_line_post.format(
            is_success, response.status_code, response.reason)

        if is_success:
            logging.debug(log_line)
            return Result(status_code=response.status_code, message=response.reason, data=data_out)

        logging.critical(log_line)
        raise TmdbApiException(f'{response.status_code} - {response.reason}')

    def get(self, endpoint: str, ep_params: dict = {}) -> Result:
        """HTTP GET request

        Args:
            endpoint (str): URL endpoint
            ep_params (Dict, optional): Endpoint parameters. Defaults to None.

        Returns:
            Result: a Result object
        """
        return self._do(http_method='GET', endpoint=endpoint, ep_params=ep_params)

    def post(self, endpoint: str, ep_params: dict = {}, data: dict = {}) -> Result:
        """HTTP POST request

        Args:
            endpoint (str): URL endpoint
            ep_params (Dict, optional): Endpoint parameters. Defaults to None.
            data (Dict, optional): Data payload. Defaults to None.

        Returns:
            Result: a Result object
        """
        return self._do(http_method='POST', endpoint=endpoint, ep_params=ep_params, data=data)

    def dl(self, file_url: str) -> requests.Response:
        """HTTP GET request for file downloads so authentication is maintained

        Args:
            file_url (str): URL of the file to download

        Returns:
            Result: Result object
        """
        return self._make_request(method='GET', url=file_url)
