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
import random
import re
import time

import pytest
from starlette import status

from app.api.routes.utils.records import generate_dataset_urn
from app.resources.common_headers import CONTENT_TYPE
from app.resources.mime_types import CustomMimeTypes
from tests.integration.config import (
    ACCEPT_HEADERS,
    DATA_DIR,
    PARQUET_HEADERS,
    SCHEMA_VERSION,
    UPLOADED_FILES,
    DataFiles,
    DataTemplates,
    DataTypes,
)
from tests.integration.data.errors import MANDATORY_PARAMETERS
from tests.test_api.api_version import API_VERSION


@pytest.mark.parametrize(
    "data_file_name, api_path", [
        (DataFiles.RS, DataTypes.RS),
        (DataFiles.CORING, DataTypes.CORING),
        (DataFiles.RSA, DataTypes.RSA),
        (DataFiles.PVT, DataTypes.PVT),
    ],
)
@pytest.mark.smoke
def test_post_record(api, tests_data, data_file_name, api_path, delete_record):
    test_data = tests_data(data_file_name)
    full_record_id = getattr(api, api_path).post_record([test_data])["recordIdVersions"][0]

    assert full_record_id.startswith(test_data["id"])

    delete_record["record_id"].append(test_data["id"])
    delete_record["api_path"] = api_path


@pytest.mark.parametrize(
    "data_file_name, api_path, id_template", [
        (DataFiles.RS, DataTypes.RS, DataTemplates.ID_RS),
        (DataFiles.CORING, DataTypes.CORING, DataTemplates.ID_CORING),
        (DataFiles.RSA, DataTypes.RSA, DataTemplates.ID_RSA),
        (DataFiles.PVT, DataTypes.PVT, DataTemplates.ID_PVT),
    ],
)
@pytest.mark.smoke
def test_update_record(api, helper, create_record, tests_data, data_file_name, api_path, id_template):
    record_data, created_record = create_record(api_path, data_file_name, id_template)

    test_data = copy.deepcopy(tests_data(data_file_name))
    test_data["id"] = record_data["id"]

    full_record_id = getattr(api, api_path).post_record([test_data])["recordIdVersions"][0]
    version = helper.parse_full_record_id(full_record_id)["version"]
    record_versions = getattr(api, api_path).get_record_versions(record_data["id"])

    assert full_record_id.startswith(test_data["id"])
    assert record_versions["versions"][-1] == version
    assert len(record_versions["versions"]) == 2
    assert version > helper.parse_full_record_id(created_record["recordIdVersions"][0])["version"]


@pytest.mark.parametrize(
    "data_file_name, api_path", [
        (DataFiles.RS, DataTypes.RS),
        (DataFiles.CORING, DataTypes.CORING),
        (DataFiles.RSA, DataTypes.RSA),
        (DataFiles.PVT, DataTypes.PVT),
        (DataFiles.CCE, DataTypes.CCE),
        (DataFiles.DIF_LIB, DataTypes.DIF_LIB),
        (DataFiles.CA, DataTypes.CA),
        (DataFiles.CVD, DataTypes.CVD),
        (DataFiles.IT, DataTypes.IT),
        (DataFiles.MSS, DataTypes.MSS),
        (DataFiles.MCM, DataTypes.MCM),
        (DataFiles.SLIM_TUBE, DataTypes.SLIM_TUBE),
        (DataFiles.STOA, DataTypes.STOA),
        (DataFiles.ST, DataTypes.ST),
        (DataFiles.TT, DataTypes.TT),
        (DataFiles.VLE, DataTypes.VLE),
        (DataFiles.WA, DataTypes.WA),
    ],
)
@pytest.mark.smoke
def test_failed_record_creation(api, tests_data, data_file_name, api_path):
    test_data = tests_data(data_file_name)
    record = copy.deepcopy(test_data)
    record["id"] = 1  # invalid id
    getattr(api, api_path).post_record([record], allowed_codes=[status.HTTP_422_UNPROCESSABLE_ENTITY])


@pytest.mark.parametrize(
    "data_file_name, api_path", [
        (DataFiles.RS, DataTypes.RS),
        (DataFiles.CORING, DataTypes.CORING),
        (DataFiles.RSA, DataTypes.RSA),
        (DataFiles.PVT, DataTypes.PVT),
    ],
)
@pytest.mark.smoke
def test_post_multiple_records(api, helper, tests_data, data_file_name, api_path, delete_record):
    test_data = tests_data(data_file_name)
    request_objects = 2
    copies = helper.create_data_copies(test_data, request_objects)

    response = getattr(api, api_path).post_record(copies)

    delete_record["api_path"] = api_path

    assert response["recordCount"] == request_objects

    for record_index, created_record in enumerate(response["recordIdVersions"]):
        record_id_parts = created_record.split(":")
        record_id_without_version = ":".join(record_id_parts[:3])
        delete_record["record_id"].append(record_id_without_version)

        assert any(el["id"] == record_id_without_version for el in copies)


@pytest.mark.parametrize(
    "data_file_name, api_path", [
        (DataFiles.RS, DataTypes.RS),
        (DataFiles.CORING, DataTypes.CORING),
        (DataFiles.RSA, DataTypes.RSA),
        (DataFiles.PVT, DataTypes.PVT),
        (DataFiles.CCE, DataTypes.CCE),
        (DataFiles.DIF_LIB, DataTypes.DIF_LIB),
        (DataFiles.CA, DataTypes.CA),
        (DataFiles.CVD, DataTypes.CVD),
        (DataFiles.IT, DataTypes.IT),
        (DataFiles.MSS, DataTypes.MSS),
        (DataFiles.MCM, DataTypes.MCM),
        (DataFiles.SLIM_TUBE, DataTypes.SLIM_TUBE),
        (DataFiles.STOA, DataTypes.STOA),
        (DataFiles.ST, DataTypes.ST),
        (DataFiles.TT, DataTypes.TT),
        (DataFiles.VLE, DataTypes.VLE),
        (DataFiles.WA, DataTypes.WA),
    ],
)
@pytest.mark.smoke
def test_post_records_with_the_same_record_id(api, tests_data, data_file_name, api_path):
    test_data = tests_data(data_file_name)
    error = getattr(api, api_path).post_record(
        [test_data, test_data], allowed_codes=[status.HTTP_400_BAD_REQUEST],
    )

    assert (
        "Cannot update the same record multiple times in the same request"
        in error["message"]
    )


@pytest.mark.parametrize(
    "data_file_name, api_path", [
        (DataFiles.RS, DataTypes.RS),
        (DataFiles.CORING, DataTypes.CORING),
        (DataFiles.RSA, DataTypes.RSA),
        (DataFiles.PVT, DataTypes.PVT),
        (DataFiles.CCE, DataTypes.CCE),
        (DataFiles.DIF_LIB, DataTypes.DIF_LIB),
        (DataFiles.CA, DataTypes.CA),
        (DataFiles.CVD, DataTypes.CVD),
        (DataFiles.IT, DataTypes.IT),
        (DataFiles.MSS, DataTypes.MSS),
        (DataFiles.MCM, DataTypes.MCM),
        (DataFiles.SLIM_TUBE, DataTypes.SLIM_TUBE),
        (DataFiles.STOA, DataTypes.STOA),
        (DataFiles.ST, DataTypes.ST),
        (DataFiles.TT, DataTypes.TT),
        (DataFiles.VLE, DataTypes.VLE),
        (DataFiles.WA, DataTypes.WA),
    ],
)
@pytest.mark.smoke
def test_post_records_with_empty_record_body(api, tests_data, data_file_name, api_path):
    test_data = tests_data(data_file_name)
    error = getattr(api, api_path).post_record(
        [test_data, {}], allowed_codes=[status.HTTP_422_UNPROCESSABLE_ENTITY],
    )

    assert "Unprocessable entity" in error["reason"]


