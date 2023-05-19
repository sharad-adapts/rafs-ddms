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
import json
import os
import time

import pytest
from starlette import status

from app.resources.common_headers import CONTENT_TYPE
from app.resources.mime_types import CustomMimeTypes
from tests.integration.config import (
    DATA_DIR,
    DATA_STORE,
    RCA_FILE,
    RSA_FILE,
    UPLOADED_FILES,
)

ID_RSA_TEMPLATE = "opendes:work-product-component--RockSampleAnalysis:"
ID_RCA_TEMPLATE = "opendes:dataset--File.Generic:routine-core-analysis"


@pytest.mark.smoke
@pytest.mark.dependency(name="test_post_rsa_record")
def test_post_rsa_record(api, tests_data):
    test_data = tests_data(RSA_FILE)
    full_record_id = api.rsa.post_rsa_data([test_data])["recordIdVersions"][0]

    assert full_record_id.startswith(test_data["id"])

    record_id = ":".join(full_record_id.split(":")[:3])
    version = int(":".join(full_record_id.split(":")[3:]))
    DATA_STORE["rsa_record_id"] = record_id
    DATA_STORE["rsa_version"] = version


@pytest.mark.smoke
@pytest.mark.dependency(depends=["test_post_rsa_record"])
def test_post_new_rsa_version(api, tests_data):
    test_data = tests_data(RSA_FILE)
    full_record_id = api.rsa.post_rsa_data([test_data])["recordIdVersions"][0]
    version = int(":".join(full_record_id.split(":")[3:]))

    assert full_record_id.startswith(test_data["id"])
    assert version > DATA_STORE["rsa_version"]

    # save current version as old and overwrite with a new one
    DATA_STORE["old_rsa_version"] = DATA_STORE["rsa_version"]
    DATA_STORE["rsa_version"] = version


@pytest.mark.smoke
def test_post_failed_record_creation(api, tests_data):
    test_data = tests_data(RSA_FILE)
    json_obj_copy = copy.deepcopy(test_data)
    json_obj_copy["id"] = 1  # invalid id
    api.rsa.post_rsa_data([json_obj_copy], allowed_codes=[status.HTTP_422_UNPROCESSABLE_ENTITY])


@pytest.mark.smoke
@pytest.mark.dependency(depends=["test_post_rsa_record"])
def test_post_multiple_rsa_record(api, helper, tests_data):
    test_data = tests_data(RSA_FILE)
    request_objects = 2
    copies = helper.create_data_copies(test_data, request_objects)

    response = api.rsa.post_rsa_data(copies)
    record_ids = response["recordIdVersions"]

    assert response["recordCount"] == request_objects

    for record_index, created_record in enumerate(record_ids):
        record_id_parts = created_record.split(":")
        record_id_without_version = ":".join(record_id_parts[:3])

        assert any(el["id"] == record_id_without_version for el in copies)


@pytest.mark.smoke
def test_multiple_rsa_with_same_record_id(api, tests_data):
    test_data = tests_data(RSA_FILE)
    error = api.rsa.post_rsa_data([test_data, test_data], allowed_codes=[status.HTTP_400_BAD_REQUEST])

    assert (
        "Cannot update the same record multiple times in the same request"
        in error["message"]
    )


@pytest.mark.smoke
def test_post_multiple_rsa_empty_record_body(api, tests_data):
    test_data = tests_data(RSA_FILE)
    error = api.rsa.post_rsa_data([test_data, {}], allowed_codes=[status.HTTP_422_UNPROCESSABLE_ENTITY])

    assert "Unprocessable entity" in error["reason"]


@pytest.mark.smoke
@pytest.mark.dependency(depends=["test_post_rsa_record"])
def test_get_versions(api):
    test_data = api.rsa.get_record_versions(DATA_STORE["rsa_record_id"])

    assert test_data["recordId"] == DATA_STORE["rsa_record_id"]
    assert test_data["versions"][-1] == DATA_STORE["rsa_version"]


