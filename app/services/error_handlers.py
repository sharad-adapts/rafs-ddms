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

from httpx import HTTPStatusError
from starlette import status

from app.exceptions.exceptions import OsduApiException


def handle_get_version_osdu_api_error(status_error: HTTPStatusError, record_id: str, version: int):
    """Custom handler to catch and reword the error related to a wrong version.

    :param status_error: httpx status error
    :type status_error: HTTPStatusError
    :param record_id: the record id
    :type record_id: str
    :param version: the version
    :type version: int
    :raises OsduApiException: when error from storage is related to version
    :raises status_error.response.raise_for_status: if another unrelated exception is passed is re raised
    """
    try:
        json_response = status_error.response.json()
    except ValueError:
        status_error.response.raise_for_status()

    is_reason_related = json_response["reason"] == "Unknown error happened while restoring the blob"
    is_message_related = json_response["message"] == "Corrupt data"
    is_version_related = is_message_related and is_reason_related
    if status_error.response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR and is_version_related:
        new_error_from_storage_api = {
            "reason": "Version not found",
            "message": f"The version '{version}' can't be found for record {record_id}",
        }
        raise OsduApiException(status_code=status.HTTP_404_NOT_FOUND, detail=new_error_from_storage_api)
    raise status_error.response.raise_for_status()
