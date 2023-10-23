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

import pytest
from starlette import status

from tests.integration.config import (
    ACCEPT_HEADERS,
    DATA_DIR,
    PARQUET_HEADERS,
    SCHEMA_VERSION,
    DataFiles,
    DatasetPrefix,
    DataTemplates,
    DataTypes,
    SamplesAnalysisTypes,
)
from tests.integration.data.errors import RCA_MANDATORY_PARAMETERS


@pytest.mark.parametrize(
    "data_file_name, measurements_file, api_path, id_template, dataset_prefix", [
        (DataFiles.RSA, DataFiles.RCA, DataTypes.RSA, DataTemplates.ID_RSA, DatasetPrefix.RCA),
        (DataFiles.CCE, DataFiles.CCE_DATA, DataTypes.CCE, DataTemplates.ID_CCE, DatasetPrefix.CCE),
        (DataFiles.DIF_LIB, DataFiles.DIF_LIB_DATA, DataTypes.DIF_LIB, DataTemplates.ID_DIF_LIB, DatasetPrefix.DIF_LIB),
        (DataFiles.CA, DataFiles.CA_DATA, DataTypes.CA, DataTemplates.ID_CA, DatasetPrefix.CA),
        (DataFiles.CVD, DataFiles.CVD_DATA, DataTypes.CVD, DataTemplates.ID_CVD, DatasetPrefix.CVD),
        (DataFiles.IT, DataFiles.IT_DATA, DataTypes.IT, DataTemplates.ID_IT, DatasetPrefix.IT),
        (DataFiles.MSS, DataFiles.MSS_DATA, DataTypes.MSS, DataTemplates.ID_MSS, DatasetPrefix.MSS),
        (DataFiles.MCM, DataFiles.MCM_DATA, DataTypes.MCM, DataTemplates.ID_MCM, DatasetPrefix.MCM),
        (
            DataFiles.SLIM_TUBE, DataFiles.SLIM_TUBE_DATA, DataTypes.SLIM_TUBE,
            DataTemplates.ID_SLIM_TUBE, DatasetPrefix.SLIM_TUBE,
        ),
        (DataFiles.STOA, DataFiles.STOA_DATA, DataTypes.STOA, DataTemplates.ID_STOA, DatasetPrefix.STOA),
        (DataFiles.ST, DataFiles.ST_DATA, DataTypes.ST, DataTemplates.ID_ST, DatasetPrefix.ST),
        (DataFiles.TT, DataFiles.TT_DATA, DataTypes.TT, DataTemplates.ID_TT, DatasetPrefix.TT),
        (DataFiles.VLE, DataFiles.VLE_DATA, DataTypes.VLE, DataTemplates.ID_VLE, DatasetPrefix.VLE),
        (DataFiles.WA, DataFiles.WA_DATA, DataTypes.WA, DataTemplates.ID_WA, DatasetPrefix.WA),
        (
            DataFiles.CAP_PRESSURE, DataFiles.CAP_PRESSURE_DATA, DataTypes.CAP_PRESSURE,
            DataTemplates.ID_SAMPLE_ANALYSIS, DatasetPrefix.CAP_PRESSURE,
        ),
        (
            DataFiles.EXTRACTION, DataFiles.EXTRACTION_DATA, DataTypes.EXTRACTION,
            DataTemplates.ID_SAMPLE_ANALYSIS, DatasetPrefix.EXTRACTION,
        ),
        (
            DataFiles.FRACTIONATION, DataFiles.FRACTIONATION_DATA, DataTypes.FRACTIONATION,
            DataTemplates.ID_SAMPLE_ANALYSIS, DatasetPrefix.FRACTIONATION,
        ),
        (
            DataFiles.PHYS_CHEM, DataFiles.PHYS_CHEM_DATA, DataTypes.PHYS_CHEM,
            DataTemplates.ID_SAMPLE_ANALYSIS, DatasetPrefix.PHYS_CHEM,
        ),
        (DataFiles.RP, DataFiles.RP_DATA, DataTypes.RP, DataTemplates.ID_SAMPLE_ANALYSIS, DatasetPrefix.RP),
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
            DatasetPrefix.RCA,
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
    "data_file_name, measurements_file, api_path, id_template", [
        (None, DataFiles.RCA, DataTypes.RSA, DataTemplates.ID_RSA),
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
        (DataFiles.CAP_PRESSURE, DataFiles.CAP_PRESSURE_DATA, DataTypes.CAP_PRESSURE, DataTemplates.ID_SAMPLE_ANALYSIS),
        (DataFiles.EXTRACTION, DataFiles.EXTRACTION_DATA, DataTypes.EXTRACTION, DataTemplates.ID_SAMPLE_ANALYSIS),
        (DataFiles.FRACTIONATION, DataFiles.FRACTIONATION_DATA, DataTypes.FRACTIONATION, DataTemplates.ID_SAMPLE_ANALYSIS),
        (DataFiles.PHYS_CHEM, DataFiles.PHYS_CHEM_DATA, DataTypes.PHYS_CHEM, DataTemplates.ID_SAMPLE_ANALYSIS),
        (DataFiles.RP, DataFiles.RP_DATA, DataTypes.RP, DataTemplates.ID_SAMPLE_ANALYSIS),
    ],
)
@pytest.mark.smoke
def test_post_measurements_with_non_existent_record_id(
    api, helper, create_record, tests_data, data_file_name, measurements_file, api_path,
    id_template,
):
    measurements = copy.deepcopy(tests_data(measurements_file))
    if api_path != DataTypes.RSA:
        record_data, _ = create_record(api_path, data_file_name, id_template)
        measurements["data"][0][0] = f'{record_data["id"]}:'

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
        (DataFiles.CAP_PRESSURE, DataFiles.CAP_PRESSURE_WRONG_ID, DataTypes.CAP_PRESSURE, DataTemplates.ID_SAMPLE_ANALYSIS),
        (DataFiles.EXTRACTION, DataFiles.EXTRACTION_WRONG_ID, DataTypes.EXTRACTION, DataTemplates.ID_SAMPLE_ANALYSIS),
        (
            DataFiles.FRACTIONATION, DataFiles.FRACTIONATION_WRONG_ID,
            DataTypes.FRACTIONATION, DataTemplates.ID_SAMPLE_ANALYSIS,
        ),
        (DataFiles.PHYS_CHEM, DataFiles.PHYS_CHEM_WRONG_ID, DataTypes.PHYS_CHEM, DataTemplates.ID_SAMPLE_ANALYSIS),
        (DataFiles.RP, DataFiles.RP_WRONG_ID, DataTypes.RP, DataTemplates.ID_SAMPLE_ANALYSIS),
    ],
    ids=[
        "RSA", "CCE", "DIF_LIB", "CA", "CVD", "IT", "MSS", "MCM", "SLIM_TUBE", "STOA", "ST",
        "TT", "VLE", "WA", "CAP_PRESSURE", "EXTRACTION", "FRACTIONATION", "PHYS_CHEM", "RP",
    ],
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
        (DataFiles.CAP_PRESSURE, DataTypes.CAP_PRESSURE, DataTemplates.ID_SAMPLE_ANALYSIS),
        (DataFiles.EXTRACTION, DataTypes.EXTRACTION, DataTemplates.ID_SAMPLE_ANALYSIS),
        (DataFiles.FRACTIONATION, DataTypes.FRACTIONATION, DataTemplates.ID_SAMPLE_ANALYSIS),
        (DataFiles.PHYS_CHEM, DataTypes.PHYS_CHEM, DataTemplates.ID_SAMPLE_ANALYSIS),
        (DataFiles.RP, DataTypes.RP, DataTemplates.ID_SAMPLE_ANALYSIS),
    ],
    ids=[
        "RSA", "CCE", "DIF_LIB", "CA", "CVD", "IT", "MSS", "MCM", "SLIM_TUBE", "STOA", "ST",
        "TT", "VLE", "WA", "CAP_PRESSURE", "EXTRACTION", "FRACTIONATION", "PHYS_CHEM", "RP",
    ],
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
        (DataFiles.CAP_PRESSURE_DATA, DataTypes.CAP_PRESSURE, DataTemplates.ID_SAMPLE_ANALYSIS),
        (DataFiles.EXTRACTION_DATA, DataTypes.EXTRACTION, DataTemplates.ID_SAMPLE_ANALYSIS),
        (DataFiles.FRACTIONATION_DATA, DataTypes.FRACTIONATION, DataTemplates.ID_SAMPLE_ANALYSIS),
        (DataFiles.PHYS_CHEM_DATA, DataTypes.PHYS_CHEM, DataTemplates.ID_SAMPLE_ANALYSIS),
        (DataFiles.RP_DATA, DataTypes.RP, DataTemplates.ID_SAMPLE_ANALYSIS),
    ],
    ids=[
        "RSA", "CCE", "DIF_LIB", "CA", "CVD", "IT", "MSS", "MCM", "SLIM_TUBE", "STOA", "ST",
        "TT", "VLE", "WA", "CAP_PRESSURE", "EXTRACTION", "FRACTIONATION", "PHYS_CHEM", "RP",
    ],
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
        (DataFiles.CAP_PRESSURE_DATA, DataTypes.CAP_PRESSURE, DataTemplates.ID_SAMPLE_ANALYSIS),
        (DataFiles.EXTRACTION_DATA, DataTypes.EXTRACTION, DataTemplates.ID_SAMPLE_ANALYSIS),
        (DataFiles.FRACTIONATION_DATA, DataTypes.FRACTIONATION, DataTemplates.ID_SAMPLE_ANALYSIS),
        (DataFiles.PHYS_CHEM_DATA, DataTypes.PHYS_CHEM, DataTemplates.ID_SAMPLE_ANALYSIS),
        (DataFiles.RP_DATA, DataTypes.RP, DataTemplates.ID_SAMPLE_ANALYSIS),
    ],
    ids=[
        "RSA", "CCE", "DIF_LIB", "CA", "CVD", "IT", "MSS", "MCM", "SLIM_TUBE", "STOA", "ST",
        "TT", "VLE", "WA", "CAP_PRESSURE", "EXTRACTION", "FRACTIONATION", "PHYS_CHEM", "RP",
    ],
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


