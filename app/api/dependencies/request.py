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

import re
from typing import List

from fastapi import Header, HTTPException, Request
from loguru import logger
from starlette import status

from app.exceptions import exceptions
from app.resources.common_headers import ACCEPT, CONTENT_TYPE
from app.resources.mime_types import SupportedMimeTypes


async def get_data_partition_id(request: Request):
    # @TODO review is required.
    # could be replaced by require_data_partition_id
    data_partition_id = request.headers.get("data-partition-id")
    if not data_partition_id:
        reason = "No data-partition-id in headers"
        logger.debug(reason)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=reason,
        )
    return data_partition_id


def require_data_partition_id(
    data_partition_id=Header(
        title="data-partition-id",
        example="opendes",
        description="Specifies the proper data partition id",
    ),
):
    return data_partition_id


def validate_content_type(request: Request, supported_types: List[str]) -> None:
    """Validate content-type.

    :param request: request
    :type request: Request
    :param supported_types: list of suppported mime types
    :type supported_types: List[str]
    :raises exceptions.InvalidHeaderException: if content type was not provided
    :raises exceptions.InvalidHeaderException: if content type is not supported
    """
    try:
        content_type = request.headers[CONTENT_TYPE]
    except KeyError:
        reason = "Content-Type header is required, but was not provided"
        logger.debug(reason)
        raise exceptions.InvalidHeaderException(detail=reason)

    if content_type not in supported_types:
        supported_content_types = f"Please provide one of the next supported content types: {supported_types}"
        reason = f"The provided content-type is not supported. {supported_content_types}"
        logger.debug(reason)
        raise exceptions.InvalidHeaderException(detail=reason)


def validate_bulkdata_content_type(request: Request) -> None:
    """Validate bulk data content-type.

    :param request: request
    :type request: Request
    :raises exceptions.InvalidHeaderException: if content type was not provided
    :raises exceptions.InvalidHeaderException: if content type is not supported
    """
    supported_types = [SupportedMimeTypes.JSON.mime_type, SupportedMimeTypes.PARQUET.mime_type]
    validate_content_type(request=request, supported_types=supported_types)


def validate_json_content_type(request: Request) -> None:
    """Validate generic application/json content-type.

    :param request: request
    :type request: Request
    :raises exceptions.InvalidHeaderException: if content type was not provided
    :raises exceptions.InvalidHeaderException: if content type is not supported
    """
    supported_types = [SupportedMimeTypes.JSON.mime_type]
    validate_content_type(request=request, supported_types=supported_types)


async def get_content_schema_version(request: Request) -> str:
    """Get content schema version from header.

    :param request: request
    :type request: Request
    :raises exceptions.InvalidHeaderException: if schema version hasn't been provided or schema format is invalid
    :return: schema version
    :rtype: str
    """
    accept_header = request.headers[ACCEPT]
    accept_header = accept_header.lower().strip()
    version_regex = r"version=(\d+\.\d+\.\d+)"
    version = re.search(version_regex, accept_header)
    try:
        content_schema_version = version.groups()[0]
    except AttributeError:
        error_title = "No schema version specified or invalid schema format."
        example_detail = "Example: --header 'Accept: */*;version=1.0.0'"
        error_details = f"Check if the schema version is specified in the 'Accept' header. {example_detail}"
        reason = f"{error_title} {error_details}"
        raise exceptions.InvalidHeaderException(detail=reason)
    logger.debug(f"Schema version: {content_schema_version}")
    return content_schema_version
