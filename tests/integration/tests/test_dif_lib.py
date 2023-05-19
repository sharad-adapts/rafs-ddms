#  Copyright 2023 ExxonMobil Technology and Engineering Company
#
import copy
import json
import os
import time

import pytest
from starlette import status

from tests.integration.config import (
    DATA_DIR,
    DATA_STORE,
    DIF_LIB_DATA_FILE,
    DIF_LIB_FILE,
)

ID_TEMPLATE = "opendes:work-product-component--DifferentialLiberationTest:"


@pytest.mark.smoke
@pytest.mark.dependency(name="test_post_dif_lib")
def test_post_dif_lib(api, tests_data):
    test_data = tests_data(DIF_LIB_FILE)
    full_record_id = [el for el in api.dif_lib.post_dif_lib_data([test_data])["recordIdVersions"] if "PVT" not in el][0]

    assert full_record_id.startswith(test_data["id"])

    record_id = ":".join(full_record_id.split(":")[:3])
    version = int(":".join(full_record_id.split(":")[3:]))
    DATA_STORE["df_record_id"] = record_id
    DATA_STORE["df_version"] = version


@pytest.mark.smoke
@pytest.mark.dependency(depends=["test_post_dif_lib"])
def test_update_dif_lib(api, tests_data):
    test_data = tests_data(DIF_LIB_FILE)
    full_record_id = [el for el in api.dif_lib.post_dif_lib_data([test_data])["recordIdVersions"] if "PVT" not in el][0]
    version = int(":".join(full_record_id.split(":")[3:]))

    assert full_record_id.startswith(test_data["id"])
    assert version > DATA_STORE["df_version"]

    # save current version as old and overwrite with a new one
    DATA_STORE["old_df_version"] = DATA_STORE["df_version"]
    DATA_STORE["df_version"] = version


@pytest.mark.smoke
def test_failed_record_creation(api, tests_data):
    test_data = tests_data(DIF_LIB_FILE)
    json_obj_copy = copy.deepcopy(test_data)
    json_obj_copy["id"] = 1  # invalid id
    api.dif_lib.post_dif_lib_data([json_obj_copy], allowed_codes=[status.HTTP_422_UNPROCESSABLE_ENTITY])


def test_pvt_report_id_is_required(api, tests_data):
    test_data = tests_data(DIF_LIB_FILE)
    json_obj_copy = copy.deepcopy(test_data)
    del json_obj_copy["data"]["PVTReportID"]

    error = api.dif_lib.post_dif_lib_data([json_obj_copy], allowed_codes=[status.HTTP_422_UNPROCESSABLE_ENTITY])
    assert "errors=[{'loc': ('data', 'PVTReportID'), 'msg': 'field required'" in error["reason"]


@pytest.mark.smoke
@pytest.mark.dependency(depends=["test_post_dif_lib"])
def test_post_multiple_dif_lib_record(api, helper, tests_data):
    test_data = tests_data(DIF_LIB_FILE)
    request_objects = 2
    copies = helper.create_data_copies(test_data, request_objects)

    response = api.dif_lib.post_dif_lib_data(copies)
    record_ids = response["recordIdVersions"]

    assert response["recordCount"] == request_objects + 1  # + updated pvt record

    for record_index, created_record in enumerate(record_ids):
        if "PVT" not in created_record:
            record_id_parts = created_record.split(":")
            record_id_without_version = ":".join(record_id_parts[:3])

            assert any(el["id"] == record_id_without_version for el in copies)


@pytest.mark.smoke
def test_bulk_records_with_same_record_id(api, tests_data):
    test_data = tests_data(DIF_LIB_FILE)
    error = api.dif_lib.post_dif_lib_data([test_data, test_data], allowed_codes=[status.HTTP_400_BAD_REQUEST])

    assert (
        "Cannot update the same record multiple times in the same request"
        in error["message"]
    )


@pytest.mark.smoke
def test_post_multiple_dif_lib_empty_record_body(api, tests_data):
    test_data = tests_data(DIF_LIB_FILE)
    error = api.dif_lib.post_dif_lib_data([test_data, {}], allowed_codes=[status.HTTP_422_UNPROCESSABLE_ENTITY])

    assert "Unprocessable entity" in error["reason"]


@pytest.mark.smoke
@pytest.mark.dependency(depends=["test_post_dif_lib"])
def test_get_versions(api):
    test_data = api.dif_lib.get_record_versions(DATA_STORE["df_record_id"])

    assert test_data["recordId"] == DATA_STORE["df_record_id"]
    assert test_data["versions"][-1] == DATA_STORE["df_version"]


@pytest.mark.smoke
def test_get_versions_of_non_existent_record(api):
    timestamp = int(time.time())
    non_existent_id = f"{ID_TEMPLATE}autotest_{timestamp}"
    error = api.dif_lib.get_record_versions(
        non_existent_id,
        allowed_codes=[status.HTTP_404_NOT_FOUND],
    )
    assert f"The record '{non_existent_id}' was not found" in error["message"]


@pytest.mark.smoke
@pytest.mark.dependency(depends=["test_post_dif_lib"])
def test_get_version(api):
    test_data = api.dif_lib.get_version_of_the_record(
        DATA_STORE["df_record_id"], DATA_STORE["df_version"],
    )

    assert test_data["id"] == DATA_STORE["df_record_id"]
    assert test_data["version"] == DATA_STORE["df_version"]


