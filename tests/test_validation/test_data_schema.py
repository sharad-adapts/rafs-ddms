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

import io

import pandas as pd
import pytest

from app.bulk_data_validation.data_validation import DataValidator
from tests.test_api.api_version import API_VERSION_V2
from tests.test_api.test_routes.data.data_mock_objects import StorageService
from tests.test_validation.test_data import (
    CORRECT_TEST_BULK_DATA,
    INCORRECT_TEST_BULK_DATA,
    TEST_SCHEMA,
)


@pytest.mark.asyncio
async def test_data_validator_success():
    mock_storage_service = StorageService(record_data=None)
    data_validator = DataValidator(TEST_SCHEMA, mock_storage_service, API_VERSION_V2)
    test_df = pd.read_json(io.StringIO(CORRECT_TEST_BULK_DATA), orient="split")

    errors = await data_validator.validate(test_df)
    assert not errors


@pytest.mark.asyncio
async def test_data_validator_fail():
    mock_storage_service = StorageService(record_data=None)
    data_validator = DataValidator(TEST_SCHEMA, mock_storage_service, API_VERSION_V2)
    test_df = pd.read_json(io.StringIO(INCORRECT_TEST_BULK_DATA), orient="split")

    errors = await data_validator.validate(test_df)
    assert isinstance(errors, dict)
    assert errors == {"invalid_type": [{"SampleDepth": "object"}]}
