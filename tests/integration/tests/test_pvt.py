#  Copyright 2023 ExxonMobil Technology and Engineering Company
#
import copy
import time

import pytest
from starlette import status

from app.resources.common_headers import CONTENT_TYPE
from app.resources.mime_types import CustomMimeTypes
from tests.integration.config import DATA_STORE, PVT_FILE, UPLOADED_FILES

ID_PVT_TEMPLATE = "opendes:work-product-component--PVT:"


@pytest.mark.smoke
@pytest.mark.dependency(name="test_post_pvt")
def test_post_pvt(api, tests_data):
    test_data = tests_data(PVT_FILE)
    full_record_id = api.pvt.post_pvt_data([test_data])["recordIdVersions"][0]

    assert full_record_id.startswith(test_data["id"])

    record_id = ":".join(full_record_id.split(":")[:3])
    version = int(":".join(full_record_id.split(":")[3:]))
    DATA_STORE["pvt_record_id"] = record_id
    DATA_STORE["pvt_version"] = version


@pytest.mark.smoke
@pytest.mark.dependency(depends=["test_post_pvt"])
def test_update_pvt(api, tests_data):
    test_data = tests_data(PVT_FILE)
    full_record_id = api.pvt.post_pvt_data([test_data])["recordIdVersions"][0]
    version = int(":".join(full_record_id.split(":")[3:]))

    assert full_record_id.startswith(test_data["id"])
    assert version > DATA_STORE["pvt_version"]

    # save current version as old and overwrite with a new one
    DATA_STORE["old_pvt_version"] = DATA_STORE["pvt_version"]
    DATA_STORE["pvt_version"] = version


@pytest.mark.parametrize(
    "case, test, record_id", [
        ("Deleted", "ConstantVolumeDepletionTestID", "deleted_test_for_automation"),
        ("Not_existent", "ConstantVolumeDepletionTestID", "not_existent"),
    ],
)
@pytest.mark.smoke
def test_pvt_test_not_found(api, tests_data, case, test, record_id):
    test_data = tests_data(PVT_FILE)
    json_obj_copy = copy.deepcopy(test_data)
    json_obj_copy["data"]["PVTTests"][test] = [
        f"opendes:work-product-component--ConstantVolumeDepletionTest:{record_id}:",
    ]

    error = api.pvt.post_pvt_data([json_obj_copy], allowed_codes=[status.HTTP_422_UNPROCESSABLE_ENTITY])
    assert "Records not found" in error["reason"]


@pytest.mark.smoke
def test_failed_record_creation(api, tests_data):
    test_data = tests_data(PVT_FILE)
    json_obj_copy = copy.deepcopy(test_data)
    json_obj_copy["id"] = 1  # invalid id
    api.pvt.post_pvt_data([json_obj_copy], allowed_codes=[status.HTTP_422_UNPROCESSABLE_ENTITY])


@pytest.mark.smoke
@pytest.mark.dependency(depends=["test_post_pvt"])
def test_post_multiple_pvt_record(api, helper, tests_data):
    test_data = tests_data(PVT_FILE)
    request_objects = 2
    copies = helper.create_data_copies(test_data, request_objects)

    response = api.pvt.post_pvt_data(copies)
    record_ids = response["recordIdVersions"]

    assert response["recordCount"] == request_objects

    for record_index, created_record in enumerate(record_ids):
        record_id_parts = created_record.split(":")
        record_id_without_version = ":".join(record_id_parts[:3])

        assert any(el["id"] == record_id_without_version for el in copies)


@pytest.mark.smoke
def test_post_multiple_pvt_with_the_same_record_id(api, tests_data):
    test_data = tests_data(PVT_FILE)
    error = api.pvt.post_pvt_data([test_data, test_data], allowed_codes=[status.HTTP_400_BAD_REQUEST])

    assert (
        "Cannot update the same record multiple times in the same request"
        in error["message"]
    )


@pytest.mark.smoke
def test_post_multiple_pvt_empty_record_body(api, tests_data):
    test_data = tests_data(PVT_FILE)
    error = api.pvt.post_pvt_data([test_data, {}], allowed_codes=[status.HTTP_422_UNPROCESSABLE_ENTITY])

    assert "Unprocessable entity" in error["reason"]


@pytest.mark.smoke
@pytest.mark.dependency(depends=["test_post_pvt"])
def test_get_versions(api):
    test_data = api.pvt.get_record_versions(DATA_STORE["pvt_record_id"])

    assert test_data["recordId"] == DATA_STORE["pvt_record_id"]
    assert test_data["versions"][-1] == DATA_STORE["pvt_version"]


@pytest.mark.smoke
def test_get_versions_of_non_existent_record(api):
    timestamp = int(time.time())
    non_existent_id = f"{ID_PVT_TEMPLATE}autotest_{timestamp}"
    error = api.pvt.get_record_versions(
        non_existent_id,
        allowed_codes=[status.HTTP_404_NOT_FOUND],
    )
    assert f"The record '{non_existent_id}' was not found" in error["message"]


@pytest.mark.smoke
@pytest.mark.dependency(depends=["test_post_pvt"])
def test_get_version(api):
    test_data = api.pvt.get_version_of_the_record(
        DATA_STORE["pvt_record_id"], DATA_STORE["pvt_version"],
    )

    assert test_data["id"] == DATA_STORE["pvt_record_id"]
    assert test_data["version"] == DATA_STORE["pvt_version"]


