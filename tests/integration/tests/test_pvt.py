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

from tests.integration.config import DataFiles, DataTypes


@pytest.mark.parametrize(
    "case, test, record_id", [
        ("Deleted", "ConstantVolumeDepletionTestID", "deleted_test_for_automation"),
        ("Not_existent", "ConstantVolumeDepletionTestID", "not_existent"),
    ],
)
@pytest.mark.smoke
def test_pvt_test_not_found(api, tests_data, case, test, record_id):
    test_data = tests_data(DataFiles.PVT)
    record = copy.deepcopy(test_data)
    record["data"]["PVTTests"][test] = [
        f"opendes:work-product-component--ConstantVolumeDepletionTest:{record_id}:",
    ]

    error = getattr(api, DataTypes.PVT).post_record([record], allowed_codes=[status.HTTP_422_UNPROCESSABLE_ENTITY])
    assert "Records not found" in error["reason"]