@pytest.mark.smoke
def test_get_versions_of_non_existent_record(api):
    timestamp = int(time.time())
    non_existent_id = f"{ID_RSA_TEMPLATE}autotest_{timestamp}"
    error = api.rsa.get_record_versions(
        non_existent_id,
        allowed_codes=[status.HTTP_404_NOT_FOUND],
    )
    assert f"The record '{non_existent_id}' was not found" in error["message"]


@pytest.mark.smoke
@pytest.mark.dependency(depends=["test_post_rsa_record"])
def test_get_version(api):
    test_data = api.rsa.get_version_of_the_record(
        DATA_STORE["rsa_record_id"], DATA_STORE["rsa_version"],
    )

    assert test_data["id"] == DATA_STORE["rsa_record_id"]
    assert test_data["version"] == DATA_STORE["rsa_version"]


@pytest.mark.smoke
@pytest.mark.dependency(depends=["test_post_rsa_record"])
def test_get_non_existent_version_of_the_record(api):
    invalid_version = int(time.time())
    error = api.rsa.get_version_of_the_record(
        DATA_STORE["rsa_record_id"],
        version=int(time.time()),
        allowed_codes=[status.HTTP_404_NOT_FOUND],
    )
    assert (
        f"The version {invalid_version} can't be found for record {DATA_STORE['rsa_record_id']}"
        in error["message"]
    )


@pytest.mark.smoke
def test_get_version_of_non_existent_record(api):
    timestamp = int(time.time())
    non_existent_id = f"{ID_RSA_TEMPLATE}autotest_{timestamp}"
    error = api.rsa.get_version_of_the_record(
        non_existent_id,
        version=int(time.time()),
        allowed_codes=[status.HTTP_404_NOT_FOUND],
    )
    assert f"The record '{non_existent_id}' was not found" in error["message"]


@pytest.mark.smoke
@pytest.mark.dependency(depends=["test_post_rsa_record"])
def test_get_rsa_record(api):
    rsa_record = api.rsa.get_rsa_data(DATA_STORE["rsa_record_id"])

    assert rsa_record["id"] == DATA_STORE["rsa_record_id"]
    assert rsa_record["version"] == DATA_STORE["rsa_version"]
    assert not rsa_record["data"]["Artefacts"]


@pytest.mark.smoke
def test_get_non_existent_rsa_record(api):
    timestamp = int(time.time())
    non_existent_id = f"{ID_RSA_TEMPLATE}autotest_{timestamp}"
    error = api.rsa.get_rsa_data(non_existent_id, allowed_codes=[status.HTTP_404_NOT_FOUND])

    assert f"The record '{non_existent_id}' was not found" in error["message"]


@pytest.mark.smoke
@pytest.mark.dependency(depends=["test_post_rsa_record"])
def test_post_rca_data(api, helper):
    with open(os.path.join(DATA_DIR, RCA_FILE)) as json_file:
        rca_data = json.load(json_file)

    response = api.rsa.post_rca_data(DATA_STORE["rsa_record_id"], rca_data)
    assert "dataset--File.Generic:routine-core-analysis" in response["ddms_urn"]
    DATA_STORE["rca_dataset_id"] = helper.get_dataset_id_from_ddms_urn(response["ddms_urn"])

    record = api.rsa.get_rsa_data(DATA_STORE["rsa_record_id"])
    assert "DDMSDatasets" in record["data"]


@pytest.mark.smoke
@pytest.mark.dependency(depends=["test_post_rsa_record"])
def test_post_rca_data_as_parquet(api, helper):
    headers = {"Content-Type": "application/x-parquet"}
    with open(os.path.join(DATA_DIR, "rca.parquet"), "rb") as parquet_file:
        parquet_data = parquet_file.read()

    response = api.rsa.post_rca_data(
        DATA_STORE["rsa_record_id"], parquet_data, headers=headers,
    )
    assert "dataset--File.Generic:routine-core-analysis" in response["ddms_urn"]
    DATA_STORE["rca_dataset_id"] = helper.get_dataset_id_from_ddms_urn(response["ddms_urn"])