@pytest.mark.parametrize(
    "data_file_name, measurements_file, api_path, id_template, dataset_prefix", [
        (DataFiles.RSA, DataFiles.RCA, DataTypes.RSA, DataTemplates.ID_RSA, "routine-core-analysis"),
        (
            DataFiles.CCE, DataFiles.CCE_DATA, DataTypes.CCE, DataTemplates.ID_CCE,
            "constant-composition-expansion",
        ),
        (
            DataFiles.DIF_LIB, DataFiles.DIF_LIB_DATA, DataTypes.DIF_LIB, DataTemplates.ID_DIF_LIB,
            "differential-liberation",
        ),
        (DataFiles.CA, DataFiles.CA_DATA, DataTypes.CA, DataTemplates.ID_CA, "compositionalanalysis"),
        (DataFiles.CVD, DataFiles.CVD_DATA, DataTypes.CVD, DataTemplates.ID_CVD, "constantvolumedepletiontest"),
        (DataFiles.IT, DataFiles.IT_DATA, DataTypes.IT, DataTemplates.ID_IT, "interfacialtension"),
        (DataFiles.MSS, DataFiles.MSS_DATA, DataTypes.MSS, DataTemplates.ID_MSS, "multi-stage-separator"),
        (DataFiles.MCM, DataFiles.MCM_DATA, DataTypes.MCM, DataTemplates.ID_MCM, "multiple-contact-miscibility"),
        (DataFiles.SLIM_TUBE, DataFiles.SLIM_TUBE_DATA, DataTypes.SLIM_TUBE, DataTemplates.ID_SLIM_TUBE, "slimtube-test"),
        (DataFiles.STOA, DataFiles.STOA_DATA, DataTypes.STOA, DataTemplates.ID_STOA, "stoanalysis"),
        (DataFiles.ST, DataFiles.ST_DATA, DataTypes.ST, DataTemplates.ID_ST, "swelling"),
        (DataFiles.TT, DataFiles.TT_DATA, DataTypes.TT, DataTemplates.ID_TT, "transport-test"),
        (DataFiles.VLE, DataFiles.VLE_DATA, DataTypes.VLE, DataTemplates.ID_VLE, "vaporliquidequilibriumtest"),
        (DataFiles.WA, DataFiles.WA_DATA, DataTypes.WA, DataTemplates.ID_WA, "wateranalysis"),
    ],
)
def test_post_measurements(
    api, create_record, helper, tests_data, data_file_name, measurements_file, api_path,
    id_template, dataset_prefix,
):
    record_data, _ = create_record(api_path, data_file_name, id_template)
    tests_data = tests_data(measurements_file)
    test_data = copy.deepcopy(tests_data)
    if api_path != DataTypes.RSA:
        test_data["data"][0][0] = f'{record_data["id"]}:'

    response = getattr(api, api_path).post_measurements(record_data["id"], test_data)
    assert f"dataset--File.Generic:{dataset_prefix}" in response["ddms_urn"]

    record = getattr(api, api_path).get_record(record_data["id"])
    assert "DDMSDatasets" in record["data"]


@pytest.mark.parametrize(
    "data_file_name, measurements_file, api_path, id_template, dataset_prefix", [
        (
            DataFiles.RSA, DataFiles.RCA_PARQUET, DataTypes.RSA, DataTemplates.ID_RSA,
            "routine-core-analysis",
        ),
    ],
)
@pytest.mark.smoke
def test_post_measurements_as_parquet(
        api, create_record, helper, data_file_name, measurements_file, api_path,
        id_template, dataset_prefix,
):
    record_data, _ = create_record(api_path, data_file_name, id_template)

    with open(os.path.join(DATA_DIR, measurements_file), "rb") as parquet_file:
        parquet_data = parquet_file.read()

    response = getattr(api, api_path).post_measurements(
        record_data["id"], parquet_data, headers=PARQUET_HEADERS,
    )
    assert f"dataset--File.Generic:{dataset_prefix}" in response["ddms_urn"]


@pytest.mark.parametrize(
    "measurements_file, api_path, id_template", [
        (DataFiles.RCA, DataTypes.RSA, DataTemplates.ID_RSA),
        (DataFiles.CCE_DATA, DataTypes.CCE, DataTemplates.ID_CCE),
        (DataFiles.DIF_LIB_DATA, DataTypes.DIF_LIB, DataTemplates.ID_DIF_LIB),
        (DataFiles.CA, DataTypes.CA, DataTemplates.ID_CA),
        (DataFiles.CVD, DataTypes.CVD, DataTemplates.ID_CVD),
        (DataFiles.IT, DataTypes.IT, DataTemplates.ID_IT),
        (DataFiles.MSS, DataTypes.MSS, DataTemplates.ID_MSS),
        (DataFiles.MCM, DataTypes.MCM, DataTemplates.ID_MCM),
        (DataFiles.SLIM_TUBE, DataTypes.SLIM_TUBE, DataTemplates.ID_SLIM_TUBE),
        (DataFiles.STOA, DataTypes.STOA, DataTemplates.ID_STOA),
        (DataFiles.ST, DataTypes.ST, DataTemplates.ID_ST),
        (DataFiles.TT, DataTypes.TT, DataTemplates.ID_TT),
        (DataFiles.VLE, DataTypes.VLE, DataTemplates.ID_VLE),
        (DataFiles.WA, DataTypes.WA, DataTemplates.ID_WA),
    ],
)
@pytest.mark.smoke
def test_post_measurements_with_non_existent_record_id(
    api, helper, tests_data, measurements_file, api_path,
    id_template,
):
    measurements = tests_data(measurements_file)

    getattr(api, api_path).post_measurements(
        f"{id_template}{helper.generate_random_record_id()}",
        measurements,
        allowed_codes=[status.HTTP_404_NOT_FOUND],
    )


