#  Copyright 2023 ExxonMobil Technology and Engineering Company
#
import copy
import json
import os
import time

import pytest
from starlette import status

from tests.integration.config import (
    CCE_DATA_FILE,
    CCE_FILE,
    DATA_DIR,
    DATA_STORE,
)
from tests.integration.tests.test_pvt import ID_PVT_TEMPLATE

ID_TEMPLATE = "opendes:work-product-component--ConstantCompositionExpansionTest:"


@pytest.mark.smoke
@pytest.mark.dependency(name="test_post_cce")
def test_post_cce(api, tests_data, create_pvt):
    test_data = tests_data(CCE_FILE)

    test_data["data"]["PVTReportID"] = f"{create_pvt['id']}:"
    full_record_id = [el for el in api.cce.post_cce_data([test_data])["recordIdVersions"] if "PVT" not in el][0]

    assert full_record_id.startswith(test_data["id"])

    record_id = ":".join(full_record_id.split(":")[:3])
    version = int(":".join(full_record_id.split(":")[3:]))
    DATA_STORE["cce_record_id"] = record_id
    DATA_STORE["cce_version"] = version

    # check that CCE test has been linked to the PVT record after creation of CCE test
    pvt_report = api.pvt.get_pvt_data(create_pvt["id"])
    assert pvt_report["data"]["PVTTests"]["ConstantCompositionExpansionTestID"][0] == f"{record_id}:"


@pytest.mark.smoke
@pytest.mark.dependency(depends=["test_post_cce"])
def test_update_cce(api, tests_data):
    test_data = tests_data(CCE_FILE)
    full_record_id = [el for el in api.cce.post_cce_data([test_data])["recordIdVersions"] if "PVT" not in el][0]
    version = int(":".join(full_record_id.split(":")[3:]))

    assert full_record_id.startswith(test_data["id"])
    assert version > DATA_STORE["cce_version"]

    # save current version as old and overwrite with a new one
    DATA_STORE["old_cce_version"] = DATA_STORE["cce_version"]
    DATA_STORE["cce_version"] = version


@pytest.mark.smoke
def test_failed_record_creation(api, tests_data):
    test_data = tests_data(CCE_FILE)
    json_obj_copy = copy.deepcopy(test_data)
    json_obj_copy["id"] = 1  # invalid id
    api.cce.post_cce_data([json_obj_copy], allowed_codes=[status.HTTP_422_UNPROCESSABLE_ENTITY])


@pytest.mark.smoke
@pytest.mark.dependency(depends=["test_post_cce"])
def test_post_multiple_cce_record(api, helper, tests_data):
    test_data = tests_data(CCE_FILE)
    request_objects = 2
    copies = helper.create_data_copies(test_data, request_objects)

    response = api.cce.post_cce_data(copies)
    record_ids = response["recordIdVersions"]

    assert response["recordCount"] == request_objects + 1  # + updated pvt record

    for record_index, created_record in enumerate(record_ids):
        if "PVT" not in created_record:
            record_id_parts = created_record.split(":")
            record_id_without_version = ":".join(record_id_parts[:3])

            assert any(el["id"] == record_id_without_version for el in copies)


@pytest.mark.smoke
def test_post_multiple_cce_same_record_id(api, tests_data):
    test_data = tests_data(CCE_FILE)
    error = api.cce.post_cce_data([test_data, test_data], allowed_codes=[status.HTTP_400_BAD_REQUEST])

    assert (
        "Cannot update the same record multiple times in the same request"
        in error["message"]
    )


@pytest.mark.parametrize(
    "case, record_id", [
        ("Deleted", "deleted_test_for_automation"),
        ("Not_existent", "not_existent"),
    ],
)
@pytest.mark.smoke
def test_pvt_report_id_not_found(api, tests_data, case, record_id):
    test_data = tests_data(CCE_FILE)
    json_obj_copy = copy.deepcopy(test_data)
    record = f"{ID_PVT_TEMPLATE}{record_id}"
    json_obj_copy["data"]["PVTReportID"] = record + ":"

    error = api.cce.post_cce_data([json_obj_copy], allowed_codes=[status.HTTP_422_UNPROCESSABLE_ENTITY])
    assert error["reason"] == f"Parent records ['{record}'] not found."


