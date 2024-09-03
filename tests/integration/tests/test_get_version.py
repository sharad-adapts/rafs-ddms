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
import time

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
def test_get_version_v2_sample_analysis(api, helper, create_record):
    api_path = DataTypes.SAMPLE_ANALYSIS

    record_data, created_record = create_record(
        api_path,
        DataFiles.SAMPLE_ANALYSIS,
        DataTemplates.ID_SAMPLE_ANALYSIS.format(partition=CONFIG["DATA_PARTITION"]),
        "BasicRockProperties",
    )
    version = helper.parse_full_record_id(created_record["recordIdVersions"][0])["version"]
    test_data = getattr(api, api_path).get_record_version(
        record_data["id"], version,
    )

    assert test_data["id"] == record_data["id"]
    assert test_data["version"] == version


@pytest.mark.smoke
@pytest.mark.v2
def test_get_non_existent_version_v2_sample_analysis(api, create_record):
    api_path = DataTypes.SAMPLE_ANALYSIS

    record_data, _ = create_record(
        api_path, DataFiles.SAMPLE_ANALYSIS,
        DataTemplates.ID_SAMPLE_ANALYSIS.format(partition=CONFIG["DATA_PARTITION"]),
        "BasicRockProperties",
    )
    int(time.time())
    error = getattr(api, api_path).get_record_version(
        record_data["id"],
        version=int(time.time()),
        allowed_codes=[status.HTTP_404_NOT_FOUND],
    )
    assert f"can't be found for record {record_data['id']}" in error["message"]


@pytest.mark.smoke
@pytest.mark.v2
def test_get_version_of_non_existent_record_v2_sample_analysis(api, helper, create_record):
    api_path = DataTypes.SAMPLE_ANALYSIS
    id_template = DataTemplates.ID_SAMPLE_ANALYSIS.format(partition=CONFIG["DATA_PARTITION"])

    non_existent_id = f"{id_template}{helper.generate_random_record_id()}"
    error = getattr(api, api_path).get_record_version(
        non_existent_id,
        version=int(time.time()),
        allowed_codes=[status.HTTP_404_NOT_FOUND],
    )
    assert f"The record '{non_existent_id}' was not found" in error["message"]