@pytest.mark.parametrize(
    "data_file_name, measurements_file, api_path, id_template", [
        (DataFiles.RSA, DataFiles.RCA_WRONG_ID, DataTypes.RSA, DataTemplates.ID_RSA),
        (DataFiles.CCE, DataFiles.CCE_WRONG_ID, DataTypes.CCE, DataTemplates.ID_CCE),
        (DataFiles.DIF_LIB, DataFiles.DIF_LIB_WRONG_ID, DataTypes.DIF_LIB, DataTemplates.ID_DIF_LIB),
        (DataFiles.CA, DataFiles.CA_WRONG_ID, DataTypes.CA, DataTemplates.ID_CA),
        (DataFiles.CVD, DataFiles.CVD_WRONG_ID, DataTypes.CVD, DataTemplates.ID_CVD),
        (DataFiles.IT, DataFiles.IT_WRONG_ID, DataTypes.IT, DataTemplates.ID_IT),
        (DataFiles.MSS, DataFiles.MSS_WRONG_ID, DataTypes.MSS, DataTemplates.ID_MSS),
        (DataFiles.MCM, DataFiles.MCM_WRONG_ID, DataTypes.MCM, DataTemplates.ID_MCM),
        (DataFiles.SLIM_TUBE, DataFiles.SLIM_TUBE_WRONG_ID, DataTypes.SLIM_TUBE, DataTemplates.ID_SLIM_TUBE),
        (DataFiles.STOA, DataFiles.STOA_WRONG_ID, DataTypes.STOA, DataTemplates.ID_STOA),
        (DataFiles.ST, DataFiles.ST_WRONG_ID, DataTypes.ST, DataTemplates.ID_ST),
        (DataFiles.TT, DataFiles.TT_WRONG_ID, DataTypes.TT, DataTemplates.ID_TT),
        (DataFiles.VLE, DataFiles.VLE_WRONG_ID, DataTypes.VLE, DataTemplates.ID_VLE),
        (DataFiles.WA, DataFiles.WA_WRONG_ID, DataTypes.WA, DataTemplates.ID_WA),
    ],
    ids=["RSA", "CCE", "DIF_LIB", "CA", "CVD", "IT", "MSS", "MCM", "SLIM_TUBE", "STOA", "ST", "TT", "VLE", "WA"],
)
@pytest.mark.smoke
def test_post_measurements_validation_failed(
        api, tests_data, create_record, data_file_name, measurements_file, api_path, id_template,
):
    record_data, _ = create_record(api_path, data_file_name, id_template)
    measurements = tests_data(measurements_file)

    error = getattr(api, api_path).post_measurements(
        record_data["id"],
        measurements,
        allowed_codes=[status.HTTP_422_UNPROCESSABLE_ENTITY],
    )
    json_string = json.dumps(measurements)
    wrong_id_count = len(re.findall(r"WrongID\d+", json_string))
    missing_records = error["errors"]["Missing records in storage"]

    assert error["reason"] == "Data validation failed."
    try:
        assert len(missing_records) == wrong_id_count
    except AssertionError:
        actual_ids = [int(item.split("WrongID")[1]) for item in missing_records]
        missing_ids = list(filter(lambda x: x not in actual_ids, range(min(actual_ids), max(actual_ids) + 1)))
        sorted_list = sorted(missing_records, key=lambda x: int(x.split("WrongID")[1]))
        ordered_list = "\n".join(sorted_list)
        raise AssertionError(
            f"The number of returned WrongIDs is {len(missing_records)} which is less than the expected {wrong_id_count}.\n"
            f"The response {api_path.upper()} is missing WrongID{missing_ids}\n\n{ordered_list}",
        )


@pytest.mark.parametrize(
    "data_file_name, api_path, id_template", [
        (DataFiles.RSA, DataTypes.RSA, DataTemplates.ID_RSA),
        (DataFiles.CCE, DataTypes.CCE, DataTemplates.ID_CCE),
        (DataFiles.DIF_LIB, DataTypes.DIF_LIB, DataTemplates.ID_DIF_LIB),
        (DataFiles.CA, DataTypes.CA, DataTemplates.ID_CA),
        (DataFiles.CVD, DataTypes.CVD, DataTemplates.ID_CVD),
        (DataFiles.IT, DataTypes.IT, DataTemplates.ID_IT),
        (DataFiles.MSS, DataTypes.MSS, DataTemplates.ID_MSS),
        (DataFiles.MCM, DataTypes.MCM, DataTemplates.ID_MCM),
        (DataFiles.SLIM_TUBE, DataTypes.SLIM_TUBE, DataTemplates.ID_SLIM_TUBE),
        (DataFiles.STOA, DataTypes.STOA, DataTemplates.ID_STOA),
        (DataFiles.ST, DataTypes.ST, DataTemplates.ID_ST),
        (DataFiles.TT, DataTypes.TT, DataTemplates.ID_TT),
        (DataFiles.VLE, DataTypes.VLE, DataTemplates.ID_VLE),
        (DataFiles.WA, DataTypes.WA, DataTemplates.ID_WA),
    ],
    ids=["RSA", "CCE", "DIF_LIB", "CA", "CVD", "IT", "MSS", "MCM", "SLIM_TUBE", "STOA", "ST", "TT", "VLE", "WA"],
)
@pytest.mark.smoke
def test_post_measurements_with_empty_body(
        api, create_record, data_file_name, api_path, id_template,
):
    record_data, _ = create_record(api_path, data_file_name, id_template)

    getattr(api, api_path).post_measurements(
        record_data["id"],
        {},
        allowed_codes=[status.HTTP_400_BAD_REQUEST],
    )


@pytest.mark.parametrize(
    "measurements_file, api_path, id_template", [
        (DataFiles.RCA, DataTypes.RSA, DataTemplates.ID_RSA),
        (DataFiles.CCE_DATA, DataTypes.CCE, DataTemplates.ID_CCE),
        (DataFiles.DIF_LIB_DATA, DataTypes.DIF_LIB, DataTemplates.ID_DIF_LIB),
        (DataFiles.CA_DATA, DataTypes.CA, DataTemplates.ID_CA),
        (DataFiles.CVD_DATA, DataTypes.CVD, DataTemplates.ID_CVD),
        (DataFiles.IT_DATA, DataTypes.IT, DataTemplates.ID_IT),
        (DataFiles.MSS_DATA, DataTypes.MSS, DataTemplates.ID_MSS),
        (DataFiles.MCM_DATA, DataTypes.MCM, DataTemplates.ID_MCM),
        (DataFiles.SLIM_TUBE_DATA, DataTypes.SLIM_TUBE, DataTemplates.ID_SLIM_TUBE),
        (DataFiles.STOA_DATA, DataTypes.STOA, DataTemplates.ID_STOA),
        (DataFiles.ST_DATA, DataTypes.ST, DataTemplates.ID_ST),
        (DataFiles.TT_DATA, DataTypes.TT, DataTemplates.ID_TT),
        (DataFiles.VLE_DATA, DataTypes.VLE, DataTemplates.ID_VLE),
        (DataFiles.WA_DATA, DataTypes.WA, DataTemplates.ID_WA),
    ],
    ids=["RSA", "CCE", "DIF_LIB", "CA", "CVD", "IT", "MSS", "MCM", "SLIM_TUBE", "STOA", "ST", "TT", "VLE", "WA"],
)
@pytest.mark.smoke
def test_post_measurements_with_empty_dataset_version(
        api, helper, measurements_file, api_path, id_template,
):
    error = getattr(api, api_path).post_measurements(
        f"{id_template}{helper.generate_random_record_id()}",
        measurements_file,
        schema_version_header=None,
        allowed_codes=[status.HTTP_400_BAD_REQUEST],
    )

    assert "No schema version specified or invalid schema format. " \
           "Check if the schema version is specified in the 'Accept' header. " \
           f"Example: --header 'Accept: */*;version={SCHEMA_VERSION}" in error["reason"]


