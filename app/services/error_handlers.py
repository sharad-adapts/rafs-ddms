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

import functools
import json

from httpx import HTTPStatusError
from loguru import logger
from starlette import status

from app.exceptions.exceptions import OsduApiException

OSDU_API_ERROR_DETAIL = "OSDU service API request failed."


def get_reason(status_error: HTTPStatusError, detail: str) -> dict:
    """Get the reason object.

    :param status_error: status error object
    :type status_error: HTTPStatusError
    :param detail: custom description of the reason
    :type detail: str
    :return: the reason object
    :rtype: dict
    """
    try:
        reason = status_error.response.json()
    except json.decoder.JSONDecodeError:
        reason = {
            "code": status_error.response.status_code,
            "reason": detail,
            "message": status_error.response.text,
        }
    return reason


def handle_core_services_http_status_error(expected_codes: list[int], detail: str = OSDU_API_ERROR_DETAIL):
    """Decorator to catch errors from osdu services, log them, and raise
    generic service exceptions if unexpected error received.

    :param expected_codes: list of expected error codes
    :type expected_codes: list
    :param detail: error details
    :type detail: str
    :raises OsduApiException: when error from OSDU service has unexpected status code
    :raises status_error.response.raise_for_status: if status code is expected
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except HTTPStatusError as status_error:
                reason = get_reason(status_error, detail)
                logger.error(reason)
                if status_error.response.status_code not in expected_codes:
                    raise OsduApiException(
                        status_code=status.HTTP_424_FAILED_DEPENDENCY,
                        detail=json.dumps(reason),
                    )
                else:
                    status_error.response.raise_for_status()
        return wrapper
    return decorator