def test_pvt_report_id_is_required(api, tests_data):
    test_data = tests_data(CCE_FILE)
    json_obj_copy = copy.deepcopy(test_data)
    del json_obj_copy["data"]["PVTReportID"]

    error = api.cce.post_cce_data([json_obj_copy], allowed_codes=[status.HTTP_422_UNPROCESSABLE_ENTITY])
    assert "errors=[{'loc': ('data', 'PVTReportID'), 'msg': 'field required'" in error["reason"]


@pytest.mark.smoke
def test_post_multiple_cce_empty_record_body(api, tests_data):
    test_data = tests_data(CCE_FILE)
    error = api.cce.post_cce_data([test_data, {}], allowed_codes=[status.HTTP_422_UNPROCESSABLE_ENTITY])

    assert "Unprocessable entity" in error["reason"]


@pytest.mark.smoke
@pytest.mark.dependency(depends=["test_post_cce"])
def test_get_versions(api):
    test_data = api.cce.get_record_versions(DATA_STORE["cce_record_id"])

    assert test_data["recordId"] == DATA_STORE["cce_record_id"]
    assert test_data["versions"][-1] == DATA_STORE["cce_version"]


@pytest.mark.smoke
def test_get_versions_of_non_existent_record(api):
    timestamp = int(time.time())
    non_existent_id = f"{ID_TEMPLATE}autotest_{timestamp}"
    error = api.cce.get_record_versions(
        non_existent_id,
        allowed_codes=[status.HTTP_404_NOT_FOUND],
    )
    assert f"The record '{non_existent_id}' was not found" in error["message"]


@pytest.mark.smoke
@pytest.mark.dependency(depends=["test_post_cce"])
def test_get_version(api):
    test_data = api.cce.get_version_of_the_record(
        DATA_STORE["cce_record_id"], DATA_STORE["cce_version"],
    )

    assert test_data["id"] == DATA_STORE["cce_record_id"]
    assert test_data["version"] == DATA_STORE["cce_version"]


@pytest.mark.smoke
@pytest.mark.dependency(depends=["test_post_cce"])
def test_get_non_existent_version_of_the_record(api):
    invalid_version = int(time.time())
    error = api.cce.get_version_of_the_record(
        DATA_STORE["cce_record_id"],
        version=int(time.time()),
        allowed_codes=[status.HTTP_404_NOT_FOUND],
    )
    assert (
        f"The version {invalid_version} can't be found for record {DATA_STORE['cce_record_id']}"
        in error["message"]
    )


@pytest.mark.smoke
def test_get_version_of_non_existent_record(api):
    timestamp = int(time.time())
    non_existent_id = f"{ID_TEMPLATE}autotest_{timestamp}"
    error = api.cce.get_version_of_the_record(
        non_existent_id,
        version=int(time.time()),
        allowed_codes=[status.HTTP_404_NOT_FOUND],
    )
    assert f"The record '{non_existent_id}' was not found" in error["message"]


@pytest.mark.smoke
@pytest.mark.dependency(depends=["test_post_cce"])
def test_get_cce_record(api):
    record = api.cce.get_cce_data(DATA_STORE["cce_record_id"])

    assert record["id"] == DATA_STORE["cce_record_id"]
    assert record["version"] == DATA_STORE["cce_version"]
    assert "Artefacts" not in record["data"]


@pytest.mark.smoke
def test_get_non_existent_cce_record(api):
    timestamp = int(time.time())
    non_existent_id = f"{ID_TEMPLATE}autotest_{timestamp}"
    error = api.cce.get_cce_data(non_existent_id, allowed_codes=[status.HTTP_404_NOT_FOUND])

    assert f"The record '{non_existent_id}' was not found" in error["message"]