@pytest.mark.smoke
def test_post_rca_with_non_existent_rsa_id(api):
    with open(os.path.join(DATA_DIR, RCA_FILE)) as json_file:
        rca_data = json.load(json_file)

    timestamp = int(time.time())
    api.rsa.post_rca_data(
        f"{ID_RSA_TEMPLATE}autotest_{timestamp}",
        rca_data,
        allowed_codes=[status.HTTP_404_NOT_FOUND],
    )


@pytest.mark.xfail(reason="XOMROCK-746")
@pytest.mark.smoke
@pytest.mark.dependency(depends=["test_post_rsa_record"])
def test_post_rca_data_validation_failed(api):
    with open(os.path.join(DATA_DIR, "rca_wrong_ids.json")) as json_file:
        rca_data = json.load(json_file)

    error = api.rsa.post_rca_data(
        DATA_STORE["rsa_record_id"],
        rca_data,
        allowed_codes=[status.HTTP_422_UNPROCESSABLE_ENTITY],
    )

    expected_errors = {
        "opendes:reference-data--PermeabilityMeasurementType:WrongID2",
        "opendes:reference-data--PermeabilityMeasurementType:WrongID",
        "opendes:reference-data--UnitOfMeasure:WrongID",
        "opendes:reference-data--RockSampleType:WrongID2",
        "opendes:reference-data--RockSampleType:WrongID",
        "opendes:master-data--RockSample:WrongID",
        "opendes:master-data--Coring:WrongID2",
        "opendes:master-data--Wellbore:WrongID",
        "opendes:master-data--Coring:WrongID",
        "opendes:master-data--RockSample:WrongID2",
        "opendes:master-data--Wellbore:WrongID2",
    }

    assert error["reason"] == "Data validation failed."
    assert expected_errors == set(error["errors"]["Missing records in storage"])


@pytest.mark.xfail(reason="XOMROCK-548")
@pytest.mark.smoke
@pytest.mark.dependency(depends=["test_post_rsa_record"])
def test_post_rca_data_with_empty_body(api):
    error = api.rsa.post_rca_data(
        DATA_STORE["rsa_record_id"],
        {"columns": [], "index": [], "data": []},
        allowed_codes=[status.HTTP_422_UNPROCESSABLE_ENTITY],
    )

    assert error["reason"] == "Data validation failed."
    assert error["errors"] == {
        "Mandatory parameters missing": [
            "RockSampleID",
            "SampleNumber",
            "SampleDepth",
        ],
    }


@pytest.mark.xfail(reason="XOMROCK-548")
@pytest.mark.smoke
@pytest.mark.dependency(depends=["test_post_rsa_record"])
def test_post_rca_without_mandatory_field_parquet(api):
    headers = {"Content-Type": "application/x-parquet"}
    with open(os.path.join(DATA_DIR, "missing_attributes_rca.parquet"), "rb") as parquet_file:
        parquet_data = parquet_file.read()
        error = api.rsa.post_rca_data(
            DATA_STORE["rsa_record_id"],
            parquet_data,
            headers=headers,
            allowed_codes=[status.HTTP_422_UNPROCESSABLE_ENTITY],
        )

    assert error["reason"] == "Data validation failed."
    assert error["errors"] == {
        "Mandatory parameters missing": [
            "RockSampleID",
            "SampleNumber",
            "SampleDepth",
        ],
    }


@pytest.mark.smoke
@pytest.mark.dependency(depends=["test_post_rsa_record"])
def test_get_rca_record_as_parquet(api):
    headers = {"Content-Type": "application/x-parquet"}
    rca_data = api.rsa.get_rca_data(
        DATA_STORE["rsa_record_id"],
        DATA_STORE["rca_dataset_id"],
        headers=headers,
    )

    # parquet is a binary file
    assert isinstance(rca_data, bytes)