@pytest.mark.skip(reason="issues/66")
@pytest.mark.parametrize(
    "data_file_name, measurements_file, api_path, id_template, mandatory_fields", [
        (DataFiles.RSA, DataFiles.RCA, DataTypes.RSA, DataTemplates.ID_RSA, RCA_MANDATORY_PARAMETERS),
        (
            DataFiles.CCE, DataFiles.CCE_DATA, DataTypes.CCE,
            DataTemplates.ID_CCE, ["ConstantCompositionExpansionTestID"],
        ),
        (
            DataFiles.DIF_LIB, DataFiles.DIF_LIB_DATA, DataTypes.DIF_LIB,
            DataTemplates.ID_DIF_LIB, ["DifferentialLiberationTestID"],
        ),
        (DataFiles.CA, DataFiles.CA_DATA, DataTypes.CA, DataTemplates.ID_CA, ["CompositionalAnalysisTestID"]),
        (DataFiles.CVD, DataFiles.CVD_DATA, DataTypes.CVD, DataTemplates.ID_CVD, ["ConstantVolumeDepletionTestID"]),
        (DataFiles.IT, DataFiles.IT_DATA, DataTypes.IT, DataTemplates.ID_IT, ["InterfacialTensionTestID"]),
        (DataFiles.MSS, DataFiles.MSS_DATA, DataTypes.MSS, DataTemplates.ID_MSS, ["MultiStageSeparatorTestID"]),
        (DataFiles.MCM, DataFiles.MCM_DATA, DataTypes.MCM, DataTemplates.ID_MCM, ["MultipleContactMiscibilityTestID"]),
        (
            DataFiles.SLIM_TUBE, DataFiles.SLIM_TUBE_DATA, DataTypes.SLIM_TUBE,
            DataTemplates.ID_SLIM_TUBE, ["SlimTubeTestID"],
        ),
        (DataFiles.STOA, DataFiles.STOA_DATA, DataTypes.STOA, DataTemplates.ID_STOA, ["StockTankOilAnalysisTestID"]),
        (DataFiles.ST, DataFiles.ST_DATA, DataTypes.ST, DataTemplates.ID_ST, ["SwellingTestID"]),
        (DataFiles.TT, DataFiles.TT_DATA, DataTypes.TT, DataTemplates.ID_TT, ["TransportTestID"]),
        (DataFiles.VLE, DataFiles.VLE_DATA, DataTypes.VLE, DataTemplates.ID_VLE, ["VaporLiquidEquilibriumTestID"]),
        (DataFiles.WA, DataFiles.WA_DATA, DataTypes.WA, DataTemplates.ID_WA, ["WaterAnalysisTestID"]),
        (
            DataFiles.CAP_PRESSURE, DataFiles.CAP_PRESSURE_DATA, DataTypes.CAP_PRESSURE,
            DataTemplates.ID_SAMPLE_ANALYSIS, ["SamplesAnalysisID", "SampleID"],
        ),
        (
            DataFiles.EXTRACTION, DataFiles.EXTRACTION_DATA, DataTypes.EXTRACTION,
            DataTemplates.ID_SAMPLE_ANALYSIS, ["SamplesAnalysisID", "SampleID"],
        ),
        (
            DataFiles.FRACTIONATION, DataFiles.FRACTIONATION_DATA, DataTypes.FRACTIONATION,
            DataTemplates.ID_SAMPLE_ANALYSIS, ["SamplesAnalysisID", "SampleID"],
        ),
        (
            DataFiles.PHYS_CHEM, DataFiles.PHYS_CHEM_DATA, DataTypes.PHYS_CHEM,
            DataTemplates.ID_SAMPLE_ANALYSIS, ["SamplesAnalysisID", "SampleID"],
        ),
        (
            DataFiles.RP, DataFiles.RP_DATA, DataTypes.RP,
            DataTemplates.ID_SAMPLE_ANALYSIS, ["SamplesAnalysisID", "SampleID"],
        ),
    ],
)
@pytest.mark.smoke
def test_post_measurements_mandatory_columns_missing(api, tests_data, create_record, data_file_name, measurements_file, api_path, id_template, mandatory_fields):
    record_data, created_record = create_record(api_path, data_file_name, id_template)

    tests_data = tests_data(measurements_file)
    test_data = copy.deepcopy(tests_data)

    # Find the indices of the columns to be removed from test_data.
    indices = [test_data["columns"].index(key) for key in mandatory_fields]

    # Remove the columns and their corresponding data from test_data.
    for column_index in sorted(indices, reverse=True):
        del test_data["columns"][column_index]
        for data_index in range(len(test_data["index"])):
            del test_data["data"][data_index][column_index]

    error = getattr(api, api_path).post_measurements(
        record_data["id"],
        test_data,
        allowed_codes=[status.HTTP_422_UNPROCESSABLE_ENTITY],
    )

    assert error["reason"] == "Data validation failed."
    assert error["errors"] == {
        "Mandatory parameters missing": mandatory_fields,
    }


@pytest.mark.skip(reason="issues/66")
@pytest.mark.parametrize(
    "data_file_name, measurements_file, api_path, id_template, expected_error", [
        (
            DataFiles.RSA, DataFiles.RCA_MANDATORY_ATTRIBUTES_PARQUET, DataTypes.RSA, DataTemplates.ID_RSA,
            RCA_MANDATORY_PARAMETERS,
        ),
    ],
)
@pytest.mark.smoke
def test_post_measurements_mandatory_columns_missing_parquet(
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