@pytest.mark.smoke
@pytest.mark.dependency(depends=["test_post_pvt"])
def test_get_non_existent_version_of_the_record(api):
    invalid_version = int(time.time())
    error = api.pvt.get_version_of_the_record(
        DATA_STORE["pvt_record_id"],
        version=int(time.time()),
        allowed_codes=[status.HTTP_404_NOT_FOUND],
    )
    assert (
        f"The version {invalid_version} can't be found for record {DATA_STORE['pvt_record_id']}"
        in error["message"]
    )


@pytest.mark.smoke
def test_get_version_of_non_existent_record(api):
    timestamp = int(time.time())
    non_existent_id = f"{ID_PVT_TEMPLATE}autotest_{timestamp}"
    error = api.pvt.get_version_of_the_record(
        non_existent_id,
        version=int(time.time()),
        allowed_codes=[status.HTTP_404_NOT_FOUND],
    )
    assert f"The record '{non_existent_id}' was not found" in error["message"]


@pytest.mark.smoke
@pytest.mark.dependency(depends=["test_post_pvt"])
def test_get_pvt_record(api):
    record = api.pvt.get_pvt_data(DATA_STORE["pvt_record_id"])

    assert record["id"] == DATA_STORE["pvt_record_id"]
    assert record["version"] == DATA_STORE["pvt_version"]


@pytest.mark.smoke
def test_get_non_existent_pvt_record(api):
    timestamp = int(time.time())
    non_existent_id = f"{ID_PVT_TEMPLATE}autotest_{timestamp}"
    error = api.pvt.get_pvt_data(non_existent_id, allowed_codes=[status.HTTP_404_NOT_FOUND])

    assert f"The record '{non_existent_id}' was not found" in error["message"]


@pytest.mark.smoke
@pytest.mark.dependency(depends=["test_post_pvt"])
def test_get_source_zip_file(api, tests_data):
    test_data = tests_data(PVT_FILE)
    pvt_copy = copy.deepcopy(test_data)
    pvt_copy["id"] = f"{ID_PVT_TEMPLATE}FileRecord"
    pvt_copy["data"]["Datasets"] = UPLOADED_FILES

    api.pvt.post_pvt_data([pvt_copy])

    response = api.pvt.get_pvt_file(pvt_copy["id"])
    assert response.headers[CONTENT_TYPE] == CustomMimeTypes.ZIP.type
    assert "attachment;filename=datasets.zip" in response.headers["Content-Disposition"]


@pytest.mark.smoke
@pytest.mark.dependency(depends=["test_post_pvt"])
def test_get_source_single_file(api, tests_data):
    test_data = tests_data(PVT_FILE)
    pvt_copy = copy.deepcopy(test_data)
    pvt_copy["id"] = f"{ID_PVT_TEMPLATE}FileRecord"
    pvt_copy["data"]["Datasets"] = [UPLOADED_FILES[0]]

    api.pvt.post_pvt_data([pvt_copy])

    response = api.pvt.get_pvt_file(pvt_copy["id"])
    assert "application/" in response.headers["Content-Type"]
    assert "attachment;filename=" in response.headers["Content-Disposition"]


@pytest.mark.smoke
@pytest.mark.dependency(depends=["test_post_pvt"])
def test_get_source_file_not_uploaded(api, tests_data):
    test_data = tests_data(PVT_FILE)
    pvt_copy = copy.deepcopy(test_data)
    pvt_copy["id"] = f"{ID_PVT_TEMPLATE}FileRecord"
    pvt_copy["data"]["Datasets"] = ["opendes:dataset--File.Generic:not_uploaded:"]

    api.pvt.post_pvt_data([pvt_copy])

    response = api.pvt.get_pvt_file(pvt_copy["id"], allowed_codes=[status.HTTP_404_NOT_FOUND])
    assert "The record 'opendes:dataset--File.Generic:not_uploaded' was not found" in response.text


@pytest.mark.smoke
@pytest.mark.dependency(depends=["test_post_pvt"])
def test_get_empty_source_dataset(api):
    response = api.pvt.get_pvt_file(DATA_STORE["pvt_record_id"], allowed_codes=[status.HTTP_404_NOT_FOUND])
    assert response.text == '{"message":"entity has no source data"}'


@pytest.mark.smoke
def test_get_dataset_file_wrong_record_id(api):
    timestamp = int(time.time())
    full_id = f"opendes:work-product-component--Coring:autotest_{timestamp}"
    response = api.pvt.get_pvt_file(full_id, allowed_codes=[status.HTTP_422_UNPROCESSABLE_ENTITY])
    assert "PVT ID is not provided in expected OSDU pattern" in response.text


def test_get_source_with_non_existent_pvt_id(api):
    timestamp = int(time.time())
    full_id = f"{ID_PVT_TEMPLATE}autotest_{timestamp}"
    error = api.pvt.get_pvt_file(
        full_id,
        allowed_codes=[status.HTTP_404_NOT_FOUND],
    )

    assert f"'{full_id}' was not found" in error.text


@pytest.mark.smoke
@pytest.mark.dependency(depends=["test_post_pvt"])
def test_delete_pvt_record(api):
    # status code check is implemented on the API client layer
    api.pvt.soft_delete_record(DATA_STORE["pvt_record_id"], allowed_codes=[status.HTTP_204_NO_CONTENT])
    api.pvt.get_pvt_data(DATA_STORE["pvt_record_id"], allowed_codes=[status.HTTP_404_NOT_FOUND])


@pytest.mark.smoke
def test_delete_non_existent_record(api):
    # status code check is implemented on the API client layer
    timestamp = int(time.time())
    api.pvt.soft_delete_record(
        f"{ID_PVT_TEMPLATE}autotest_{timestamp}",
        allowed_codes=[status.HTTP_404_NOT_FOUND],
    )
