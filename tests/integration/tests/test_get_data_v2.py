import copy
import random

import pytest
from starlette import status

from app.api.routes.utils.records import generate_dataset_urn
from tests.integration.config import (
    ACCEPT_HEADERS,
    SCHEMA_VERSION,
    DataFiles,
    DatasetPrefix,
    DataTemplates,
    DataTypes,
    SamplesAnalysisTypes,
)
from tests.test_api.api_version import API_VERSION


@pytest.mark.parametrize(
    "measurements_file, analysis_type", [
        (DataFiles.NMR_DATA, SamplesAnalysisTypes.NMR),
    ],
)
@pytest.mark.smoke
@pytest.mark.v2
def test_get_measurements_as_json(
    api, helper, tests_data, create_record, measurements_file, analysis_type,
):
    record_data, created_record = create_record(
        DataTypes.SAMPLE_ANALYSIS,
        DataFiles.SAMPLE_ANALYSIS,
        DataTemplates.ID_SAMPLE_ANALYSIS,
        analysis_type,
    )

    tests_data = tests_data(measurements_file, analysis_type)
    test_data = copy.deepcopy(tests_data)
    test_data["data"][0][0] = f'{record_data["id"]}:'

    full_dataset_id = api.sample_analysis.post_measurements(record_data["id"], test_data, analysis_type)["ddms_urn"]
    dataset_id = helper.get_dataset_id_from_ddms_urn(full_dataset_id)

    measurements = api.sample_analysis.get_measurements(record_data["id"], dataset_id, analysis_type)

    assert isinstance(measurements, dict)

    assert "columns" in measurements and measurements["columns"]
    assert "index" in measurements and measurements["index"]
    assert "data" in measurements and measurements["data"]


@pytest.mark.parametrize(
    "analysis_type", [SamplesAnalysisTypes.NMR],
)
@pytest.mark.smoke
@pytest.mark.v2
def test_get_measurements_with_empty_dataset_version(api, helper, analysis_type):
    dataset_id = f"{DataTemplates.ID_DATASET}{analysis_type}{helper.generate_random_record_id()}"
    error = api.sample_analysis.get_measurements(
        f"{DataTemplates.ID_SAMPLE_ANALYSIS}{helper.generate_random_record_id()}",
        dataset_id,
        analysis_type,
        schema_version_header=None,
        allowed_codes=[status.HTTP_400_BAD_REQUEST],
    )

    assert "No schema version specified or invalid schema format. " \
           "Check if the schema version is specified in the 'Accept' header. " \
           f"Example: --header 'Accept: */*;version={SCHEMA_VERSION}" in error["reason"]


@pytest.mark.parametrize(
    "analysis_type", [SamplesAnalysisTypes.NMR],
)
@pytest.mark.smoke
@pytest.mark.v2
def test_get_measurements_with_wrong_dataset_version(
        api, helper, analysis_type,
):
    version = random.choice(["0.0.0", "1.11.0", "11.111.000.", "100000000.1000000.100000000"])
    dataset_id = f"{DataTemplates.ID_DATASET}{analysis_type}{helper.generate_random_record_id()}"
    error = api.sample_analysis.get_measurements(
        f"{DataTemplates.ID_SAMPLE_ANALYSIS}{helper.generate_random_record_id()}",
        dataset_id,
        analysis_type,
        schema_version_header=ACCEPT_HEADERS.format(version=version),
        allowed_codes=[status.HTTP_400_BAD_REQUEST],
    )

    assert "There is no model for given version. " \
           f"Schema version {version.rstrip('.')} is not one of proper versions: {{'{SCHEMA_VERSION}'}}" in error[
               "reason"
           ]


@pytest.mark.parametrize(
    "analysis_type", [SamplesAnalysisTypes.NMR],
)
@pytest.mark.smoke
@pytest.mark.v2
def test_get_measurements_invalid_dataset_version(
        api, helper, tests_data, analysis_type, delete_record,
):
    tests_data = tests_data(DataFiles.SAMPLE_ANALYSIS, analysis_type)
    test_data = copy.deepcopy(tests_data)
    dataset_id = f"{DataTemplates.ID_DATASET}{analysis_type}{helper.generate_random_record_id()}"
    version = "1.7.0"

    ddms_urn = generate_dataset_urn(
        ddms_id="rafs",
        api_version=API_VERSION,
        entity_type=f"{analysis_type.replace('-', '')}data",
        wpc_id=test_data["id"],
        dataset_id=dataset_id,
        content_schema_version=version,
    )
    test_data["data"]["DDMSDatasets"] = test_data.get("DDMSDatasets", [ddms_urn])

    api.sample_analysis.post_record([test_data])

    delete_record["record_id"].append(test_data["id"])
    delete_record["api_path"] = DataTypes.SAMPLE_ANALYSIS

    error = api.sample_analysis.get_measurements(
        test_data["id"],
        dataset_id,
        analysis_type,
        schema_version_header=ACCEPT_HEADERS.format(version=SCHEMA_VERSION),
        allowed_codes=[status.HTTP_400_BAD_REQUEST],
    )

    assert "Invalid schema version has been provided. " \
           f"Schema version {SCHEMA_VERSION} is not one of proper versions: {{'{version}'}}" == error["reason"]


@pytest.mark.parametrize(
    "analysis_type", [SamplesAnalysisTypes.NMR],
)
@pytest.mark.smoke
@pytest.mark.v2
def test_get_measurements_non_existent_record_id(api, helper, analysis_type):
    full_id = f"{DataTemplates.ID_SAMPLE_ANALYSIS}{helper.generate_random_record_id()}"
    dataset_id = f"{DataTemplates.ID_DATASET}{analysis_type}{helper.generate_random_record_id()}"
    error = api.sample_analysis.get_measurements(
        full_id,
        dataset_id,
        analysis_type,
        allowed_codes=[status.HTTP_404_NOT_FOUND],
    )
    assert full_id in error["message"]


@pytest.mark.parametrize(
    "analysis_type", [SamplesAnalysisTypes.NMR],
)
@pytest.mark.smoke
@pytest.mark.v2
def test_get_measurements_non_existent_dataset_id(
    api, helper, create_record, analysis_type,
):
    record_data, created_record = create_record(
        DataTypes.SAMPLE_ANALYSIS,
        DataFiles.SAMPLE_ANALYSIS,
        DataTemplates.ID_SAMPLE_ANALYSIS,
        analysis_type,
    )

    dataset_id = f"{DataTemplates.ID_DATASET}{analysis_type}{helper.generate_random_record_id()}"
    error = api.sample_analysis.get_measurements(
        record_data["id"],
        dataset_id,
        analysis_type,
        allowed_codes=[status.HTTP_404_NOT_FOUND],
    )
    assert dataset_id in error["message"]
