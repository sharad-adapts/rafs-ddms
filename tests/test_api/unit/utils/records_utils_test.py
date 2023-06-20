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

from app.api.routes.utils.records import get_id_version
from app.exceptions.exceptions import UnprocessableContentException

EXPECTED_RECORD_ID = "partition:entity_type:record_id"


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