@pytest.mark.smoke
@pytest.mark.dependency(depends=["test_post_cce"])
def test_post_measurements(api, helper):
    with open(os.path.join(DATA_DIR, CCE_DATA_FILE)) as json_file:
        cce_data = json.load(json_file)

    response = api.cce.post_measurements(DATA_STORE["cce_record_id"], cce_data)
    assert "dataset--File.Generic:constant-composition-expansion" in response["ddms_urn"]
    DATA_STORE["cce_dataset_id"] = helper.get_dataset_id_from_ddms_urn(response["ddms_urn"])

    record = api.cce.get_cce_data(DATA_STORE["cce_record_id"])
    assert "DDMSDatasets" in record["data"]


@pytest.mark.smoke
def test_post_measurements_non_existent_id(api):
    with open(os.path.join(DATA_DIR, CCE_DATA_FILE)) as json_file:
        cce_data = json.load(json_file)

    timestamp = int(time.time())
    api.cce.post_measurements(
        f"{ID_TEMPLATE}autotest_{timestamp}",
        cce_data,
        allowed_codes=[status.HTTP_404_NOT_FOUND],
    )


@pytest.mark.xfail(reason="XOMROCK-746")
@pytest.mark.dependency(depends=["test_post_cce"])
def test_post_measurements_validation_failed(api):
    with open(os.path.join(DATA_DIR, "cce_wrong_ids.json")) as json_file:
        cce_data = json.load(json_file)

    error = api.cce.post_measurements(
        DATA_STORE["cce_record_id"],
        cce_data,
        allowed_codes=[status.HTTP_422_UNPROCESSABLE_ENTITY],
    )

    expected_errors = {
        "opendes:reference-data--PressureMeasurementType:WrongID",
        "opendes:work-product-component--ConstantCompositionExpansionTes:WrongID",
        "opendes:master-data--FluidSample:WrongID:",
    }

    assert error["reason"] == "Data validation failed."
    assert expected_errors == set(error["errors"]["Missing records in storage"])


@pytest.mark.smoke
@pytest.mark.dependency(depends=["test_post_measurements"])
def test_get_measurements_as_json(api):
    cce_data = api.cce.get_measurements(DATA_STORE["cce_record_id"], DATA_STORE["cce_dataset_id"])

    assert isinstance(cce_data, dict)

    assert "columns" in cce_data and cce_data["columns"]
    assert "index" in cce_data and cce_data["index"]
    assert "data" in cce_data and cce_data["data"]


# Should be after test_get_measurements_as_json, as it will overwritte with empty data and get_measurements_as_json will fail
# Alternatively, we can use different record-id for empty dataset tests
@pytest.mark.xfail(reason="XOMROCK-548")
@pytest.mark.dependency(depends=["test_get_measurements_as_json"])
def test_post_measurements_with_empty_body(api):
    error = api.cce.post_measurements(
        DATA_STORE["cce_record_id"],
        {"columns": [], "index": [], "data": []},
        allowed_codes=[status.HTTP_422_UNPROCESSABLE_ENTITY],
    )

    assert error["reason"] == "Data validation failed."
    assert error["errors"] == {
        "Mandatory parameters missing": [
            "id",
        ],
    }


@pytest.mark.smoke
@pytest.mark.dependency(depends=["test_post_cce"])
def test_delete_cce_record(api):
    # status code check is implemented on the API client layer
    api.cce.soft_delete_record(DATA_STORE["cce_record_id"], allowed_codes=[status.HTTP_204_NO_CONTENT])
    api.cce.get_cce_data(DATA_STORE["cce_record_id"], allowed_codes=[status.HTTP_404_NOT_FOUND])


@pytest.mark.smoke
def test_delete_non_existent_record(api):
    # status code check is implemented on the API client layer
    timestamp = int(time.time())
    api.cce.soft_delete_record(
        f"{ID_TEMPLATE}autotest_{timestamp}",
        allowed_codes=[status.HTTP_404_NOT_FOUND],
    )
