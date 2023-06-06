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

import json
from unittest.mock import MagicMock

import httpx
import pytest
from httpx import HTTPStatusError
from starlette import status

from app.core.config import get_app_settings
from app.exceptions.exceptions import OsduApiException
from app.models.schemas.user import User
from app.services.osdu_clients.storage_client import StorageServiceApiClient
from app.services.storage import StorageService
from tests.test_api.test_routes.osdu.storage_mock_objects import (
    OSDU_GENERIC_RECORD,
)


@pytest.fixture
def mock_record_client():
    mock_client = MagicMock(spec=StorageServiceApiClient, instance=True)
    yield mock_client


@pytest.fixture
def mock_user():
    mock_user = MagicMock(spec=User)
    mock_user.access_token = "test_token"
    yield mock_user


@pytest.fixture
def storage_service(mock_user):
    data_partition_id = "test_partition"
    yield StorageService(data_partition_id, get_app_settings(), mock_user)


@pytest.fixture
def mock_get_response(mock_record_client, storage_service):
    response_json = OSDU_GENERIC_RECORD.dict(exclude_none=True)
    mock_record_client.client = MagicMock(spec=httpx.AsyncClient)
    mock_record_client.get_latest_record.return_value = response_json
    mock_record_client.get_specific_record.return_value = response_json
    storage_service.storage_client = mock_record_client
    yield


@pytest.fixture
def mock_get_500_wrong_version_response(mock_record_client, storage_service):
    json_response = {
        "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "reason": "Unknown error happened while restoring the blob",
        "message": "Corrupt data",
    }

    class Response(object):
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        text = json.dumps(json_response)
        def json(_): return json_response

    mock_record_client.client = MagicMock(spec=httpx.AsyncClient)
    mock_record_client.get_specific_record.side_effect = HTTPStatusError(
        message="", request=object(), response=Response(),
    )
    storage_service.storage_client = mock_record_client
    yield


@pytest.mark.asyncio
async def test_get_latest_record(storage_service, mock_record_client, mock_user, mock_get_response):
    record_id = "test-id"

    record = await storage_service.get_record(record_id)

    assert record == OSDU_GENERIC_RECORD.dict(exclude_none=True)
    mock_record_client.get_latest_record.assert_called_once_with(record_id)


@pytest.mark.asyncio
async def test_get_specific_record(storage_service, mock_record_client, mock_user, mock_get_response):
    record_id = "test-id"
    version = 1

    record = await storage_service.get_record(record_id, version)

    assert record == OSDU_GENERIC_RECORD.dict(exclude_none=True)
    mock_record_client.get_specific_record.assert_called_once_with(
        record_id, version,
    )


@pytest.mark.asyncio
async def test_get_record_versions(storage_service, mock_record_client, mock_user):
    record_id = "test_id"
    version = 1
    response_json = {
        "recordId": record_id,
        "versions": [version],
    }
    mock_record_client.get_record_versions.return_value = response_json
    storage_service.storage_client = mock_record_client

    record = await storage_service.get_record_versions(record_id)

    assert record == response_json
    mock_record_client.get_record_versions.assert_called_once_with(record_id)


@pytest.mark.asyncio
async def test_upsert_records(storage_service, mock_record_client, mock_user):
    records = [OSDU_GENERIC_RECORD.dict(exclude_none=True)]
    response_json = {
        "recordCount": 1,
        "recordIds": [
            "test-id",
        ],
        "skippedRecordIds": [],
        "recordIdVersions": [
            "test-id:1",
        ],
    }
    mock_record_client.create_update_records.return_value = response_json
    storage_service.storage_client = mock_record_client

    record = await storage_service.upsert_records(records)

    assert record == response_json
    mock_record_client.create_update_records.assert_called_with(records)


@pytest.mark.asyncio
async def test_soft_delete_record(storage_service, mock_record_client, mock_user):
    record_id = "test_id"
    mock_record_client.soft_delete_record.return_value = None
    mock_record_client.storage_url = "https://test-url"
    storage_service.storage_client = mock_record_client

    assert await storage_service.soft_delete_record(record_id) is None

    mock_record_client.soft_delete_record.assert_called_once_with(record_id)


@pytest.mark.asyncio
async def test_get_specific_record_raises_404(storage_service, mock_record_client, mock_user, mock_get_500_wrong_version_response):
    record_id = "test-id"
    version = 1

    with pytest.raises(OsduApiException) as exc:
        await storage_service.get_record(record_id, version)

    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc.value.detail.get("message") == f"The version '{version}' can't be found for record {record_id}"
    assert exc.value.detail.get("reason") == "Version not found"