@pytest.mark.parametrize(
    "measurements_file, api_path, id_template", [
        (DataFiles.RCA, DataTypes.RSA, DataTemplates.ID_RSA),
        (DataFiles.CCE_DATA, DataTypes.CCE, DataTemplates.ID_CCE),
        (DataFiles.DIF_LIB_DATA, DataTypes.DIF_LIB, DataTemplates.ID_DIF_LIB),
        (DataFiles.CA_DATA, DataTypes.CA, DataTemplates.ID_CA),
        (DataFiles.CVD_DATA, DataTypes.CVD, DataTemplates.ID_CVD),
        (DataFiles.IT_DATA, DataTypes.IT, DataTemplates.ID_IT),
        (DataFiles.MSS_DATA, DataTypes.MSS, DataTemplates.ID_MSS),
        (DataFiles.MCM_DATA, DataTypes.MCM, DataTemplates.ID_MCM),
        (DataFiles.SLIM_TUBE_DATA, DataTypes.SLIM_TUBE, DataTemplates.ID_SLIM_TUBE),
        (DataFiles.STOA_DATA, DataTypes.STOA, DataTemplates.ID_STOA),
        (DataFiles.ST_DATA, DataTypes.ST, DataTemplates.ID_ST),
        (DataFiles.TT_DATA, DataTypes.TT, DataTemplates.ID_TT),
        (DataFiles.VLE_DATA, DataTypes.VLE, DataTemplates.ID_VLE),
        (DataFiles.WA_DATA, DataTypes.WA, DataTemplates.ID_WA),
    ],
    ids=["RSA", "CCE", "DIF_LIB", "CA", "CVD", "IT", "MSS", "MCM", "SLIM_TUBE", "STOA", "ST", "TT", "VLE", "WA"],
)
@pytest.mark.smoke
def test_post_measurements_with_wrong_dataset_version(
        api, helper, measurements_file, api_path, id_template,
):
    version = random.choice(["0.0.0", "1.11.0", "11.111.000.", "100000000.1000000.100000000"])
    error = getattr(api, api_path).post_measurements(
        f"{id_template}{helper.generate_random_record_id()}",
        measurements_file,
        schema_version_header=ACCEPT_HEADERS.format(version=version),
        allowed_codes=[status.HTTP_400_BAD_REQUEST],
    )

    assert "There is no model for given version. " \
           f"Schema version {version.rstrip('.')} is not one of proper versions: {{'{SCHEMA_VERSION}'}}" in error[
               "reason"
           ]


@pytest.mark.xfail(reason="XOMROCK-548")
@pytest.mark.parametrize(
    "data_file_name, api_path, id_template, expected_error", [
        (DataFiles.RSA, DataTypes.RSA, DataTemplates.ID_RSA, MANDATORY_PARAMETERS),
        (DataFiles.CCE, DataTypes.CCE, DataTemplates.ID_CCE, ["id"]),
        (DataFiles.DIF_LIB, DataTypes.DIF_LIB, DataTemplates.ID_DIF_LIB, ["id"]),
        (DataFiles.CA, DataTypes.CA, DataTemplates.ID_CA, ["id"]),
        (DataFiles.CVD, DataTypes.CVD, DataTemplates.ID_CVD, ["id"]),
        (DataFiles.IT, DataTypes.IT, DataTemplates.ID_IT, ["id"]),
        (DataFiles.MSS, DataTypes.MSS, DataTemplates.ID_MSS, ["id"]),
        (DataFiles.MCM, DataTypes.MCM, DataTemplates.ID_MCM, ["id"]),
        (DataFiles.SLIM_TUBE, DataTypes.SLIM_TUBE, DataTemplates.ID_SLIM_TUBE, ["id"]),
        (DataFiles.STOA, DataTypes.STOA, DataTemplates.ID_STOA, ["id"]),
        (DataFiles.ST, DataTypes.ST, DataTemplates.ID_ST, ["id"]),
        (DataFiles.TT, DataTypes.TT, DataTemplates.ID_TT, ["id"]),
        (DataFiles.VLE, DataTypes.VLE, DataTemplates.ID_VLE, ["id"]),
        (DataFiles.WA, DataTypes.WA, DataTemplates.ID_WA, ["id"]),
    ],
)
@pytest.mark.smoke
def test_post_measurements_with_empty_data(api, create_record, data_file_name, api_path, id_template, expected_error):
    record_data, created_record = create_record(api_path, data_file_name, id_template)

    error = getattr(api, api_path).post_measurements(
        record_data["id"],
        {"columns": [], "index": [], "data": []},
        allowed_codes=[status.HTTP_422_UNPROCESSABLE_ENTITY],
    )

    assert error["reason"] == "Data validation failed."
    assert error["errors"] == {
        "Mandatory parameters missing": expected_error,
    }


@pytest.mark.xfail(reason="XOMROCK-548")
@pytest.mark.parametrize(
    "data_file_name, measurements_file, api_path, id_template, expected_error", [
        (
            DataFiles.RSA, DataFiles.RCA_MANDATORY_ATTRIBUTES_PARQUET, DataTypes.RSA, DataTemplates.ID_RSA,
            MANDATORY_PARAMETERS,
        ),
    ],
)
@pytest.mark.smoke
def test_post_measurements_without_mandatory_field_parquet(
        api, create_record, data_file_name, measurements_file,
        api_path, id_template, expected_error,
):
    record_data, created_record = create_record(api_path, data_file_name, id_template)

    with open(os.path.join(DATA_DIR, measurements_file), "rb") as parquet_file:
        parquet_data = parquet_file.read()
        error = getattr(api, api_path).post_measurements(
            record_data["id"],
            parquet_data,
            headers=PARQUET_HEADERS,
            allowed_codes=[status.HTTP_422_UNPROCESSABLE_ENTITY],
        )

    assert error["reason"] == "Data validation failed."
    assert error["errors"] == {
        "Mandatory parameters missing": expected_error,
    }


@pytest.mark.parametrize(
    "data_file_name, measurements_file, api_path, id_template", [
        (DataFiles.RSA, DataFiles.RCA, DataTypes.RSA, DataTemplates.ID_RSA),
    ],
)
@pytest.mark.smoke
def test_get_measurements_as_parquet(
    api, helper, tests_data, create_record, data_file_name, measurements_file,
    api_path, id_template,
):
    record_data, created_record = create_record(api_path, data_file_name, id_template)

    full_dataset_id = getattr(api, api_path).post_measurements(record_data["id"], tests_data(measurements_file))[
        "ddms_urn"
    ]
    dataset_id = helper.get_dataset_id_from_ddms_urn(full_dataset_id)

    measurements = getattr(api, api_path).get_measurements(
        record_data["id"],
        dataset_id,
        headers=PARQUET_HEADERS,
    )

    # parquet is a binary file
    assert isinstance(measurements, bytes)


