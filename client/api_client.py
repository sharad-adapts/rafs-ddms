#  Copyright 2023 ExxonMobil Technology and Engineering Company
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
import uuid
from os import linesep
from time import sleep
from typing import List
from urllib.parse import urljoin, urlparse

import requests
from loguru import logger
from starlette import status

from app.resources.common_headers import CORRELATION_ID, DATA_PARTITION_ID
from client.api.settings import ApiClientSettings


class APIException(Exception):
    """Error class for manipulating API response results."""


class HTTPMethods(object):
    GET = "get"
    POST = "post"
    DELETE = "delete"


class APIClient(object):
    """Class API client."""

    def __init__(self, host: str, version: str, url_prefix: str, data_partition: str, token: str) -> None:
        settings = ApiClientSettings()
        extracted_url_prefix = urlparse(host).path
        self.host = host
        self.url_prefix = f"{extracted_url_prefix}{url_prefix}{version}"
        self.data_partition = data_partition
        self.token = token
        self.url: str
        self.retry_attempts = settings.retry_attempts
        self.retry_delay = settings.retry_delay

    def post(self, path: str, **kwargs) -> requests.Response:
        return self._send_request(method=HTTPMethods.POST, path=path, **kwargs)

    def get(self, path: str, **kwargs) -> requests.Response:
        return self._send_request(method=HTTPMethods.GET, path=path, **kwargs)

    def delete(self, path: str, **kwargs) -> requests.Response:
        return self._send_request(method=HTTPMethods.DELETE, path=path, **kwargs)

    def _build_headers(self, kwargs):
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            DATA_PARTITION_ID: self.data_partition,
            "Cache-Control": "no-store",
            CORRELATION_ID: f"rafs-ddms/autotest/{uuid.uuid4()}",
        }

        if kwargs.get("headers") is not None:
            headers.update(kwargs.get("headers"))
            kwargs.pop("headers")

        return headers

    @staticmethod
    def _log_response(method, path, response):
        logger.info(f"{linesep}{linesep}============ RESPONSE =============== {linesep}")
        log_msg = f"{method.upper()} {path} {response.headers} - {response.status_code}"
        logger.info(log_msg)

    @staticmethod
    def _handle_error_response(response, allowed_codes):
        response_error = f"\n[ERROR] Response CODE: [{response.status_code}]. EXPECTED CODES: {allowed_codes}"
        response_body = f"\n[ERROR] Response BODY: {response.text}"
        response_url = f"\n[ERROR] Response URL: {response.url}"
        headers_list = [f"{key}: {value}" for key, value in response.headers.items()]  # noqa: WPS110
        headers_str = "\n".join(headers_list)
        response_headers = f"\n[ERROR] Response HEADERS:\n{headers_str}"
        raise AssertionError(f"{response_error}{response_body}{response_url}{response_headers}")

    def _base_request(self, path: str, method: str, allowed_codes: List[int], **kwargs) -> requests.Response:
        """Universal API request sending :param method: api method type
        (get,post, etc.)

        :param path: path
        :type path: str
        :param method: method
        :type method: str
        :param allowed_codes: expected status codes
        :type allowed_codes: List[int]
        :raises APIException: API Exception
        :return: response
        :rtype: requests.Response
        """
        headers = self._build_headers(kwargs)

        request = getattr(requests, method)

        try:
            response = request(self.url, headers=headers, **kwargs)
        except (requests.ConnectionError, requests.HTTPError, requests.Timeout) as error:
            raise APIException("{0}: {1}".format(type(error).__name__, str(error)))

        self._log_response(method, path, response)

        if response.status_code not in allowed_codes:
            self._handle_error_response(response, allowed_codes)

        return response

    def _send_request(
        self,
        method: str,
        path: str,
        **kwargs,
    ) -> requests.Response:
        """Resending API request if API error.

        :param method: API method
        :type method: str
        :param path: path of the endpoint
        :type path: str
        :param allowed_codes: available response codes
        :type allowed_codes: list
        :param retry_attempts: limit of sending retries
        :type retry_attempts: int
        :param retry_delay: seconds between sending
        :type retry_delay: int
        :param kwargs: additional request params
        :type kwargs: dict
        :raises APIException: API Exception
        :return: response
        :rtype: requests.Response
        """
        allowed_codes = [status.HTTP_200_OK]
        if kwargs.get("allowed_codes"):
            allowed_codes = kwargs.get("allowed_codes")
            kwargs.pop("allowed_codes")
        self.url = urljoin(self.host, f"{self.url_prefix}{path}")
        for retry_attempt in range(self.retry_attempts + 1):
            logger.info(f"Sending {method.upper()} request to {path}")
            request_body = kwargs.get("json", kwargs.get("body", ""))
            logger.debug(f"{method.upper()} request body: {request_body}")
            try:
                response = self._base_request(
                    path=path,
                    method=method,
                    allowed_codes=allowed_codes,
                    **kwargs,
                )
            except APIException:
                if retry_attempt < self.retry_attempts:
                    sleep(self.retry_delay)
            else:
                return response

        logger.error(f"{method.upper()} request error: {path}")
        raise APIException("API retry attempts limit reached.")
