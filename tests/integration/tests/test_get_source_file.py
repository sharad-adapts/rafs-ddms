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

from app.resources.common_headers import CONTENT_TYPE
from app.resources.mime_types import SupportedMimeTypes
from tests.integration.config import (
    UPLOADED_FILES,
    DataFiles,
    DataTemplates,
    DataTypes,
)


@pytest.mark.parametrize(
    "data_file_name, api_path, id_template", [
        (DataFiles.RSA, DataTypes.RSA, DataTemplates.ID_RSA),
        (DataFiles.PVT, DataTypes.PVT, DataTemplates.ID_PVT),
    ],
)
@pytest.mark.smoke
def test_get_source_zip_file(api, create_record, data_file_name, api_path, id_template):
    record_data, _ = create_record(api_path, data_file_name, id_template, UPLOADED_FILES)

    response = getattr(api, api_path).get_source_file(record_data["id"])
    assert response.headers[CONTENT_TYPE] == SupportedMimeTypes.ZIP.mime_type
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

    response = getattr(api, api_path).get_source_file(record_data["id"])
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

    response = getattr(api, api_path).get_source_file(record_data["id"], allowed_codes=[status.HTTP_404_NOT_FOUND])
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
    response = getattr(api, api_path).get_source_file(record_data["id"], allowed_codes=[status.HTTP_404_NOT_FOUND])
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
    response = getattr(api, api_path).get_source_file(full_id, allowed_codes=[status.HTTP_422_UNPROCESSABLE_ENTITY])
    assert f"{data_type} ID is not provided in expected OSDU pattern" in response.text


@pytest.mark.parametrize(
    "api_path, id_template", [
        (DataTypes.RSA, DataTemplates.ID_RSA),
        (DataTypes.PVT, DataTemplates.ID_PVT),
    ],
)
def test_get_source_with_non_existent_id(api, helper, api_path, id_template):
    full_id = f"{id_template}{helper.generate_random_record_id()}"
    error = getattr(api, api_path).get_source_file(
        full_id,
        allowed_codes=[status.HTTP_404_NOT_FOUND],
    )

    assert f"'{full_id}' was not found" in error.text
