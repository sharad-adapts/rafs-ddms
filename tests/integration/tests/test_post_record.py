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

import pytest
from starlette import status

from tests.integration.config import (
    CONFIG,
    DataFiles,
    DataTemplates,
    DataTypes,
)


@pytest.mark.smoke
@pytest.mark.v2
def test_post_record_v2_sample_analysis(api, tests_data, delete_record):
    data_file_name = DataFiles.SAMPLE_ANALYSIS
    api_path = DataTypes.SAMPLE_ANALYSIS

    test_data = tests_data(data_file_name, "BasicRockProperties")
    full_record_id = getattr(api, api_path).post_record([test_data])["recordIdVersions"][0]

    assert full_record_id.startswith(test_data["id"])

    delete_record["record_id"].append(test_data["id"])
    delete_record["api_path"] = api_path


@pytest.mark.smoke
@pytest.mark.v2
def test_post_record_v2_masterdata_sample(api, tests_data, delete_record):
    data_file_name = DataFiles.SAMPLE
    api_path = DataTypes.MASTER_DATA

    test_data = tests_data(data_file_name)
    full_record_id = getattr(api, api_path).post_record([test_data])["recordIdVersions"][0]

    assert full_record_id.startswith(test_data["id"])

    delete_record["record_id"].append(test_data["id"])
    delete_record["api_path"] = api_path


@pytest.mark.smoke
@pytest.mark.v2
def test_post_record_v2_pvt_model(api, tests_data, delete_record):
    data_file_name = DataFiles.PVT_MODEL
    api_path = DataTypes.PVT_MODEL

    test_data = tests_data(data_file_name)
    full_record_id = getattr(api, api_path).post_record([test_data])["recordIdVersions"][0]

    assert full_record_id.startswith(test_data["id"])

    delete_record["record_id"].append(test_data["id"])
    delete_record["api_path"] = api_path


@pytest.mark.smoke
@pytest.mark.v2
def test_update_record_v2_sample_analysis(api, tests_data, helper, create_record):
    data_file_name = DataFiles.SAMPLE_ANALYSIS
    api_path = DataTypes.SAMPLE_ANALYSIS
    id_template = DataTemplates.ID_SAMPLE_ANALYSIS.format(partition=CONFIG["DATA_PARTITION"])

    record_data, created_record = create_record(api_path, data_file_name, id_template, "BasicRockProperties")

    test_data = copy.deepcopy(tests_data(data_file_name, "BasicRockProperties"))
    test_data["id"] = record_data["id"]

    full_record_id = getattr(api, api_path).post_record([test_data])["recordIdVersions"][0]
    version = helper.parse_full_record_id(full_record_id)["version"]
    record_versions = getattr(api, api_path).get_record_versions(record_data["id"])

    assert full_record_id.startswith(test_data["id"])
    assert record_versions["versions"][-1] == version
    assert len(record_versions["versions"]) == 2
    assert version > helper.parse_full_record_id(created_record["recordIdVersions"][0])["version"]


@pytest.mark.smoke
@pytest.mark.v2
def test_failed_record_creation_v2_sample_analysis(api, tests_data):
    data_file_name = DataFiles.SAMPLE_ANALYSIS
    api_path = DataTypes.SAMPLE_ANALYSIS

    test_data = tests_data(data_file_name)
    record = copy.deepcopy(test_data)
    record["id"] = 1  # invalid id
    getattr(api, api_path).post_record([record], allowed_codes=[status.HTTP_422_UNPROCESSABLE_ENTITY])


@pytest.mark.smoke
@pytest.mark.v2
def test_failed_record_creation_v2_sample_analysis(api, tests_data, helper, delete_record):
    data_file_name = DataFiles.SAMPLE_ANALYSIS
    api_path = DataTypes.SAMPLE_ANALYSIS

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


@pytest.mark.smoke
@pytest.mark.v2
def test_failed_record_creation_v2_sample_analysis(api, tests_data):
    data_file_name = DataFiles.SAMPLE_ANALYSIS
    api_path = DataTypes.SAMPLE_ANALYSIS

    test_data = tests_data(data_file_name)
    error = getattr(api, api_path).post_record(
        [test_data, test_data], allowed_codes=[status.HTTP_400_BAD_REQUEST],
    )

    assert (
        "Cannot update the same record multiple times in the same request"
        in error["message"]
    )


@pytest.mark.smoke
@pytest.mark.v2
def test_failed_record_creation_v2_sample_analysis(api, tests_data):
    data_file_name = DataFiles.SAMPLE_ANALYSIS
    api_path = DataTypes.SAMPLE_ANALYSIS

    test_data = tests_data(data_file_name)
    error = getattr(api, api_path).post_record(
        [test_data, {}], allowed_codes=[status.HTTP_422_UNPROCESSABLE_ENTITY],
    )

    assert "Unprocessable entity" in error["reason"]
