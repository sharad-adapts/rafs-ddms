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

from logging import getLogger
from os import linesep
from time import sleep
from typing import List
from urllib.parse import urljoin

import requests
from starlette import status


class APIException(Exception):
    """Error class for manipulating API response results."""


class HTTPMethods(object):
    GET = "get"
    POST = "post"
    DELETE = "delete"


class APIClient(object):
    """Class API client."""

    def __init__(self, host: str, url_prefix: str, data_partition: str, token: str) -> None:
        self.host = host
        self.url_prefix = url_prefix
        self.data_partition = data_partition
        self.token = token
        self.log = getLogger(__name__)
        self.url: str

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
            "data-partition-id": self.data_partition,
            "Cache-Control": "no-store",
            "Accept": "version=1.0.0",
        }

        if kwargs and kwargs.get("headers"):
            headers.update(kwargs.get("headers"))
            kwargs.pop("headers")

        return headers

    def _log_response(self, method, path, response):
        self.log.info(f"{linesep}{linesep}============ RESPONSE =============== {linesep}")
        log_msg = f"{method.upper()} {path} - {response.status_code}"
        self.log.info(log_msg)

    @staticmethod
    def _handle_error_response(response, allowed_codes):
        response_error = f"\n[ERROR] Response code: [{response.status_code}]. EXPECTED CODES: {allowed_codes}"
        response_body = f"\n[ERROR] Response body: {response.text}"
        response_url = f"\n[ERROR] Response URL: {response.url}"
        raise AssertionError(f"{response_error}{response_body}{response_url}")

    def _base_request(self, path: str, method: str, allowed_codes: List[int], **kwargs) -> requests.Response:
        """
        Universal API request sending
        :param method: api method type (get, post, etc.)
        :param allowed_codes: expected status codes
        :param kwargs: additional request params
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
        retry_attempts: int = 3,
        retry_delay: int = 1,
        **kwargs,
    ) -> requests.Response:
        """
        Resending API request if API error
        :param method: API method
        :param path: path of the endpoint
        :param allowed_codes: available response codes
        :param retry_attempts: limit of sending retries
        :param retry_delay: seconds between sending
        :param kwargs: additional request params
        :return: response
        """
        allowed_codes = [status.HTTP_200_OK]
        if kwargs.get("allowed_codes"):
            allowed_codes = kwargs.get("allowed_codes")
            kwargs.pop("allowed_codes")
        self.url = urljoin(self.host, f"{self.url_prefix}{path}")
        for retry_attempt in range(retry_attempts + 1):
            self.log.info(f"Sending {method.upper()} request to {path}")
            request_body = kwargs.get("json", kwargs.get("body", ""))
            self.log.debug(f"{method.upper()} request body: {request_body}")
            try:
                response = self._base_request(
                    path=path,
                    method=method,
                    allowed_codes=allowed_codes,
                    **kwargs,
                )
            except APIException:
                if retry_attempt < retry_attempts:
                    sleep(retry_delay)
            else:
                return response

        self.log.error(f"{method.upper()} request error: {path}")
        raise APIException("API retry attempts limit reached.")