@pytest.mark.smoke
@pytest.mark.dependency(depends=["test_post_rsa_record"])
def test_get_rca_record_as_json(api):
    rca_data = api.rsa.get_rca_data(DATA_STORE["rsa_record_id"], DATA_STORE["rca_dataset_id"])

    assert isinstance(rca_data, dict)

    assert "columns" in rca_data and rca_data["columns"]
    assert "index" in rca_data and rca_data["index"]
    assert "data" in rca_data and rca_data["data"]


@pytest.mark.smoke
@pytest.mark.dependency(depends=["test_post_rsa_record"])
def test_get_source_zip_file(api, tests_data):
    test_data = tests_data(RSA_FILE)
    rsa_copy = copy.deepcopy(test_data)
    rsa_copy["id"] = f"{ID_RSA_TEMPLATE}FileRecord"
    rsa_copy["data"]["Datasets"] = UPLOADED_FILES

    api.rsa.post_rsa_data([rsa_copy])

    response = api.rsa.get_rca_file(rsa_copy["id"])
    assert response.headers[CONTENT_TYPE] == CustomMimeTypes.ZIP.type
    assert "attachment;filename=datasets.zip" in response.headers["Content-Disposition"]


@pytest.mark.smoke
@pytest.mark.dependency(depends=["test_post_rsa_record"])
def test_get_source_single_file(api, tests_data):
    test_data = tests_data(RSA_FILE)
    rsa_copy = copy.deepcopy(test_data)
    rsa_copy["id"] = f"{ID_RSA_TEMPLATE}FileRecord"
    rsa_copy["data"]["Datasets"] = [UPLOADED_FILES[0]]

    api.rsa.post_rsa_data([rsa_copy])

    response = api.rsa.get_rca_file(rsa_copy["id"])
    assert "application/" in response.headers["Content-Type"]
    assert "attachment;filename=" in response.headers["Content-Disposition"]


@pytest.mark.smoke
@pytest.mark.dependency(depends=["test_post_rsa_record"])
def test_get_empty_source_dataset(api):
    response = api.rsa.get_rca_file(DATA_STORE["rsa_record_id"], allowed_codes=[status.HTTP_404_NOT_FOUND])
    assert response.text == '{"message":"entity has no source data"}'


@pytest.mark.smoke
def test_get_dataset_file_wrong_record_id(api):
    timestamp = int(time.time())
    full_id = f"opendes:work-product-component--Coring:autotest_{timestamp}"
    response = api.rsa.get_rca_file(full_id, allowed_codes=[status.HTTP_422_UNPROCESSABLE_ENTITY])
    assert "RockSampleAnalysis ID is not provided in expected OSDU pattern" in response.text


def test_get_source_with_non_existent_rsa_id(api):
    timestamp = int(time.time())
    full_id = f"{ID_RSA_TEMPLATE}autotest_{timestamp}"
    error = api.rsa.get_rca_file(
        full_id,
        allowed_codes=[status.HTTP_404_NOT_FOUND],
    )

    assert f"'{full_id}' was not found" in error.text


