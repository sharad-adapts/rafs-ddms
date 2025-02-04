import copy
import random

import pytest
from starlette import status

from tests.integration.config import (
    ACCEPT_HEADERS,
    CONFIG,
    SCHEMA_VERSION,
    DataFiles,
    DataTemplates,
    DataTypes,
    SamplesAnalysisTypes,
)


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
    samples_analysis_id = DataTemplates.ID_SAMPLE_ANALYSIS.format(partition=CONFIG["DATA_PARTITION"])
    record_data, created_record = create_record(
        DataTypes.SAMPLE_ANALYSIS,
        DataFiles.SAMPLE_ANALYSIS,
        samples_analysis_id,
        analysis_type,
    )

    tests_data = tests_data(measurements_file, analysis_type)
    test_data = copy.deepcopy(tests_data)
    test_data["data"][0][0] = f'{record_data["id"]}:'

    full_dataset_id = api.sample_analysis.post_measurements(record_data["id"], test_data, analysis_type)["ddms_urn"]
    content_id = helper.get_content_id_from_ddms_urn(full_dataset_id)

    measurements = api.sample_analysis.get_measurements(record_data["id"], content_id, analysis_type)

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
    dataset_generic_id = DataTemplates.ID_DATASET.format(partition=CONFIG["DATA_PARTITION"])
    dataset_id = f"{dataset_generic_id}{analysis_type}{helper.generate_random_record_id()}"
    samples_analysis_id = DataTemplates.ID_SAMPLE_ANALYSIS.format(partition=CONFIG["DATA_PARTITION"])
    error = api.sample_analysis.get_measurements(
        f"{samples_analysis_id}{helper.generate_random_record_id()}",
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
    dataset_generic_id = DataTemplates.ID_DATASET.format(partition=CONFIG["DATA_PARTITION"])
    dataset_id = f"{dataset_generic_id}{analysis_type}{helper.generate_random_record_id()}"
    samples_analysis_id = DataTemplates.ID_SAMPLE_ANALYSIS.format(partition=CONFIG["DATA_PARTITION"])
    error = api.sample_analysis.get_measurements(
        f"{samples_analysis_id}{helper.generate_random_record_id()}",
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
def test_get_measurements_non_existent_record_id(api, helper, analysis_type):
    samples_analysis_id = DataTemplates.ID_SAMPLE_ANALYSIS.format(partition=CONFIG["DATA_PARTITION"])
    full_id = f"{samples_analysis_id}{helper.generate_random_record_id()}"
    dataset_generic_id = DataTemplates.ID_DATASET.format(partition=CONFIG["DATA_PARTITION"])
    dataset_id = f"{dataset_generic_id}{analysis_type}{helper.generate_random_record_id()}"
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
    samples_analysis_id = DataTemplates.ID_SAMPLE_ANALYSIS.format(partition=CONFIG["DATA_PARTITION"])
    record_data, created_record = create_record(
        DataTypes.SAMPLE_ANALYSIS,
        DataFiles.SAMPLE_ANALYSIS,
        samples_analysis_id,
        analysis_type,
    )

    dataset_generic_id = DataTemplates.ID_DATASET.format(partition=CONFIG["DATA_PARTITION"])
    dataset_id = f"{dataset_generic_id}{analysis_type}{helper.generate_random_record_id()}"
    error = api.sample_analysis.get_measurements(
        record_data["id"],
        dataset_id,
        analysis_type,
        allowed_codes=[status.HTTP_404_NOT_FOUND],
    )
    assert dataset_id in error["message"]