@pytest.mark.parametrize(
    "data_file_name, measurements_file, api_path, id_template", [
        (DataFiles.RSA, DataFiles.RCA, DataTypes.RSA, DataTemplates.ID_RSA),
        (DataFiles.CCE, DataFiles.CCE_DATA, DataTypes.CCE, DataTemplates.ID_CCE),
        (DataFiles.DIF_LIB, DataFiles.DIF_LIB_DATA, DataTypes.DIF_LIB, DataTemplates.ID_DIF_LIB),
        (DataFiles.CA, DataFiles.CA_DATA, DataTypes.CA, DataTemplates.ID_CA),
        (DataFiles.CVD, DataFiles.CVD_DATA, DataTypes.CVD, DataTemplates.ID_CVD),
        (DataFiles.IT, DataFiles.IT_DATA, DataTypes.IT, DataTemplates.ID_IT),
        (DataFiles.MSS, DataFiles.MSS_DATA, DataTypes.MSS, DataTemplates.ID_MSS),
        (DataFiles.MCM, DataFiles.MCM_DATA, DataTypes.MCM, DataTemplates.ID_MCM),
        (DataFiles.SLIM_TUBE, DataFiles.SLIM_TUBE_DATA, DataTypes.SLIM_TUBE, DataTemplates.ID_SLIM_TUBE),
        (DataFiles.STOA, DataFiles.STOA_DATA, DataTypes.STOA, DataTemplates.ID_STOA),
        (DataFiles.ST, DataFiles.ST_DATA, DataTypes.ST, DataTemplates.ID_ST),
        (DataFiles.TT, DataFiles.TT_DATA, DataTypes.TT, DataTemplates.ID_TT),
        (DataFiles.VLE, DataFiles.VLE_DATA, DataTypes.VLE, DataTemplates.ID_VLE),
        (DataFiles.WA, DataFiles.WA_DATA, DataTypes.WA, DataTemplates.ID_WA),
    ],
)
@pytest.mark.smoke
def test_get_measurements_as_json(
    api, helper, tests_data, create_record, data_file_name, measurements_file, api_path,
    id_template,
):
    record_data, created_record = create_record(api_path, data_file_name, id_template)

    tests_data = tests_data(measurements_file)
    test_data = copy.deepcopy(tests_data)
    if api_path != DataTypes.RSA:
        test_data["data"][0][0] = f'{record_data["id"]}:'

    full_dataset_id = getattr(api, api_path).post_measurements(record_data["id"], test_data)[
        "ddms_urn"
    ]
    dataset_id = helper.get_dataset_id_from_ddms_urn(full_dataset_id)

    measurements = getattr(api, api_path).get_measurements(record_data["id"], dataset_id)

    assert isinstance(measurements, dict)

    assert "columns" in measurements and measurements["columns"]
    assert "index" in measurements and measurements["index"]
    assert "data" in measurements and measurements["data"]


@pytest.mark.parametrize(
    "api_path, id_template, dataset_prefix", [
        (DataTypes.RSA, DataTemplates.ID_RSA, "routine-core-analysis"),
        (DataTypes.CCE, DataTemplates.ID_CCE, "constant-composition-expansion"),
        (DataTypes.DIF_LIB, DataTemplates.ID_DIF_LIB, "differential-liberation"),
        (DataTypes.CA, DataTemplates.ID_CA, "compositionalanalysis"),
        (DataTypes.CVD, DataTemplates.ID_CVD, "constantvolumedepletiontest"),
        (DataTypes.IT, DataTemplates.ID_IT, "interfacialtension"),
        (DataTypes.MSS, DataTemplates.ID_MSS, "multi-stage-separator"),
        (DataTypes.MCM, DataTemplates.ID_MCM, "multiple-contact-miscibility"),
        (DataTypes.SLIM_TUBE, DataTemplates.ID_SLIM_TUBE, "slimtube-test"),
        (DataTypes.STOA, DataTemplates.ID_STOA, "stoanalysis"),
        (DataTypes.ST, DataTemplates.ID_ST, "swelling"),
        (DataTypes.TT, DataTemplates.ID_TT, "transport-test"),
        (DataTypes.VLE, DataTemplates.ID_VLE, "vaporliquidequilibriumtest"),
        (DataTypes.WA, DataTemplates.ID_WA, "wateranalysis"),
    ],
    ids=["RSA", "CCE", "DIF_LIB", "CA", "CVD", "IT", "MSS", "MCM", "SLIM_TUBE", "STOA", "ST", "TT", "VLE", "WA"],
)
@pytest.mark.smoke
def test_get_measurements_with_empty_dataset_version(
        api, helper, dataset_prefix, api_path, id_template,
):
    dataset_id = f"{DataTemplates.ID_DATASET}{dataset_prefix}{helper.generate_random_record_id()}"
    error = getattr(api, api_path).get_measurements(
        f"{id_template}{helper.generate_random_record_id()}",
        dataset_id,
        schema_version_header=None,
        allowed_codes=[status.HTTP_400_BAD_REQUEST],
    )

    assert "No schema version specified or invalid schema format. " \
           "Check if the schema version is specified in the 'Accept' header. " \
           f"Example: --header 'Accept: */*;version={SCHEMA_VERSION}" in error["reason"]


@pytest.mark.parametrize(
    "api_path, id_template, dataset_prefix", [
        (DataTypes.RSA, DataTemplates.ID_RSA, "routine-core-analysis"),
        (DataTypes.CCE, DataTemplates.ID_CCE, "constant-composition-expansion"),
        (DataTypes.DIF_LIB, DataTemplates.ID_DIF_LIB, "differential-liberation"),
        (DataTypes.CA, DataTemplates.ID_CA, "compositionalanalysis"),
        (DataTypes.CVD, DataTemplates.ID_CVD, "constantvolumedepletiontest"),
        (DataTypes.IT, DataTemplates.ID_IT, "interfacialtension"),
        (DataTypes.MSS, DataTemplates.ID_MSS, "multi-stage-separator"),
        (DataTypes.MCM, DataTemplates.ID_MCM, "multiple-contact-miscibility"),
        (DataTypes.SLIM_TUBE, DataTemplates.ID_SLIM_TUBE, "slimtube-test"),
        (DataTypes.STOA, DataTemplates.ID_STOA, "stoanalysis"),
        (DataTypes.ST, DataTemplates.ID_ST, "swelling"),
        (DataTypes.TT, DataTemplates.ID_TT, "transport-test"),
        (DataTypes.VLE, DataTemplates.ID_VLE, "vaporliquidequilibriumtest"),
        (DataTypes.WA, DataTemplates.ID_WA, "wateranalysis"),
    ],
    ids=["RSA", "CCE", "DIF_LIB", "CA", "CVD", "IT", "MSS", "MCM", "SLIM_TUBE", "STOA", "ST", "TT", "VLE", "WA"],
)
@pytest.mark.smoke
def test_get_measurements_with_wrong_dataset_version(
        api, helper, dataset_prefix, api_path, id_template,
):
    version = random.choice(["0.0.0", "1.11.0", "11.111.000.", "100000000.1000000.100000000"])
    dataset_id = f"{DataTemplates.ID_DATASET}{dataset_prefix}{helper.generate_random_record_id()}"
    error = getattr(api, api_path).get_measurements(
        f"{id_template}{helper.generate_random_record_id()}",
        dataset_id,
        schema_version_header=ACCEPT_HEADERS.format(version=version),
        allowed_codes=[status.HTTP_400_BAD_REQUEST],
    )

    assert "There is no model for given version. " \
           f"Schema version {version.rstrip('.')} is not one of proper versions: {{'{SCHEMA_VERSION}'}}" in error[
               "reason"
           ]