@pytest.mark.smoke
@pytest.mark.dependency(depends=["test_post_dif_lib"])
def test_get_non_existent_version_of_the_record(api):
    invalid_version = int(time.time())
    error = api.dif_lib.get_version_of_the_record(
        DATA_STORE["df_record_id"],
        version=int(time.time()),
        allowed_codes=[status.HTTP_404_NOT_FOUND],
    )
    assert (
        f"The version {invalid_version} can't be found for record {DATA_STORE['df_record_id']}"
        in error["message"]
    )


@pytest.mark.smoke
def test_get_version_of_non_existent_record(api):
    timestamp = int(time.time())
    non_existent_id = f"{ID_TEMPLATE}autotest_{timestamp}"
    error = api.dif_lib.get_version_of_the_record(
        non_existent_id,
        version=int(time.time()),
        allowed_codes=[status.HTTP_404_NOT_FOUND],
    )
    assert f"The record '{non_existent_id}' was not found" in error["message"]


@pytest.mark.smoke
@pytest.mark.dependency(depends=["test_post_dif_lib"])
def test_get_dif_lib_record(api):
    df_record = api.dif_lib.get_dif_lib_data(DATA_STORE["df_record_id"])

    assert df_record["id"] == DATA_STORE["df_record_id"]
    assert df_record["version"] == DATA_STORE["df_version"]


@pytest.mark.smoke
def test_get_non_existent_dif_lib_record(api):
    timestamp = int(time.time())
    non_existent_id = f"{ID_TEMPLATE}autotest_{timestamp}"
    error = api.dif_lib.get_dif_lib_data(non_existent_id, allowed_codes=[status.HTTP_404_NOT_FOUND])

    assert f"The record '{non_existent_id}' was not found" in error["message"]


@pytest.mark.smoke
@pytest.mark.dependency(depends=["test_post_dif_lib"])
def test_post_measurements(api, helper):
    with open(os.path.join(DATA_DIR, DIF_LIB_DATA_FILE)) as json_file:
        dif_lib_data = json.load(json_file)

    response = api.dif_lib.post_measurements(DATA_STORE["df_record_id"], dif_lib_data)
    assert "dataset--File.Generic:differential-liberation" in response["ddms_urn"]
    DATA_STORE["dif_lib_dataset_id"] = helper.get_dataset_id_from_ddms_urn(response["ddms_urn"])

    record = api.dif_lib.get_dif_lib_data(DATA_STORE["df_record_id"])
    assert "DDMSDatasets" in record["data"]


@pytest.mark.smoke
def test_post_measurements_non_existent_df_id(api):
    with open(os.path.join(DATA_DIR, DIF_LIB_DATA_FILE)) as json_file:
        dif_lib_data = json.load(json_file)

    timestamp = int(time.time())
    api.dif_lib.post_measurements(
        f"{ID_TEMPLATE}autotest_{timestamp}",
        dif_lib_data,
        allowed_codes=[status.HTTP_404_NOT_FOUND],
    )


@pytest.mark.xfail(reason="XOMROCK-548")
@pytest.mark.dependency(depends=["test_post_dif_lib"])
def test_post_measurements_with_empty_body(api):
    error = api.dif_lib.post_measurements(
        DATA_STORE["df_record_id"],
        {"columns": [], "index": [], "data": []},
        allowed_codes=[status.HTTP_422_UNPROCESSABLE_ENTITY],
    )

    assert error["reason"] == "Data validation failed."
    assert error["errors"] == {
        "Mandatory parameters missing": [
            "DifferentialLiberationTestID",
        ],
    }


@pytest.mark.xfail(reason="XOMROCK-746")
@pytest.mark.dependency(depends=["test_post_dif_lib"])
def test_post_measurements_validation_failed(api):
    with open(os.path.join(DATA_DIR, "dif_lib_wrong_ids.json")) as json_file:
        dif_lib_data = json.load(json_file)

    error = api.dif_lib.post_measurements(
        DATA_STORE["df_record_id"],
        dif_lib_data,
        allowed_codes=[status.HTTP_422_UNPROCESSABLE_ENTITY],
    )

    expected_errors = {
        "opendes:reference-data--PressureMeasurementType:WrongID2",
        "opendes:work-product-component--DifferentialLiberationTest:WrongID",
        "opendes:master-data--FluidSample:WrongID",
    }

    assert error["reason"] == "Data validation failed."
    assert expected_errors == set(error["errors"]["Missing records in storage"])


@pytest.mark.smoke
@pytest.mark.dependency(depends=["test_post_dif_lib"])
def test_get_measurements_as_json(api):
    dif_lib_data = api.dif_lib.get_measurements(DATA_STORE["df_record_id"], DATA_STORE["dif_lib_dataset_id"])

    assert isinstance(dif_lib_data, dict)

    assert "columns" in dif_lib_data and dif_lib_data["columns"]
    assert "index" in dif_lib_data and dif_lib_data["index"]
    assert "data" in dif_lib_data and dif_lib_data["data"]


@pytest.mark.smoke
@pytest.mark.dependency(depends=["test_post_dif_lib"])
def test_delete_dif_lib_record(api):
    # status code check is implemented on the API client layer
    api.dif_lib.soft_delete_record(DATA_STORE["df_record_id"], allowed_codes=[status.HTTP_204_NO_CONTENT])
    api.dif_lib.get_dif_lib_data(DATA_STORE["df_record_id"], allowed_codes=[status.HTTP_404_NOT_FOUND])


@pytest.mark.smoke
def test_delete_non_existent_record(api):
    # status code check is implemented on the API client layer
    timestamp = int(time.time())
    api.dif_lib.soft_delete_record(
        f"{ID_TEMPLATE}autotest_{timestamp}",
        allowed_codes=[status.HTTP_404_NOT_FOUND],
    )
