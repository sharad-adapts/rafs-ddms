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

import copy
import time

import pytest
from starlette import status

from tests.integration.config import CORING_FILE, DATA_STORE


@pytest.mark.smoke
@pytest.mark.dependency(name="test_post_coring")
def test_post_coring(api, tests_data):
    test_data = tests_data(CORING_FILE)
    full_record_id = api.coring.post_coring_data([test_data])["recordIdVersions"][0]

    assert full_record_id.startswith(test_data["id"])

    record_id = ":".join(full_record_id.split(":")[:3])
    version = int(":".join(full_record_id.split(":")[3:]))
    DATA_STORE["coring_record_id"] = record_id
    DATA_STORE["coring_version"] = version


@pytest.mark.smoke
@pytest.mark.dependency(depends=["test_post_coring"])
def test_update_coring(api, tests_data):
    test_data = tests_data(CORING_FILE)
    full_record_id = api.coring.post_coring_data([test_data])["recordIdVersions"][0]
    version = int(":".join(full_record_id.split(":")[3:]))

    assert full_record_id.startswith(test_data["id"])
    assert version > DATA_STORE["coring_version"]

    # save current version as old and overwrite with a new one
    DATA_STORE["old_coring_version"] = DATA_STORE["coring_version"]
    DATA_STORE["coring_version"] = version


@pytest.mark.smoke
def test_failed_record_creation(api, tests_data):
    test_data = tests_data(CORING_FILE)
    json_obj_copy = copy.deepcopy(test_data)
    json_obj_copy["id"] = 1  # invalid id
    api.coring.post_coring_data([json_obj_copy], allowed_codes=[status.HTTP_422_UNPROCESSABLE_ENTITY])


@pytest.mark.smoke
@pytest.mark.dependency(depends=["test_post_coring"])
def test_post_multiple_coring_record(api, helper, tests_data):
    test_data = tests_data(CORING_FILE)
    request_objects = 2
    copies = helper.create_data_copies(test_data, request_objects)

    response = api.coring.post_coring_data(copies)
    record_ids = response["recordIdVersions"]

    assert response["recordCount"] == request_objects

    for record_index, created_record in enumerate(record_ids):
        record_id_parts = created_record.split(":")
        record_id_without_version = ":".join(record_id_parts[:3])

        assert any(el["id"] == record_id_without_version for el in copies)


@pytest.mark.smoke
def test_bulk_records_with_same_record_id(api, tests_data):
    test_data = tests_data(CORING_FILE)
    error = api.coring.post_coring_data([test_data, test_data], allowed_codes=[status.HTTP_400_BAD_REQUEST])

    assert (
        "Cannot update the same record multiple times in the same request"
        in error["message"]
    )


@pytest.mark.smoke
def test_post_multiple_coring_empty_record_body(api, tests_data):
    test_data = tests_data(CORING_FILE)
    error = api.coring.post_coring_data([test_data, {}], allowed_codes=[status.HTTP_422_UNPROCESSABLE_ENTITY])

    assert "Unprocessable entity" in error["reason"]


@pytest.mark.smoke
@pytest.mark.dependency(depends=["test_post_coring"])
def test_get_versions(api):
    test_data = api.coring.get_record_versions(DATA_STORE["coring_record_id"])

    assert test_data["recordId"] == DATA_STORE["coring_record_id"]
    assert test_data["versions"][-1] == DATA_STORE["coring_version"]


@pytest.mark.smoke
def test_get_versions_of_non_existent_record(api):
    timestamp = int(time.time())
    non_existent_id = f"opendes:master-data--Coring:autotest_{timestamp}"
    error = api.coring.get_record_versions(
        non_existent_id,
        allowed_codes=[status.HTTP_404_NOT_FOUND],
    )
    assert f"The record '{non_existent_id}' was not found" in error["message"]


@pytest.mark.smoke
@pytest.mark.dependency(depends=["test_post_coring"])
def test_get_version(api):
    test_data = api.coring.get_version_of_the_record(
        DATA_STORE["coring_record_id"], DATA_STORE["coring_version"],
    )

    assert test_data["id"] == DATA_STORE["coring_record_id"]
    assert test_data["version"] == DATA_STORE["coring_version"]


@pytest.mark.smoke
@pytest.mark.dependency(depends=["test_post_coring"])
def test_get_non_existent_version_of_the_record(api):
    invalid_version = int(time.time())
    error = api.coring.get_version_of_the_record(
        DATA_STORE["coring_record_id"],
        version=int(time.time()),
        allowed_codes=[status.HTTP_404_NOT_FOUND],
    )
    assert (
        f"The version {invalid_version} can't be found for record {DATA_STORE['coring_record_id']}"
        in error["message"]
    )


@pytest.mark.smoke
def test_get_version_of_non_existent_record(api):
    timestamp = int(time.time())
    non_existent_id = f"opendes:master-data--Coring:autotest_{timestamp}"
    error = api.coring.get_version_of_the_record(
        non_existent_id,
        version=int(time.time()),
        allowed_codes=[status.HTTP_404_NOT_FOUND],
    )
    assert f"The record '{non_existent_id}' was not found" in error["message"]


@pytest.mark.smoke
@pytest.mark.dependency(depends=["test_post_coring"])
def test_get_coring_record(api):
    coring_record = api.coring.get_coring_data(DATA_STORE["coring_record_id"])

    assert coring_record["id"] == DATA_STORE["coring_record_id"]
    assert coring_record["version"] == DATA_STORE["coring_version"]


@pytest.mark.smoke
def test_get_non_existent_coring_record(api):
    timestamp = int(time.time())
    non_existent_id = f"opendes:master-data--Coring:autotest_{timestamp}"
    error = api.coring.get_coring_data(non_existent_id, allowed_codes=[status.HTTP_404_NOT_FOUND])

    assert f"The record '{non_existent_id}' was not found" in error["message"]


@pytest.mark.smoke
@pytest.mark.dependency(depends=["test_post_coring"])
def test_delete_coring_record(api):
    # status code check is implemented on the API client layer
    api.coring.soft_delete_record(DATA_STORE["coring_record_id"], allowed_codes=[status.HTTP_204_NO_CONTENT])
    api.coring.get_coring_data(DATA_STORE["coring_record_id"], allowed_codes=[status.HTTP_404_NOT_FOUND])


@pytest.mark.smoke
def test_delete_non_existent_record(api):
    # status code check is implemented on the API client layer
    timestamp = int(time.time())
    api.coring.soft_delete_record(
        f"opendes:master-data--Coring:autotest_{timestamp}",
        allowed_codes=[status.HTTP_404_NOT_FOUND],
    )