@pytest.mark.parametrize(
    "data_file_name, api_path, id_template, dataset_prefix", [
        (DataFiles.RSA, DataTypes.RSA, DataTemplates.ID_RSA, "routine-core-analysis"),
        (DataFiles.CCE, DataTypes.CCE, DataTemplates.ID_CCE, "constant-composition-expansion"),
        (DataFiles.DIF_LIB, DataTypes.DIF_LIB, DataTemplates.ID_DIF_LIB, "differential-liberation"),
        (DataFiles.CA, DataTypes.CA, DataTemplates.ID_CA, "compositionalanalysis"),
        (DataFiles.CVD, DataTypes.CVD, DataTemplates.ID_CVD, "constantvolumedepletiontest"),
        (DataFiles.IT, DataTypes.IT, DataTemplates.ID_IT, "interfacialtension"),
        (DataFiles.MSS, DataTypes.MSS, DataTemplates.ID_MSS, "multi-stage-separator"),
        (DataFiles.MCM, DataTypes.MCM, DataTemplates.ID_MCM, "multiple-contact-miscibility"),
        (DataFiles.SLIM_TUBE, DataTypes.SLIM_TUBE, DataTemplates.ID_SLIM_TUBE, "slimtube-test"),
        (DataFiles.STOA, DataTypes.STOA, DataTemplates.ID_STOA, "stoanalysis"),
        (DataFiles.ST, DataTypes.ST, DataTemplates.ID_ST, "swelling"),
        (DataFiles.TT, DataTypes.TT, DataTemplates.ID_TT, "transport-test"),
        (DataFiles.VLE, DataTypes.VLE, DataTemplates.ID_VLE, "vaporliquidequilibriumtest"),
        (DataFiles.WA, DataTypes.WA, DataTemplates.ID_WA, "wateranalysis"),
    ],
    ids=["RSA", "CCE", "DIF_LIB", "CA", "CVD", "IT", "MSS", "MCM", "SLIM_TUBE", "STOA", "ST", "TT", "VLE", "WA"],
)
@pytest.mark.smoke
def test_get_measurements_invalid_dataset_version(
        api, helper, tests_data, data_file_name, api_path, id_template, dataset_prefix, delete_record,
):
    tests_data = tests_data(data_file_name)
    test_data = copy.deepcopy(tests_data)
    dataset_id = f"{DataTemplates.ID_DATASET}{dataset_prefix}{helper.generate_random_record_id()}"
    version = "1.7.0"

    ddms_urn = generate_dataset_urn(
        ddms_id="rafs",
        api_version=API_VERSION,
        entity_type=f"{dataset_prefix.replace('-', '')}data",
        wpc_id=test_data["id"],
        dataset_id=dataset_id,
        content_schema_version=version,
    )
    test_data["data"]["DDMSDatasets"] = test_data.get("DDMSDatasets", [ddms_urn])

    getattr(api, api_path).post_record([test_data])

    delete_record["record_id"].append(test_data["id"])
    delete_record["api_path"] = api_path

    error = getattr(api, api_path).get_measurements(
        test_data["id"],
        dataset_id,
        schema_version_header=ACCEPT_HEADERS.format(version=SCHEMA_VERSION),
        allowed_codes=[status.HTTP_400_BAD_REQUEST],
    )

    assert "Invalid schema version has been provided. " \
           f"Schema version {SCHEMA_VERSION} is not one of proper versions: {{'{version}'}}" == error["reason"]


@pytest.mark.parametrize(
    "api_path, id_template, dataset_prefix", [
        (DataTypes.RSA, DataTemplates.ID_RSA, "routine-core-analysis"),
    ],
)
@pytest.mark.smoke
def test_get_measurements_non_existent_record_id(api, helper, api_path, id_template, dataset_prefix):
    full_id = f"{id_template}{helper.generate_random_record_id()}"
    dataset_id = f"{DataTemplates.ID_DATASET}{dataset_prefix}{helper.generate_random_record_id()}"
    error = getattr(api, api_path).get_measurements(
        full_id,
        dataset_id,
        allowed_codes=[status.HTTP_404_NOT_FOUND],
    )
    assert full_id in error["message"]


@pytest.mark.parametrize(
    "data_file_name, api_path, id_template, dataset_prefix", [
        (DataFiles.RSA, DataTypes.RSA, DataTemplates.ID_RSA, "routine-core-analysis"),
    ],
)
@pytest.mark.smoke
def test_get_measurements_non_existent_dataset_id(
    api, helper, create_record, data_file_name, api_path, id_template,
    dataset_prefix,
):
    record_data, created_record = create_record(api_path, data_file_name, id_template)

    dataset_id = f"{DataTemplates.ID_DATASET}{dataset_prefix}{helper.generate_random_record_id()}"
    error = getattr(api, api_path).get_measurements(
        record_data["id"],
        dataset_id,
        allowed_codes=[status.HTTP_404_NOT_FOUND],
    )
    assert dataset_id in error["message"]


@pytest.mark.parametrize(
    "data_file_name, api_path, id_template", [
        (DataFiles.RS, DataTypes.RS, DataTemplates.ID_RS),
        (DataFiles.CORING, DataTypes.CORING, DataTemplates.ID_CORING),
        (DataFiles.RSA, DataTypes.RSA, DataTemplates.ID_RSA),
        (DataFiles.PVT, DataTypes.PVT, DataTemplates.ID_PVT),
    ],
)
@pytest.mark.smoke
def test_get_record(api, helper, create_record, api_path, data_file_name, id_template):
    record_data, created_record = create_record(api_path, data_file_name, id_template)
    record = getattr(api, api_path).get_record(record_data["id"])

    assert record["id"] == record_data["id"]
    assert record["version"] == helper.parse_full_record_id(created_record["recordIdVersions"][0])["version"]


@pytest.mark.parametrize(
    "api_path, id_template", [
        (DataTypes.RS, DataTemplates.ID_RS),
        (DataTypes.CORING, DataTemplates.ID_CORING),
        (DataTypes.RSA, DataTemplates.ID_RSA),
        (DataTypes.PVT, DataTemplates.ID_PVT),
        (DataTypes.CCE, DataTemplates.ID_CCE),
        (DataTypes.DIF_LIB, DataTemplates.ID_DIF_LIB),
        (DataTypes.CA, DataTemplates.ID_CA),
        (DataTypes.CVD, DataTemplates.ID_CVD),
        (DataTypes.IT, DataTemplates.ID_IT),
        (DataTypes.MSS, DataTemplates.ID_MSS),
        (DataTypes.MCM, DataTemplates.ID_MCM),
        (DataTypes.SLIM_TUBE, DataTemplates.ID_SLIM_TUBE),
        (DataTypes.STOA, DataTemplates.ID_STOA),
        (DataTypes.ST, DataTemplates.ID_ST),
        (DataTypes.TT, DataTemplates.ID_TT),
        (DataTypes.VLE, DataTemplates.ID_VLE),
        (DataTypes.WA, DataTemplates.ID_WA),
    ],
)
@pytest.mark.smoke
def test_get_non_existent_record(api, helper, api_path, id_template):
    non_existent_id = f"{id_template}{helper.generate_random_record_id()}"
    error = getattr(api, api_path).get_record(non_existent_id, allowed_codes=[status.HTTP_404_NOT_FOUND])

    assert f"The record '{non_existent_id}' was not found" in error["message"]


