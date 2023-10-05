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

from tests.integration.config import DataFiles, DataTemplates, DataTypes


@pytest.mark.parametrize(
    "data_file_name, api_path", [
        (DataFiles.RS, DataTypes.RS),
        (DataFiles.CORING, DataTypes.CORING),
        (DataFiles.RSA, DataTypes.RSA),
        (DataFiles.PVT, DataTypes.PVT),
        (DataFiles.SAR, DataTypes.SAR),
        (DataFiles.CAP_PRESSURE, DataTypes.CAP_PRESSURE),
        (DataFiles.EXTRACTION, DataTypes.EXTRACTION),
        (DataFiles.FRACTIONATION, DataTypes.FRACTIONATION),
        (DataFiles.PHYS_CHEM, DataTypes.PHYS_CHEM),
        (DataFiles.RP, DataTypes.RP),
        (DataFiles.SAMPLE_ANALYSIS, DataTypes.SAMPLE_ANALYSIS),
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
        (DataFiles.SAR, DataTypes.SAR, DataTemplates.ID_SAR),
        (DataFiles.CAP_PRESSURE, DataTypes.CAP_PRESSURE, DataTemplates.ID_SAMPLE_ANALYSIS),
        (DataFiles.EXTRACTION, DataTypes.EXTRACTION, DataTemplates.ID_SAMPLE_ANALYSIS),
        (DataFiles.FRACTIONATION, DataTypes.FRACTIONATION, DataTemplates.ID_SAMPLE_ANALYSIS),
        (DataFiles.PHYS_CHEM, DataTypes.PHYS_CHEM, DataTemplates.ID_SAMPLE_ANALYSIS),
        (DataFiles.RP, DataTypes.RP, DataTemplates.ID_SAMPLE_ANALYSIS),
        (DataFiles.SAMPLE_ANALYSIS, DataTypes.SAMPLE_ANALYSIS, DataTemplates.ID_SAMPLE_ANALYSIS),
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
        (DataFiles.SAR, DataTypes.SAR),
        (DataFiles.EXTRACTION, DataTypes.EXTRACTION),
        (DataFiles.FRACTIONATION, DataTypes.FRACTIONATION),
        (DataFiles.PHYS_CHEM, DataTypes.PHYS_CHEM),
        (DataFiles.RP, DataTypes.RP),
        (DataFiles.SAMPLE_ANALYSIS, DataTypes.SAMPLE_ANALYSIS),
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
        (DataFiles.SAR, DataTypes.SAR),
        (DataFiles.EXTRACTION, DataTypes.EXTRACTION),
        (DataFiles.FRACTIONATION, DataTypes.FRACTIONATION),
        (DataFiles.PHYS_CHEM, DataTypes.PHYS_CHEM),
        (DataFiles.RP, DataTypes.RP),
        (DataFiles.SAMPLE_ANALYSIS, DataTypes.SAMPLE_ANALYSIS),
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
        (DataFiles.SAR, DataTypes.SAR),
        (DataFiles.EXTRACTION, DataTypes.EXTRACTION),
        (DataFiles.FRACTIONATION, DataTypes.FRACTIONATION),
        (DataFiles.PHYS_CHEM, DataTypes.PHYS_CHEM),
        (DataFiles.RP, DataTypes.RP),
        (DataFiles.SAMPLE_ANALYSIS, DataTypes.SAMPLE_ANALYSIS),
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
        (DataFiles.SAR, DataTypes.SAR),
        (DataFiles.EXTRACTION, DataTypes.EXTRACTION),
        (DataFiles.FRACTIONATION, DataTypes.FRACTIONATION),
        (DataFiles.PHYS_CHEM, DataTypes.PHYS_CHEM),
        (DataFiles.RP, DataTypes.RP),
        (DataFiles.SAMPLE_ANALYSIS, DataTypes.SAMPLE_ANALYSIS),
    ],
)
@pytest.mark.smoke
def test_post_records_with_empty_record_body(api, tests_data, data_file_name, api_path):
    test_data = tests_data(data_file_name)
    error = getattr(api, api_path).post_record(
        [test_data, {}], allowed_codes=[status.HTTP_422_UNPROCESSABLE_ENTITY],
    )

    assert "Unprocessable entity" in error["reason"]
