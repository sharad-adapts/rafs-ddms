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
def test_delete_v2_sample_analysis(api, create_record):
    data_file_name = DataFiles.SAMPLE_ANALYSIS
    api_path = DataTypes.SAMPLE_ANALYSIS
    id_template = DataTemplates.ID_SAMPLE_ANALYSIS.format(partition=CONFIG["DATA_PARTITION"])

    record_data, _ = create_record(api_path, data_file_name, id_template, "BasicRockProperties")
    # status code check is implemented on the API client layer
    getattr(api, api_path).soft_delete_record(record_data["id"], allowed_codes=[status.HTTP_204_NO_CONTENT])
    getattr(api, api_path).get_record(record_data["id"], allowed_codes=[status.HTTP_404_NOT_FOUND])


@pytest.mark.smoke
@pytest.mark.v2
def test_delete_v2_sample_analysis_non_existent_record(api, helper, create_record):
    api_path = DataTypes.SAMPLE_ANALYSIS
    id_template = DataTemplates.ID_SAMPLE_ANALYSIS.format(partition=CONFIG["DATA_PARTITION"])

    # status code check is implemented on the API client layer
    getattr(api, api_path).soft_delete_record(
        f"{id_template}{helper.generate_random_record_id()}",
        allowed_codes=[status.HTTP_404_NOT_FOUND],
    )