@pytest.mark.parametrize(
    "data_file_name, api_path, id_template", [
        (DataFiles.RSA, DataTypes.RSA, DataTemplates.ID_RSA),
        (DataFiles.PVT, DataTypes.PVT, DataTemplates.ID_PVT),
    ],
)
@pytest.mark.smoke
def test_get_source_zip_file(api, create_record, data_file_name, api_path, id_template):
    record_data, _ = create_record(api_path, data_file_name, id_template, UPLOADED_FILES)

    response = getattr(api, api_path).get_file(record_data["id"])
    assert response.headers[CONTENT_TYPE] == CustomMimeTypes.ZIP.type
    assert "attachment;filename=datasets.zip" in response.headers["Content-Disposition"]


@pytest.mark.parametrize(
    "data_file_name, api_path, id_template", [
        (DataFiles.RSA, DataTypes.RSA, DataTemplates.ID_RSA),
        (DataFiles.PVT, DataTypes.PVT, DataTemplates.ID_PVT),
    ],
)
@pytest.mark.smoke
def test_get_source_single_file(api, create_record, data_file_name, api_path, id_template):
    record_data, _ = create_record(api_path, data_file_name, id_template, [UPLOADED_FILES[0]])

    response = getattr(api, api_path).get_file(record_data["id"])
    assert "application/" in response.headers["Content-Type"]
    assert "attachment;filename=" in response.headers["Content-Disposition"]


@pytest.mark.parametrize(
    "data_file_name, api_path, id_template", [
        (DataFiles.RSA, DataTypes.RSA, DataTemplates.ID_RSA),
        (DataFiles.PVT, DataTypes.PVT, DataTemplates.ID_PVT),
    ],
)
@pytest.mark.smoke
def test_get_source_file_not_uploaded(api, create_record, data_file_name, api_path, id_template):
    record_data, _ = create_record(
        api_path, data_file_name, id_template,
        ["opendes:dataset--File.Generic:not_uploaded:"],
    )

    response = getattr(api, api_path).get_file(record_data["id"], allowed_codes=[status.HTTP_404_NOT_FOUND])
    assert "The record 'opendes:dataset--File.Generic:not_uploaded' was not found" in response.text


@pytest.mark.parametrize(
    "data_file_name, api_path, id_template", [
        (DataFiles.RSA, DataTypes.RSA, DataTemplates.ID_RSA),
        (DataFiles.PVT, DataTypes.PVT, DataTemplates.ID_PVT),
    ],
)
@pytest.mark.smoke
def test_get_empty_source_dataset(api, create_record, api_path, data_file_name, id_template):
    record_data, _ = create_record(api_path, data_file_name, id_template)
    response = getattr(api, api_path).get_file(record_data["id"], allowed_codes=[status.HTTP_404_NOT_FOUND])
    assert response.text == '{"message":"entity has no source data"}'


@pytest.mark.parametrize(
    "api_path, data_type", [
        (DataTypes.RSA, "RockSampleAnalysis"),
        (DataTypes.PVT, "PVT"),
    ],
)
@pytest.mark.smoke
def test_get_dataset_file_wrong_record_id(api, helper, api_path, data_type):
    full_id = f"{DataTemplates.ID_CORING}{helper.generate_random_record_id()}"
    response = getattr(api, api_path).get_file(full_id, allowed_codes=[status.HTTP_422_UNPROCESSABLE_ENTITY])
    assert f"{data_type} ID is not provided in expected OSDU pattern" in response.text


@pytest.mark.parametrize(
    "api_path, id_template", [
        (DataTypes.RSA, DataTemplates.ID_RSA),
        (DataTypes.PVT, DataTemplates.ID_PVT),
    ],
)
def test_get_source_with_non_existent_id(api, helper, api_path, id_template):
    full_id = f"{id_template}{helper.generate_random_record_id()}"
    error = getattr(api, api_path).get_file(
        full_id,
        allowed_codes=[status.HTTP_404_NOT_FOUND],
    )

    assert f"'{full_id}' was not found" in error.text


@pytest.mark.parametrize(
    "data_file_name, api_path, id_template", [
        (DataFiles.RS, DataTypes.RS, DataTemplates.ID_RS),
        (DataFiles.CORING, DataTypes.CORING, DataTemplates.ID_CORING),
        (DataFiles.RSA, DataTypes.RSA, DataTemplates.ID_RSA),
        (DataFiles.PVT, DataTypes.PVT, DataTemplates.ID_PVT),
    ],
)
@pytest.mark.smoke
def test_get_versions(api, helper, create_record, api_path, data_file_name, id_template):
    record_data, created_record = create_record(api_path, data_file_name, id_template)
    test_data = getattr(api, api_path).get_record_versions(record_data["id"])

    assert test_data["recordId"] == record_data["id"]
    assert test_data["versions"][-1] == helper.parse_full_record_id(created_record["recordIdVersions"][0])["version"]


@pytest.mark.parametrize(
    "api_path, id_template", [
        (DataTypes.RS, DataTemplates.ID_RS),
        (DataTypes.CORING, DataTemplates.ID_CORING),
        (DataTypes.RSA, DataTemplates.ID_RSA),
        (DataTypes.PVT, DataTemplates.ID_PVT),
        (DataTypes.CCE, DataTemplates.ID_CCE),
        (DataTypes.DIF_LIB, DataTemplates.ID_DIF_LIB),
        (DataTypes.CA, DataTemplates.ID_CA),
        (DataTypes.CVD, DataTemplates.ID_CVD),
        (DataTypes.IT, DataTemplates.ID_IT),
        (DataTypes.MSS, DataTemplates.ID_MSS),
        (DataTypes.MCM, DataTemplates.ID_MCM),
        (DataTypes.SLIM_TUBE, DataTemplates.ID_SLIM_TUBE),
        (DataTypes.STOA, DataTemplates.ID_STOA),
        (DataTypes.ST, DataTemplates.ID_ST),
        (DataTypes.TT, DataTemplates.ID_TT),
        (DataTypes.VLE, DataTemplates.ID_VLE),
        (DataTypes.WA, DataTemplates.ID_WA),
    ],
)
@pytest.mark.smoke
def test_get_versions_of_non_existent_record(api, helper, api_path, id_template):
    non_existent_id = f"{id_template}{helper.generate_random_record_id()}"
    error = getattr(api, api_path).get_record_versions(
        non_existent_id,
        allowed_codes=[status.HTTP_404_NOT_FOUND],
    )
    assert f"The record '{non_existent_id}' was not found" in error["message"]


@pytest.mark.parametrize(
    "data_file_name, api_path, id_template", [
        (DataFiles.RS, DataTypes.RS, DataTemplates.ID_RS),
        (DataFiles.CORING, DataTypes.CORING, DataTemplates.ID_CORING),
        (DataFiles.RSA, DataTypes.RSA, DataTemplates.ID_RSA),
        (DataFiles.PVT, DataTypes.PVT, DataTemplates.ID_PVT),
    ],
)
@pytest.mark.smoke
def test_get_version(api, helper, create_record, api_path, data_file_name, id_template):
    record_data, created_record = create_record(api_path, data_file_name, id_template)
    version = helper.parse_full_record_id(created_record["recordIdVersions"][0])["version"]
    test_data = getattr(api, api_path).get_record_version(
        record_data["id"], version,
    )

    assert test_data["id"] == record_data["id"]
    assert test_data["version"] == version