@pytest.mark.smoke
@pytest.mark.dependency(depends=["test_post_rsa_record"])
@pytest.mark.parametrize(
    "filter_string, expected_result",
    [
        (
            "RockSampleID,eq,opendes:master-data--RockSample:1:",
            [["opendes:master-data--RockSample:1:"]],
        ),  # exact match
        (
            "CoringID,neq,opendes:master-data--Coring:1:",
            [["opendes:master-data--Coring:2:"]],
        ),  # not equal
        pytest.param(
            "SampleDepth.Value,gt,10", [[346]], marks=[
                pytest.mark.xfail(reason="Not Implemented Yet XOMROCK-563"),
            ],
        ),  # greater than
        pytest.param(
            "NetConfiningStress.Value,gte,1", [[1], [1]], marks=[
                pytest.mark.xfail(reason="Not Implemented Yet XOMROCK-563"),
            ],
        ),  # greater than or equal to
        pytest.param(
            "ConfiningStress.Value,lt,100", [[34]], marks=[
                pytest.mark.xfail(reason="Not Implemented Yet XOMROCK-563"),
            ],
        ),  # less than
        pytest.param(
            "GrainDensity.Value,lte,10", [[10], [1.3]], marks=[
                pytest.mark.xfail(reason="Not Implemented Yet XOMROCK-563"),
            ],
        ),  # less than or equal to
    ],
)
def test_rca_filters_positive(api, filter_string, expected_result):
    columns_filter = filter_string.split(",")[0]  # column name only
    response = api.rsa.get_rca_data(
        DATA_STORE["rsa_record_id"],
        DATA_STORE["rca_dataset_id"],
        columns_filter=columns_filter,
        rows_filter=filter_string,
    )

    assert response["columns"] == [columns_filter], "Wrong columns value"
    assert response["data"] == expected_result, "Wrong filtration"


@pytest.mark.xfail(reason="Not Implemented Yet XOMROCK-563")
@pytest.mark.smoke
@pytest.mark.dependency(depends=["test_post_rsa_record"])
@pytest.mark.parametrize(
    "column, operator, expected_result", [
        ("SampleDepth.Value", "avg", [[175.72]]),
        ("SampleDepth.Value", "count", [[2]]),
        ("SampleDepth.Value", "min", [[5.44]]),
        ("NetConfiningStress.Value", "min", [[1], [1]]),
        ("ConfiningStress.Value", "max", [[123.0]]),
        ("GrainDensity.Value", "sum", [[11.3]]),
    ],
)
def test_rca_aggregation_positive(api, column, operator, expected_result):
    response = api.rsa.get_rca_data(
        DATA_STORE["rsa_record_id"],
        DATA_STORE["rca_dataset_id"],
        columns_aggregation=",".join([column, operator]),
    )

    assert response["data"] == expected_result, "Wrong aggregation"


@pytest.mark.smoke
def test_get_rca_record_non_existent_rsa_id(api):
    timestamp = int(time.time())
    full_id = f"{ID_RSA_TEMPLATE}autotest_{timestamp}"
    dataset_id = f"{ID_RCA_TEMPLATE}autotest_{timestamp}"
    error = api.rsa.get_rca_data(
        full_id,
        dataset_id,
        allowed_codes=[status.HTTP_404_NOT_FOUND],
    )
    assert full_id in error["message"]


@pytest.mark.smoke
def test_get_rca_record_non_existent_rca_id(api):
    timestamp = int(time.time())
    full_id = DATA_STORE["rsa_record_id"]
    dataset_id = f"{ID_RCA_TEMPLATE}autotest_{timestamp}"
    error = api.rsa.get_rca_data(
        full_id,
        dataset_id,
        allowed_codes=[status.HTTP_404_NOT_FOUND],
    )
    assert dataset_id in error["message"]


@pytest.mark.smoke
@pytest.mark.dependency(depends=["test_post_rsa_record"])
def test_delete_rsa_record(api):
    # status code check is implemented on the API client layer
    api.rsa.soft_delete_record(DATA_STORE["rsa_record_id"], allowed_codes=[status.HTTP_204_NO_CONTENT])
    api.rsa.get_rsa_data(DATA_STORE["rsa_record_id"], allowed_codes=[status.HTTP_404_NOT_FOUND])


@pytest.mark.smoke
def test_delete_non_existent_record(api):
    # status code check is implemented on the API client layer
    timestamp = int(time.time())
    api.rsa.soft_delete_record(
        f"{ID_RSA_TEMPLATE}autotest_{timestamp}",
        allowed_codes=[status.HTTP_404_NOT_FOUND],
    )
