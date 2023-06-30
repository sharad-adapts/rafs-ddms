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
    "data_file_name, api_path, test_record_id", [
        (DataFiles.CCE, DataTypes.CCE, "ConstantCompositionExpansionTestID"),
        (DataFiles.DIF_LIB, DataTypes.DIF_LIB, "DifferentialLiberationTestID"),
        (DataFiles.CA, DataTypes.CA, "CompositionalAnalysisTestID"),
        (DataFiles.CVD, DataTypes.CVD, "ConstantVolumeDepletionTestID"),
        (DataFiles.IT, DataTypes.IT, "InterfacialTensionTestID"),
        (DataFiles.MSS, DataTypes.MSS, "MultiStageSeparatorTestID"),
        (DataFiles.MCM, DataTypes.MCM, "MultipleContactMiscibilityTestID"),
        (DataFiles.SLIM_TUBE, DataTypes.SLIM_TUBE, "SlimTubeTestID"),
        (DataFiles.STOA, DataTypes.STOA, "StockTankOilAnalysisTestID"),
        (DataFiles.ST, DataTypes.ST, "SwellingTestID"),
        (DataFiles.TT, DataTypes.TT, "TransportTestID"),
        (DataFiles.VLE, DataTypes.VLE, "VaporLiquidEquilibriumTestID"),
        (DataFiles.WA, DataTypes.WA, "WaterAnalysisTestID"),
    ],
)
@pytest.mark.smoke
def test_post_test_record(api, create_pvt, helper, tests_data, data_file_name, api_path, delete_record, test_record_id):
    test_data = tests_data(data_file_name)

    test_data["data"]["PVTReportID"] = f"{create_pvt['id']}:"

    full_record_id = [
        el for el in getattr(api, api_path).post_record([test_data])["recordIdVersions"] if
        DataTypes.PVT.upper() not in el
    ][0]
    record_id = helper.parse_full_record_id(full_record_id)["record_without_version"]

    assert full_record_id.startswith(test_data["id"])

    # check that Test has been linked to the PVT record after creation
    pvt_report = getattr(api, DataTypes.PVT).get_record(create_pvt["id"])
    assert pvt_report["data"]["PVTTests"][test_record_id][0] == f"{record_id}:"

    delete_record["record_id"].append(test_data["id"])
    delete_record["api_path"] = api_path


@pytest.mark.parametrize(
    "data_file_name, api_path, id_template", [
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
def test_update_test_record(api, helper, create_record, tests_data, data_file_name, api_path, id_template):
    record_data, created_record = create_record(api_path, data_file_name, id_template)

    test_data = copy.deepcopy(tests_data(data_file_name))
    test_data["id"] = record_data["id"]

    new_version = getattr(api, api_path).post_record([test_data])["recordIdVersions"]
    full_record_id = helper.extract_only_created_tests_ids(new_version)[0]
    version = helper.parse_full_record_id(full_record_id)["version"]
    record_versions = getattr(api, api_path).get_record_versions(record_data["id"])

    assert full_record_id.startswith(test_data["id"])
    assert record_versions["versions"][-1] == version
    assert len(record_versions["versions"]) == 2
    assert version > helper.parse_full_record_id(created_record["recordIdVersions"][0])["version"]


@pytest.mark.parametrize(
    "data_file_name, api_path", [
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
def test_post_multiple_records(api, helper, tests_data, data_file_name, api_path, delete_record):
    test_data = tests_data(data_file_name)
    request_objects = 2
    copies = helper.create_data_copies(test_data, request_objects)

    response = getattr(api, api_path).post_record(copies)

    delete_record["api_path"] = api_path

    assert response["recordCount"] == request_objects + 1  # + updated pvt record

    for record_index, created_record in enumerate(response["recordIdVersions"]):
        if DataTypes.PVT.upper() not in created_record:
            record_id_parts = created_record.split(":")
            record_id_without_version = ":".join(record_id_parts[:3])
            delete_record["record_id"].append(record_id_without_version)

            assert any(el["id"] == record_id_without_version for el in copies)


@pytest.mark.parametrize(
    "case, record_id", [
        ("Deleted", "deleted_test_for_automation"),
        ("Not_existent", "not_existent"),
    ],
)
@pytest.mark.parametrize(
    "data_file_name, api_path", [
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
def test_pvt_report_id_not_found(api, tests_data, case, record_id, data_file_name, api_path):
    test_data = tests_data(data_file_name)
    record = copy.deepcopy(test_data)
    pvt_record = f"{DataTemplates.ID_PVT}{record_id}"
    record["data"]["PVTReportID"] = pvt_record + ":"

    error = getattr(api, api_path).post_record([record], allowed_codes=[status.HTTP_422_UNPROCESSABLE_ENTITY])
    assert error["reason"] == f"Parent records ['{pvt_record}'] not found."


@pytest.mark.parametrize(
    "data_file_name, api_path", [
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
def test_pvt_report_id_is_required(api, tests_data, data_file_name, api_path):
    test_data = tests_data(data_file_name)
    record = copy.deepcopy(test_data)
    del record["data"]["PVTReportID"]

    error = getattr(api, api_path).post_record([record], allowed_codes=[status.HTTP_422_UNPROCESSABLE_ENTITY])
    assert "errors=[{'loc': ('data', 'PVTReportID'), 'msg': 'field required'" in error["reason"]


@pytest.mark.parametrize(
    "data_file_name, api_path, id_template", [
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
def test_get_test_record(api, helper, create_record, tests_data, data_file_name, api_path, id_template, delete_record):
    record_data, created_record = create_record(api_path, data_file_name, id_template)
    record = getattr(api, api_path).get_record(record_data["id"])

    full_record_id = helper.extract_only_created_tests_ids(created_record["recordIdVersions"])[0]

    assert record["id"] == record_data["id"]
    assert record["version"] == helper.parse_full_record_id(full_record_id)["version"]


@pytest.mark.parametrize(
    "data_file_name, api_path, id_template", [
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
def test_get_versions(api, helper, create_record, api_path, data_file_name, id_template):
    record_data, created_record = create_record(api_path, data_file_name, id_template)
    test_data = getattr(api, api_path).get_record_versions(record_data["id"])

    full_record_id = helper.extract_only_created_tests_ids(created_record["recordIdVersions"])[0]

    assert test_data["recordId"] == record_data["id"]
    assert test_data["versions"][-1] == helper.parse_full_record_id(full_record_id)["version"]


@pytest.mark.parametrize(
    "data_file_name, api_path, id_template", [
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
def test_get_version(api, helper, create_record, api_path, data_file_name, id_template):
    record_data, created_record = create_record(api_path, data_file_name, id_template)

    full_record_id = helper.extract_only_created_tests_ids(created_record["recordIdVersions"])[0]

    version = helper.parse_full_record_id(full_record_id)["version"]
    test_data = getattr(api, api_path).get_record_version(
        record_data["id"], version,
    )

    assert test_data["id"] == record_data["id"]
    assert test_data["version"] == version