@pytest.mark.parametrize(
    "data_file_name, api_path, id_template", [
        (DataFiles.RS, DataTypes.RS, DataTemplates.ID_RS),
        (DataFiles.CORING, DataTypes.CORING, DataTemplates.ID_CORING),
        (DataFiles.RSA, DataTypes.RSA, DataTemplates.ID_RSA),
        (DataFiles.PVT, DataTypes.PVT, DataTemplates.ID_PVT),
        (DataFiles.CCE, DataTypes.CCE, DataTemplates.ID_CCE),
        (DataFiles.DIF_LIB, DataTypes.DIF_LIB, DataTemplates.ID_DIF_LIB),
        (DataFiles.CA, DataTypes.CA, DataTemplates.ID_CA),
        (DataFiles.CVD, DataTypes.CVD, DataTemplates.ID_CVD),
        (DataFiles.IT, DataTypes.IT, DataTemplates.ID_IT),
        (DataFiles.MSS, DataTypes.MSS, DataTemplates.ID_MSS),
        (DataFiles.MCM, DataTypes.MCM, DataTemplates.ID_MCM),
        (DataFiles.SLIM_TUBE, DataTypes.SLIM_TUBE, DataTemplates.ID_SLIM_TUBE),
        (DataFiles.STOA, DataTypes.STOA, DataTemplates.ID_STOA),
        (DataFiles.ST, DataTypes.ST, DataTemplates.ID_ST),
        (DataFiles.TT, DataTypes.TT, DataTemplates.ID_TT),
        (DataFiles.VLE, DataTypes.VLE, DataTemplates.ID_VLE),
        (DataFiles.WA, DataTypes.WA, DataTemplates.ID_WA),
    ],
)
@pytest.mark.smoke
def test_get_non_existent_version_of_the_record(api, create_record, api_path, data_file_name, id_template):
    record_data, _ = create_record(api_path, data_file_name, id_template)
    int(time.time())
    error = getattr(api, api_path).get_record_version(
        record_data["id"],
        version=int(time.time()),
        allowed_codes=[status.HTTP_404_NOT_FOUND],
    )
    assert f"can't be found for record {record_data['id']}" in error["message"]


@pytest.mark.parametrize(
    "api_path, id_template", [
        (DataTypes.RS, DataTemplates.ID_RS),
        (DataTypes.CORING, DataTemplates.ID_CORING),
        (DataTypes.RSA, DataTemplates.ID_RSA),
        (DataTypes.PVT, DataTemplates.ID_PVT),
        (DataTypes.CCE, DataTemplates.ID_CCE),
        (DataTypes.DIF_LIB, DataTemplates.ID_DIF_LIB),
        (DataTypes.CA, DataTemplates.ID_CA),
        (DataTypes.CVD, DataTemplates.ID_CVD),
        (DataTypes.IT, DataTemplates.ID_IT),
        (DataTypes.MSS, DataTemplates.ID_MSS),
        (DataTypes.MCM, DataTemplates.ID_MCM),
        (DataTypes.SLIM_TUBE, DataTemplates.ID_SLIM_TUBE),
        (DataTypes.STOA, DataTemplates.ID_STOA),
        (DataTypes.ST, DataTemplates.ID_ST),
        (DataTypes.TT, DataTemplates.ID_TT),
        (DataTypes.VLE, DataTemplates.ID_VLE),
        (DataTypes.WA, DataTemplates.ID_WA),
    ],
)
@pytest.mark.smoke
def test_get_version_of_non_existent_record(api, helper, api_path, id_template):
    non_existent_id = f"{id_template}{helper.generate_random_record_id()}"
    error = getattr(api, api_path).get_record_version(
        non_existent_id,
        version=int(time.time()),
        allowed_codes=[status.HTTP_404_NOT_FOUND],
    )
    assert f"The record '{non_existent_id}' was not found" in error["message"]


@pytest.mark.parametrize(
    "data_file_name, api_path, id_template", [
        (DataFiles.RS, DataTypes.RS, DataTemplates.ID_RS),
        (DataFiles.CORING, DataTypes.CORING, DataTemplates.ID_CORING),
        (DataFiles.RSA, DataTypes.RSA, DataTemplates.ID_RSA),
        (DataFiles.PVT, DataTypes.PVT, DataTemplates.ID_PVT),
        (DataFiles.CCE, DataTypes.CCE, DataTemplates.ID_CCE),
        (DataFiles.DIF_LIB, DataTypes.DIF_LIB, DataTemplates.ID_DIF_LIB),
        (DataFiles.CA, DataTypes.CA, DataTemplates.ID_CA),
        (DataFiles.CVD, DataTypes.CVD, DataTemplates.ID_CVD),
        (DataFiles.IT, DataTypes.IT, DataTemplates.ID_IT),
        (DataFiles.MSS, DataTypes.MSS, DataTemplates.ID_MSS),
        (DataFiles.MCM, DataTypes.MCM, DataTemplates.ID_MCM),
        (DataFiles.SLIM_TUBE, DataTypes.SLIM_TUBE, DataTemplates.ID_SLIM_TUBE),
        (DataFiles.STOA, DataTypes.STOA, DataTemplates.ID_STOA),
        (DataFiles.ST, DataTypes.ST, DataTemplates.ID_ST),
        (DataFiles.TT, DataTypes.TT, DataTemplates.ID_TT),
        (DataFiles.VLE, DataTypes.VLE, DataTemplates.ID_VLE),
        (DataFiles.WA, DataTypes.WA, DataTemplates.ID_WA),
    ],
)
@pytest.mark.smoke
def test_delete_record(api, create_record, api_path, data_file_name, id_template):
    record_data, _ = create_record(api_path, data_file_name, id_template, to_delete=False)
    # status code check is implemented on the API client layer
    getattr(api, api_path).soft_delete_record(record_data["id"], allowed_codes=[status.HTTP_204_NO_CONTENT])
    getattr(api, api_path).get_record(record_data["id"], allowed_codes=[status.HTTP_404_NOT_FOUND])


@pytest.mark.parametrize(
    "api_path, id_template", [
        (DataTypes.RS, DataTemplates.ID_RS),
        (DataTypes.CORING, DataTemplates.ID_CORING),
        (DataTypes.RSA, DataTemplates.ID_RSA),
        (DataTypes.PVT, DataTemplates.ID_PVT),
        (DataTypes.CCE, DataTemplates.ID_CCE),
        (DataTypes.DIF_LIB, DataTemplates.ID_DIF_LIB),
        (DataTypes.CA, DataTemplates.ID_CA),
        (DataTypes.CVD, DataTemplates.ID_CVD),
        (DataTypes.IT, DataTemplates.ID_IT),
        (DataTypes.MSS, DataTemplates.ID_MSS),
        (DataTypes.MCM, DataTemplates.ID_MCM),
        (DataTypes.SLIM_TUBE, DataTemplates.ID_SLIM_TUBE),
        (DataTypes.STOA, DataTemplates.ID_STOA),
        (DataTypes.ST, DataTemplates.ID_ST),
        (DataTypes.TT, DataTemplates.ID_TT),
        (DataTypes.VLE, DataTemplates.ID_VLE),
        (DataTypes.WA, DataTemplates.ID_WA),
    ],
)
@pytest.mark.smoke
def test_delete_non_existent_record(api, helper, api_path, id_template):
    # status code check is implemented on the API client layer
    getattr(api, api_path).soft_delete_record(
        f"{id_template}{helper.generate_random_record_id()}",
        allowed_codes=[status.HTTP_404_NOT_FOUND],
    )
