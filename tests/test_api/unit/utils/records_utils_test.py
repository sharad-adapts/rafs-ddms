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

from app.api.routes.utils.records import (
    find_dataset_id,
    get_id_version,
    update_dataset_id,
)
from app.exceptions.exceptions import UnprocessableContentException
from tests.test_api.unit.utils.common import (
    EXPECTED_RECORD_ID,
    INVALID_URN,
    ORIGINAL_DDMS_DATASETS,
    TEST_DATASET_RECORD_ID,
    TEST_DATASET_RECORD_ID_2,
    TEST_DDMS_DATASET_URN,
    TEST_DDMS_DATASET_URN_2,
    TEST_ENTITY_TYPE,
    TEST_ENTITY_TYPE_2,
)


def test_get_id_version_with_full_id_():
    record_id, version = get_id_version("partition:entity_type:record_id:1234")

    assert record_id == EXPECTED_RECORD_ID
    assert version == 1234


def test_get_id_version_with_full_id_raises():
    with pytest.raises(UnprocessableContentException) as exc:
        get_id_version("partition:entity_type:record_id:1234s")

    assert exc.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert exc.value.detail == "Record id version '1234s' should be numeric"


def test_get_id_version_ending_with_colon():
    record_id, version = get_id_version("partition:entity_type:record_id:")

    assert record_id == EXPECTED_RECORD_ID
    assert version == None


def test_get_id_version_ending_without_colon():
    record_id, version = get_id_version("partition:entity_type:record_id")

    assert record_id == EXPECTED_RECORD_ID
    assert version == None


@pytest.mark.asyncio
async def test_update_empty_ddms_dataset():
    ddms_datasets = update_dataset_id([], "", "")
    assert not ddms_datasets


@pytest.mark.asyncio
async def test_update_same_ddms_dataset():
    ddms_datasets = update_dataset_id(ORIGINAL_DDMS_DATASETS, TEST_DDMS_DATASET_URN, TEST_ENTITY_TYPE)
    assert ORIGINAL_DDMS_DATASETS == ddms_datasets


@pytest.mark.asyncio
async def test_update_different_entity_ddms_dataset():
    original_ddms_datasets = [*ORIGINAL_DDMS_DATASETS, TEST_DDMS_DATASET_URN_2]

    ddms_datasets = update_dataset_id(original_ddms_datasets, TEST_DDMS_DATASET_URN_2, TEST_ENTITY_TYPE_2)
    assert TEST_DDMS_DATASET_URN in ddms_datasets
    assert TEST_DDMS_DATASET_URN_2 in ddms_datasets

    ddms_datasets = update_dataset_id(original_ddms_datasets, TEST_DDMS_DATASET_URN, TEST_ENTITY_TYPE)
    assert TEST_DDMS_DATASET_URN in ddms_datasets
    assert TEST_DDMS_DATASET_URN_2 in ddms_datasets


@pytest.mark.asyncio
async def test_find_dataset_id_from_urn():
    dataset_id_from_record_id, _ = get_id_version(TEST_DATASET_RECORD_ID)
    dataset_id = find_dataset_id(ORIGINAL_DDMS_DATASETS, TEST_ENTITY_TYPE)
    assert dataset_id == dataset_id_from_record_id


@pytest.mark.asyncio
async def test_find_dataset_id_from_several_urns():
    dataset_id_from_record_id, _ = get_id_version(TEST_DATASET_RECORD_ID_2)
    dataset_id = find_dataset_id(
        [TEST_DDMS_DATASET_URN, TEST_DDMS_DATASET_URN_2],
        TEST_ENTITY_TYPE_2,
    )
    assert dataset_id == dataset_id_from_record_id


@pytest.mark.asyncio
async def test_find_dataset_id_non_existent_entity():
    dataset_id = find_dataset_id(
        ORIGINAL_DDMS_DATASETS,
        TEST_ENTITY_TYPE_2,
    )
    assert dataset_id is None


@pytest.mark.asyncio
async def test_find_dataset_id_invalid_urn():
    dataset_id = find_dataset_id(
        [INVALID_URN],
        TEST_ENTITY_TYPE,
    )
    assert dataset_id is None
